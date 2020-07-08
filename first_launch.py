import os
from pathlib import Path
import json

cwd = str(Path(__file__).parents[0])


def base_settings():
    print('Для настройки бота, следуйте инструкциям и указывайте все параметры.')

    owner = int(input('ID владельца сервера: '))
    prefix = input('Префикс, для команд: ')
    token = input('Токен вашего бота, зарегистрированного на сайте "https://discord.com/developers/applications": ')

    with open(os.path.join(cwd, 'config', 'config.json'), 'w') as j:
        config_file = {'owner': owner, 'prefix': prefix, 'token': token}
        j.write(json.dumps(config_file))
        print('Основной файл конфигурации создан.')


def ranking_settings():
    print('Теперь необходимо указать параметры для рангового модуля.')

    role_for_rating = input('Выдавать роли за рейтинг? (да/нет)').lower()
    timeout = int(input('Сколько времени ждать подтверждения дуэли? В секундах: '))
    work_channel = int(input('ID канала, в котором будет работать бот: '))

    print('Теперь необходимо указать все роли, которые вы хотите выдавать за рейтинг.')
    print('Напишите выход, когда закончите или оставьте поле ввода пустым.')

    rating_role = []
    while True:
        need_rating = input('Необходимо рейтинга для получения роли: ')
        if need_rating == 'выход' or need_rating == '':
            break
        role_name = input('Имя роли: ')
        if role_name == 'выход' or need_rating == '':
            break
        role_id = input('ID роли: ')
        if role_id == 'выход' or need_rating == '':
            break
        rating_role.append([int(need_rating), role_name, int(role_id)])
    print('Вы закончили добавление ролей.')

    with open(os.path.join(cwd, 'Extensions', 'config', 'ranking', 'rating.json'), 'w') as j:
        config_file = {'RATING_ROLE': rating_role,
                       'ROLE_FOR_RATING': True if role_for_rating.startswith('д') or role_for_rating.startswith('y') else False,
                       'TIMEOUT': timeout,
                       "WORK_CHANNEL": work_channel}
        j.write(json.dumps(config_file))
        print('Файл конфигурации создан.')


def database_settings():
    print('Создание файла конфигурации для подключения к базе данных. ')
    db_host = input('Host: ')
    db_name = input('DataBase Name: ')
    db_user = input('User: ')
    db_password = input('Password: ')
    with open(os.path.join(cwd, 'Extensions', 'config', 'ranking', 'rating.json'), 'w') as j:
        config_file = {'DB_HOST': db_host,
                       'DB_NAME': db_name,
                       'DB_USER': db_user,
                       "DB_PASSWORD": db_password}
        j.write(json.dumps(config_file))
        print('Файл конфигурации создан.')


if __name__ == '__main__':
    while True:
        print('Меню настройщика:\n1. Основные настройки.\n2. Настройки рангового модуля.')
        menu = input('Выберете пункт меню: ')
        if menu == '1':
            base_settings()
        elif menu == '2':
            ranking_settings()
        elif menu == '3':
            database_settings()
        else:
            continue
