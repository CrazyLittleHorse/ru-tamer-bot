import json
import os
from pathlib import Path

import pymysql

cwd = str(Path(__file__).parents[1])


class Database(object):
    """Класс для подключения и работы с базой данных MySql"""

    def __init__(self):
        with open(os.path.join(cwd, 'config', 'ranking', 'database.json'), 'r') as f:
            self.database_config = json.loads(f.read())
        self.__conn = pymysql.connect(host=os.environ.get('DB_HOST', self.database_config.get('DB_HOST')),
                                      user=os.environ.get('DB_USER', self.database_config.get('DB_USER')),
                                      password=os.environ.get('DB_PASSWORD', self.database_config.get('DB_PASSWORD')),
                                      db=os.environ.get('DB_NAME', self.database_config.get('DB_NAME')))
        self.__cur = self.__conn.cursor()

    def __enter__(self):
        return self

    def __del__(self):
        if self.__conn.open:
            self.__conn.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__cur.close()
        if isinstance(exc_val, Exception):
            print(exc_val)
            self.__conn.rollback()
        else:
            self.__conn.commit()
        self.__conn.close()

    def new_rating(self, user_id: int, user_rating: int, user_wins: int, user_loses: int):
        """Изменяет рейтинг пользователя"""
        __query_update = (f'UPDATE players_rating pr '
                          f'SET pr.current = 0, pr.date_end = CURRENT_TIMESTAMP() '
                          f'WHERE pr.user_id = {user_id} AND pr.current = 1;')
        __query_insert = (f'INSERT INTO players_rating '
                          f'(version, user_id, user_rating, user_wins, user_loses, date_start) '
                          f'VALUES ('
                          f'IFNULL((SELECT MAX(version) + 1 FROM players_rating pr WHERE pr.user_id = {user_id}), 1), '
                          f'{user_id}, '
                          f'{user_rating}, '
                          f'{user_wins}, '
                          f'{user_loses}, '
                          f'CURRENT_TIMESTAMP());')
        __query_arr = [__query_update,
                       __query_insert]
        for __query in __query_arr:
            self.__cur.execute(__query)

    def remove_user(self, user_id: int):
        """Удаляет все записи о пользователе"""

        self.__cur.execute(f'''DELETE FROM players_rating WHERE user_id={user_id}''')

    def get_top(self, limit=5) -> tuple:
        """Возвращает топ по user_rating"""

        self.__cur.execute(f'SELECT '
                           f'players_rating.user_id, '
                           f'players_rating.user_rating '
                           f'FROM players_rating '
                           f'WHERE players_rating.current = 1 '
                           f'ORDER BY players_rating.user_rating DESC LIMIT {limit if limit in range(0, 11) else 5}')

        return tuple(self.__cur.fetchall())

    def get_info(self, user_id: int):
        """Возвращает информацию о пользователе:
        user_id, user_rating, user_wins, user_loses
        либо None"""

        self.__cur.execute(f'SELECT '
                           f'   pr.user_id, '
                           f'   pr.user_rating, '
                           f'   (SELECT '
                           f'       SUM(pr.user_wins) '
                           f'       FROM players_rating pr '
                           f'       WHERE pr.user_id = {user_id}), '
                           f'   (SELECT '
                           f'       SUM(pr.user_loses) '
                           f'       FROM players_rating pr '
                           f'       WHERE pr.user_id = {user_id}) '
                           f'FROM players_rating pr '
                           f'WHERE pr.user_id = {user_id} '
                           f'AND pr.current = 1;')

        try:
            user_info = (tuple(self.__cur.fetchone()))
        except TypeError:
            user_info = None

        return user_info

    def get_champion(self, user_id: int) -> bool:
        """Проверяет, является ли пользователь чемпионом"""

        self.__cur.execute(f'SELECT pr.user_id '
                           f'FROM players_rating pr '
                           f'WHERE pr.current=1 '
                           f'ORDER BY pr.user_rating DESC LIMIT 1')

        return True if user_id in self.__cur.fetchone() else False

    def check_user(self, user_id: int) -> bool:
        """Проверка на наличие пользователя в базе"""

        self.__cur.execute(
            f'''SELECT 1 FROM players_rating pr WHERE pr.user_id={user_id} LIMIT 1''')

        return True if self.__cur.fetchone() else False
