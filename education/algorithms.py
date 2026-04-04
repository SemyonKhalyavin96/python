from typing import List
class Solution:

    # Есть строка из символов X, Y, O
    # Необходимо написать функцию которая выводит минимальное расстояние между X и Y
    # Если в строке вообще нет X или Y вывести 0
    @staticmethod
    def get_min_distance(s: str) -> int:
        result = float('inf')
        last_x_idx = -1
        last_y_idx = -1

        #Идём по строке
        for idx, c in enumerate(s):
            #Если встречается X и есть индекс у Y, считаем расстояние и проверяем на минимум
            if c == 'X':
                if last_y_idx != -1:
                    result = min(result, idx - last_y_idx)
                last_x_idx = idx
            # Если встречается Y и есть индекс у X, считаем расстояние и проверяем на минимум
            if c == 'Y':
                if last_x_idx != -1:
                    result = min(result, idx - last_x_idx)
                last_y_idx = idx

        return 0 if result == float('inf') else result

    #Есть отсортированный массив a[n], числа index и k
    #Необходимо написать функцию, которая выведет в любом порядке массив из k элементов,
    #состоящий из чисел наиболее приближенных к a[index]
    #nums = [1, 2, 3], index = 1, k = 1, result = [2],
    #nums = [1, 2, 3], index = 1, k = 2, result = [1, 2],  2 и 1 (3 дальше, т.к. расстояние 1 и 3>1)
    #nums = [1, 2, 3], index = 1, k = 3, result = [1, 2, 3]
    @staticmethod
    def find_k_closest(nums: List[int], index: int, k: int):
        result = [nums[index]]
        l = index - 1
        r = index + 1

        while len(result) < k:
            if r > len(nums) - 1:
                result.append(nums[l])
                l -= 1
            elif l < 0:
                result.append(nums[r])
                r += 1
            else:
                if nums[index] - nums[l] <= nums[r] - nums[index]:
                    result.append(nums[l])
                    l -= 1
                else:
                    result.append(nums[r])
                    r += 1

        return result

    @staticmethod
    def find_k_closest_binary(nums: List[int], index: int, k: int):
        target = nums[index]
        l = 0
        #Минимальная допустимая левая граница для окна, иначе вылезем за nums
        r = len(nums) - k

        while l < r:
            mid = (l + r) // 2
            #Если расстояние между таргетом и правой границей меньше - сдвигаем левую границу вправо.
            #Иначе сдвигаем правую границу влево
            if target - nums[mid] > nums[mid + k] - target:
                l = mid + 1
            else:
                r = mid

        return nums[l:l+k]

    #Есть ряд в кинотеатре с занятыми и свободными местами:
    #[0, 0, 1, 0, 0, 0, 1, 0]
    #Новый человек садится на максимально удаленное место
    #Найти расстояние до максимально удаленного места
    #[1,0,0,0,1] - должно получиться 2
    def maxDistToClosest(self, seats: List[int]) -> int:
        start = None
        max_dist = 0

        for i in range(len(seats)):
            if seats[i] == 0:
                continue
            #Краевой случай - [0,0,0,0,0,1]
            #Прошли по списку, но так и не нашли единицу до текущего момента - значит, максимальное расстояние,
            #это индекс первой постречавшейся единицы
            if start is None:
                max_dist = i
            #В противном случае опеределяем максимальное расстояние как среднее место между единицами
            #Если они больше максимума, то обновляем его
            else:
                max_dist = max((i - start) // 2, max_dist)
            #Присваиваем start индексу новой единицы
            start = i

        # Краевой случай - [1,0,0,0,0,0]
        # Тогда нужно взять индекс последнего элемента, и вычесть из него start
        return max(max_dist, len(seats) - 1 - start)















