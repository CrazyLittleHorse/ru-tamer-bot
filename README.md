# RU Tamer Bot

Небольшой бот для [discord сервера мистиков](https://discord.gg/rWFkPGJ), по игре Black Desert Online. 


## Основные особенности
- Подсчет рейтинга по системе Elo на основе результата дуэли.
- Сохранение рейтинга в DB.
- Вывод статистики о пользователях.


## Начало работы


### Требования

Версия Python 3.6 и выше.
Для проверки используйте:
```
# Linux/macOS
$ python -V

# Windows
$ py -V
```
[Discord.py](https://github.com/Rapptz/discord.py) и [PyMySql](https://github.com/PyMySQL/PyMySQL) 
устанавливаются через  [pip](https://pypi.org/project/pip/):

```
# Linux/macOS
$ python3 -m pip install -U discord.py
$ python3 -m pip install PyMySQL

# Windows
$ py -3 -m pip install -U discord.py
$ py -3 -m pip install -U PyMySql
```

### Установка

При первом запуске, необходимо запустить first_launch.py:
```
#Linux/macOS
$ python3 first_launch.py

#Windows
$ py -3 first_launch.py
```

Следуя инструкциям, настроить все пункты:

```
1. Основные настройки.
2. Настройки рангового модуля.
3. Настройка подключения к MySql.
```
Сгенерированные настройщиком файлы находятся в:
```
ru-tamer-bot
├── config
|   └── config.json #Основной файл настроек. 
└── Extensions
    └── config
       ├── rating.json #Настройки рангового модуля.
       └── database.json #Настройки подключения к базе данных. 
```

Файлы можно редактировать вручную, при условии сохранения их структуры.


## Развертывание

Бот на 99% подходит для развертывания на сервисе [Heroku](http://heroku.com/).

Помимо [Heroku](http://heroku.com/), вам необходим сервер с базой данных MySql.

Так же зарегистрируйте вашего бота на портале [Discord](https://discord.com/developers/applications).

Для развертывания на [Heroku](http://heroku.com/), 
вам необходимо зарегистрироваться, создать новое приложение 
и в настройках приложения, указать все перечисленные ниже переменные:
```
'BOT_TOKEN' - токен вашего бота, генерируется на портале discord dev.
'DB_HOST' - host mysql базы данных.
'DB_NAME' - название бд.
'DB_USER' - имя пользователя от бд.
'DB_PASSWORD' - пароль от бд.
'OWNER' - discord id владельца сервера, можно получить, включив режим разработчика в discord.
'PREFIX' - префикс перед коммандами бота.
'TIMEOUT' - время ожидания подтверждения дуэли(в секундах)
'WORK_CHANNEL' - id канала, в котором будут работать команды бота.
```

## Использовано при разработке

* [Discord.py](https://github.com/Rapptz/discord.py) - API wrapper for Discord written in Python
* [PyMySql](https://github.com/PyMySQL/PyMySQL) - Pure Python MySQL Client
* [A-Good-Help-Command-for-discord.py](https://github.com/niztg/A-Good-Help-Command-for-discord.py) - A help command for discord.py that can return the description of any cog, command or subcommand.



## Именование версий

Мы используем [SemVer](http://semver.org/) для именования версий. Доступные версии можно посмотреть в [тагах этого репозитория](https://github.com/CrazyLittleHorse/ru-tamer-bot/tags). 

## Авторы

* **Yuri Zotov** - *начальная работа* - [CrazyLittleHorse](https://github.com/CrazyLittleHorse)


## Лицензия

Этот проект использует MIT License - смотри [LICENSE.md](LICENSE.md) для подробностей.

## Acknowledgments

* Благодарность всем кто работал на инструментами, которые были использованы при разработке проекта.

