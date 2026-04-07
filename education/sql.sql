/*
1. Есть таблица формата:

create table orders (
  driver_id varchar,
  city      varchar,
  order_id  varchar
  -- еще какие-то поля
);

Нужно получить топ 10 водителей по кол-ву заказов в каждом городе.
*/
with driver_total_orders as (
  select
    driver_id,
    city,
    count(distinct order_id) as total_orders
  from orders
  group by 1,2
),
driver_rating as (
  select
    driver_id,
    city,
    total_orders,
    dense_rank() over(partition by city order by total_orders desc) as rating
  from driver_total_orders
)
select
  driver_id,
  city,
  total_orders,
  rating
from driver_rating
where rating <= 10

/*
2. Имеем таблицу:

 id | time  | value
----+-------+-------
  1 | 07:30 | <NULL>
  1 | 09:21 |    10
  1 | 13:53 | <NULL>
  1 | 16:12 | <NULL>
  2 | 09:42 |   133
  2 | 15:20 | <NULL>
  2 | 21:33 | <NULL>
  3 | 08:01 | <NULL>
  3 | 11:41 |     8
  3 | 14:23 | <NULL>
  3 | 16:17 | <NULL>
  3 | 19:54 |     2
  4 | 13:10 |   312
  4 | 14:42 | <NULL>
  4 | 16:31 |     7
  4 | 17:44 | <NULL>

Необходимо заполнить NULLы предыдущим значением (не NULL) - протяжка вниз, т.е. получить таблицу:

 id | time  | value
----+-------+-------
  1 | 07:30 | <NULL>
  1 | 09:21 |    10
  1 | 13:53 |    10
  1 | 16:12 |    10
  2 | 09:42 |   133
  2 | 15:20 |   133
  2 | 21:33 |   133
  3 | 08:01 | <NULL>
  3 | 11:41 |     8
  3 | 14:23 |     8
  3 | 16:17 |     8
  3 | 19:54 |     2
  4 | 13:10 |   312
  4 | 14:42 |   312
  4 | 16:31 |     7
  4 | 17:44 |     7
*/

WITH grouped AS (
    SELECT
        id,
        time,
        value,
        COUNT(value) OVER (PARTITION BY id ORDER BY time) AS grp
    FROM test_data
)
SELECT
    id,
    time,
    FIRST_VALUE(value) OVER (PARTITION BY id, grp ORDER BY time) AS filled_value
FROM grouped
ORDER BY id, time;

with groups as (
  select
    id,
    time,
    value,
    sum(case when value is null then 0 else 1 end) over(partition by id order by time) as grp
  from test_data
)
SELECT
  id,
  time,
  max(value) over(partition by id, grp) as value
from groups


/*
3. Есть лог (таблица) с изменением статуса заказа пользователя:

create table order_user_status
(
    order_id varchar,
    status varchar,
    event_dttm datetime
)

И аналогичная таблица с изменением статусов заказа для водителя:

create table order_driver_status
(
    order_id varchar,
    driver_status varchar,
    event_dttm datetime
)

Необходимо на базе этих 2 объектов получить таблицу вида:

create table order_status_hist
(
    order_id varchar,
    status varchar,
    driver_status varchar,
    start_dttm datetime,
    end_dttm datetime
)

Статусы могут приходить как угодно: надо рассматривать все кейсы
*/

with order_scd2 as (
select
  order_id,
  status,
  event_dttm as start_dttm,
  lead(event_dttm, 1, cast('5999-12-31' as DateTime)) over(partition by order_id order by start_dttm) - interval 1 second as end_dttm
from order_user_status
),
driver_scd2 as (
select
  order_id,
  driver_status,
  event_dttm as start_dttm,
  lead(event_dttm, 1, cast('5999-12-31' as DateTime)) over(partition by order_id order by start_dttm) - interval 1 second as end_dttm
from order_driver_status
),
timeline as (
select
  order_id,
  event_dttm as start_dttm
from order_user_status
union distinct
select
  order_id,
  event_dttm as start_dttm
from order_driver_status
),
interval_orders as (
select
  order_id,
  start_dttm,
  lead(start_dttm, 1, cast('5999-12-31' as DateTime)) over(partition by order_id order by start_dttm) - interval 1 second as end_dttm
from timeline
)
select
  i.order_id,
  ous.status,
  ods.driver_status,
  i.start_dttm,
  i.end_dttm
from interval_orders i
left join order_scd2 ous
on i.order_id = ous.order_id
and i.start_dttm between ous.start_dttm and ous.end_dttm
left join driver_scd2 ods
on i.order_id = ods.order_id
and i.start_dttm between ods.start_dttm and ods.end_dttm

