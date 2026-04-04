from ast import Tuple
import json
import os
from pathlib import Path
import pandas as pd

import pip._vendor.requests as requests
from pip._vendor.requests.exceptions import HTTPError

'''
Создание сегмента из CSV-файла: https://api-audience.yandex.ru/v1/management/segments/upload_csv_file
Список доступных сегментов: https://api-audience.yandex.ru/v1/management/segments
Изменение данных сегмента, созданного из файла: https://api-audience.yandex.ru/v1/management/segment/{segmentId}/modify_data
Сохранение сегмента, созданного из файла: https://api-audience.yandex.ru/v1/management/segment/{segmentId}/confirm
{'segment': {'id': 33099428, 'type': 'uploading', 'status': 'uploaded', 'has_guests': False, 'guest_quantity': 0, 'can_create_dependent': False, 'has_derivatives': False, 'hashed': False, 'item_quantity': 149, 'guest': False}}
'''
current_file = os.path.dirname(__file__)
token = 'y0_AgAAAAAp-myZAAtIHwAAAAD627JkAACLIZRegV9Ej5bEtjS0nlANMmFpEw'
url = 'https://api-audience.yandex.ru'


def pretty_print_POST(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in
    this function because it is programmed to be pretty
    printed and may differ from the actual request.
    """
    print('{}\n{}\r\n{}\r\n\r\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))


'''
Возвращает список существующих сегментов, доступных пользователю.
'''


def get_segments():
    response = requests.get(
        url=f'{url}/v1/management/segments',
        headers={'Authorization': 'OAuth {}'.format(token)}
    )
    req = requests.Request('GET', f'{url}/v1/management/segments', headers={'Authorization': 'OAuth {}'.format(token)})
    prepared = req.prepare()
    pretty_print_POST(prepared)
    print(response.text)
    return json.loads(response.text)['segments']


'''
Возвращает информацию по сегменту
'''


def get_segment_info(segment_id) -> str:
    segments = get_segments()
    for segment in segments:
        if segment_id == segment['id']:
            return segment


'''
Возвращает segment_id по имени сегмента
'''


def get_segment_id_by_name(segment_name):
    segments = get_segments()
    for segment in segments:
        if segment_name == segment['name']:
            return segment['id']


'''
Создает сегмент из файла с данными. В файле должно быть не менее 100 записей.
'''


def create_segment(file):
    file = Path(file)
    try:
        response = requests.post(
            url=f'{url}/v1/management/segments/upload_csv_file',
            headers={'Authorization': 'OAuth {}'.format(token),
                     'Content-Disposition': f'filename={{{file.name}}}'
                     },
            files={'file': open(file, 'r').read()},
            verify=False
        )
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        json_response = response.json()
        print(json_response)
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        # json_response = response.json()
        # segment_id = int(json_response['segment']['id'])
        segment_id = json.loads(response.text)['segment']['id']
        segment_status = json.loads(response.text)['segment']['status']
        print(f'Segment uploaded: {segment_id}')
        print(response.text)
    return segment_id, segment_status


'''
Сохраняет сегмент, созданный из файла с данными.
    segment_id: идентификатор сегмента, который вы хотите сохранить
    name: название сегмента
    hashed: является ли захешированной каждая строка загруженного файла.
            Возможные значения (по умолчанию 1):
                0 — строка не захеширована;
                1 — строка захеширована.
    content_type: вид содержимого файла.
            Возможные значения (по умолчанию 'crm'):
                idfa_gaid — идентификаторы устройств;
                mac — MAC-адреса;
                crm — CRM-данные.Ы   
'''


def save_segment(segment_id, name, hashed=1, content_type='crm'):
    data = {
        'segment': {
            'id': segment_id,
            'name': name,
            'hashed': hashed,
            'content_type': content_type,
            'hashing_alg': 'SHA256'
        }
    }
    try:
        response = requests.post(
            url=f'{url}/v1/management/segment/{segment_id}/confirm',
            headers={'Authorization': 'OAuth {}'.format(token)},
            data=json.dumps(data),
            verify=False
        )
        req = requests.Request('POST', f'{url}/v1/management/segment/{segment_id}/confirm',
                               headers={'Authorization': 'OAuth {}'.format(token)}, data=json.dumps(data))
        prepared = req.prepare()
        pretty_print_POST(prepared)
        print(f'response headers: {response.headers}')
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        json_response = response.json()
        print(json_response)
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        json_response = response.json()
        print(f'response_json: {json_response}')
        # print (f'Segment confirmed: {segment_id}')
    return


'''
Изменяет данные указанного сегмента. 
При обновлении сегментов нужно использовать структуру файла, которая была при первичной загрузке сегмента.
    modification_type - Тип изменения данных: добавление или удаление данных, перезаписывание файла целиком. 
    При добавлении данные должны совпадать с исходным форматом (захешированная или незахешированая информация).
    Допустимые значения (по умолчанию 'addition'):
        subtraction — удаление данных из файла.
        addition — добавление данных в файл.
        replace — перезаписывание файла целиком.
'''


def edit_segment(segment_id, file, modification_type='addition'):
    file = Path(file)
    try:
        response = requests.post(
            url=f'{url}/v1/management/segment/{segment_id}/modify_data?modification_type={modification_type}',
            headers={'Authorization': 'OAuth {}'.format(token),
                     'Content-Disposition': f'filename={{{file.name}}}'
                     },
            files={'file': open(file, 'r').read()},
            verify=False
        )
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        json_response = response.json()
        print(json_response)
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        json_response = response.json()
        print(f'Segment edited: {segment_id}')
    return


'''
Удаляет указанный сегмент.
'''


def delete_segment(segment_id):
    try:
        response = requests.delete(
            url=f'{url}/v1/management/segment/{segment_id}',
            headers={'Authorization': 'OAuth {}'.format(token)})
        response.raise_for_status()
        req = requests.Request('DELETE', f'{url}/v1/management/segment/{segment_id}',
                               headers={'Authorization': 'OAuth {}'.format(token)})
        prepared = req.prepare()
        pretty_print_POST(prepared)
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        json_response = response.json()
        print(json_response)
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        json_response = response.json()
        is_success = int(json_response['success'])
        print(f'Segment deleted: {is_success}')


def get_grants(segment_id):
    try:
        response = requests.get(
            url=f'{url}/v1/management/segment/{segment_id}/grants',
            headers={'Authorization': 'OAuth {}'.format(token)})
        response.raise_for_status()
        req = requests.Request('GET', f'{url}/v1/management/segment/{segment_id}/grants',
                               headers={'Authorization': 'OAuth {}'.format(token)})
        prepared = req.prepare()
        pretty_print_POST(prepared)
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        json_response = response.json()
        print(json_response)
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        json_response = response.json()
        print(f'Segment {segment_id} grants: {json_response}')


def create_grant(segment_id, user_login, comment=''):
    data = {
        'grant': {
            'user_login': user_login,
            'comment': comment
        }
    }
    try:
        response = requests.put(
            url=f'{url}/v1/management/segment/{segment_id}/grant',
            headers={'Authorization': 'OAuth {}'.format(token)},
            data=json.dumps(data)
        )
        response.raise_for_status()
        req = requests.Request('PUT', f'{url}/v1/management/segment/{segment_id}/grant',
                               headers={'Authorization': 'OAuth {}'.format(token)}, data=json.dumps(data))
        prepared = req.prepare()
        pretty_print_POST(prepared)
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        json_response = response.json()
        print(json_response)
    except Exception as err:
        print(f'Other error occurred: {err}')


def delete_grant(segment_id, user_login):
    try:
        response = requests.delete(
            url=f'{url}/v1/management/segment/{segment_id}/grant?user_login={user_login}',
            headers={'Authorization': 'OAuth {}'.format(token)}
        )
        response.raise_for_status()
        req = requests.Request('DELETE', f'{url}/v1/management/segment/{segment_id}/grant?user_login={user_login}',
                               headers={'Authorization': 'OAuth {}'.format(token)})
        prepared = req.prepare()
        pretty_print_POST(prepared)
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        json_response = response.json()
        print(json_response)
    except Exception as err:
        print(f'Other error occurred: {err}')


def main():
    # segments = get_segments()
    # print(segments)

    # print(f'segment_id: {segment_id}, segment_status: {segment_status}')
    # save_segment(33359281, '5555')
    # edit_segment(33169887, csv_file_2)
    # get_segments()
    # delete_segment(33099982)
    # get_segments()
    # segment = get_segment_info(33169887)
    # print(f'id: {segment["id"]}, segment_status: {segment["status"]}, create_time: {segment["create_time"]}')

    csv_file_1 = current_file + '\data\manual_sha256.csv'
    csv_file_2 = current_file + '\data\manual_md5.csv'
    # segment_id = get_segment_id_by_name('1111')
    # if segment_id is None:
    #    print('Сегмент с указанным именем не найден!')
    # else:
    #    print(segment_id)
    # segment_id, segment_status = create_segment(csv_file_1)
    # save_segment(segment_id, 'manual_ВНС_dadm consent all')
    edit_segment(segment_id=41720113, file=csv_file_1, modification_type='addition')
    # get_segments()
    # get_grants(33548458)
    # create_grant(33548458, 'gazprombank-creditcard', comment = '')
    # get_grants(33548458)
    # delete_grant(33548458, 'gazprombank-creditcard')
    # get_grants(33781628)

    # segment_id, segment_status = create_segment(csv_file_2)
    # save_segment(segment_id, 'test_md5')
    # get_segments()
    # get_grants(34399845)
    # create_grant(34399845, 'gazprombank-creditcard', comment='')


main()