/*
4. Есть таблица с полями passenger_id, ride_id, cost, type(комфорт или эконом), date
Просят вывести тех пассажиров, кто потратил больше 5000, но при этом проехал на комфорте не больше 1 раза
*/

select
  passenger_id
from trips
group by passenger_id
having sum(cost) > 5000 and count(case when type = 'комфорт' then 1 end) < 2

/*
5. Таблица та же
Просят вывести по каждому пассажиру самую большую последовательность в днях.
Например, человек ездил каждый день в течение недели - 7 дней. Потом день не ездил, и снова ездил 4 дня. Правильный результат для такого должен быть 7.
*/

with trips_distinct as (
  select distinct
    passenger_id,
    date
  from trips
),
day_cond as (
  select
    passenger_id,
    date,
    case when lag(date, 1, cast('1900-01-01' as Date)) over(partition by passenger_id order by date) + interval 1 day = date then 0 else 1 end as grp_flg
  from trips_distinct
),
pass_day_grp as (
  select
    passenger_id,
    date,
    sum(grp_flg) over(partition by passenger_id order by date) as grp
  from day_cond
),
pass_day_dur as (
  select
    passenger_id,
    grp,
    count(*) as grp_dur
  from pass_day_grp
  group by passenger_id, grp
)
select
  passenger_id,
  max(grp_dur)
from pass_day_dur
group by passenger_id;

with trips_distinct as (
  select distinct
    passenger_id,
    date
  from trips
)
,trips_rn as (
  select
    passenger_id,
    date,
    row_number() over(partition by passenger_id order by date) as rn
  from trips
)
,trips_grp as (
  select
    passenger_id,
    date - interval rn days as grp
  from trips_rn
)
,trips_agg as (
  select
    passenger_id,
    grp,
    count(*) as strick
  from trips_grp
  group by passenger_id, grp
)
select
  passenger_id,
  max(strick)
from trips_agg
group by passenger_id;

/*
6. Есть 2 таблицы debet и credit с полями agreement, date, amt
Необходимо написать запрос который выведет разницу за каждый день debet - credit
*/

with all_operations as (
  select
    agreement,
    date,
    amt as qty
  from debet
  union all
  select
    agreement,
    date,
    -amt as qty
  from credit
)
select
  agreement,
  date,
  sum(qty) as balance
from all_operations
group by agreement, date
order by agreement, date;

/*
7 . В таблице содержатся записи об операциях по одному счету.
CREATE TABLE #OperPart
(
  OperationID  numeric(15,0)
 ,CharType     int
 ,OperDate     datetime
 ,Qty          numeric(28,10)
 ,Indatetime   datetime
 ,Rest         numeric(28,10)
)
Если CharType = -1 , то операция пополнения счета, если 1 – операция списания со счета
Остаток на начало дня 20.08.2021 по счету 1000868.31
Необходимо для каждой операции в таблице #OperPart заполнить поле Rest актуальным остатком
(под актуальным остатком понимается остаток, который образовался после совершения данной операции)
*/
with rest as (
select
  OperationID,
  10000 + sum(Qty*(-1 * CharType)) over(order by Indatetime) as Rest
from operations
)
update operations op
set op.Rest = rest.Rest
where op.OperationID = rest.OperationID;

/*
У вас есть историческая таблица с изменениями цен на товары:
CREATE TABLE price_history (
    product_id INT,
    price DECIMAL(10,2),
    effective_from TIMESTAMP,
    effective_to TIMESTAMP,
    version_id SERIAL PRIMARY KEY
);
Таблица содержит записи с разными версиями цен на товары. Некоторые записи могут содержать одинаковые цены на последовательные периоды времени.
Необходимо написать SQL-запрос, который:

1. Схлопнет последовательные записи с одинаковыми ценами для каждого товара
2. Вернет таблицу с корректными временными промежутками
3. Сохранит первую дату начала периода и последнюю дату окончания для последовательных одинаковых цен
*/
with change_price as (
select
  product_id,
  price,
  effective_from,
  effective_to,
  CASE
    WHEN lag(price) over (partition by product_id order by effective_from) = price THEN 0
    ELSE 1
  END not_equal_prev_price
from price_history
)
, price_group as (
select
  product_id,
  price,
  effective_from,
  effective_to,
  sum(not_equal_prev_price) over(partition by product_id order by effective_from) as grp
from change_price
)
select
  product_id,
  price,
  min(effective_from) as effective_from,
  max(effective_to) as effective_to
from price_group
group by product_id, price, grp
order by product_id, effective_from;
