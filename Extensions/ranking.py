import asyncio
import datetime
import math
import os
import json
import discord
from discord.ext import commands
from pathlib import Path
from Extensions.utils.database import Database

# Список всех рангов в формате (необходимый рейтинг), ссылка на иконку, название ранга, множитель бонуса
RATING = (
    (range(0, 1040), 'https://i.imgur.com/SuYYsXY.png', 'Без ранга', 60),

    (range(1040, 1100), 'https://i.imgur.com/XbVzYHR.png', 'Бронза 1', 55),
    (range(1100, 1160), 'https://i.imgur.com/azG6I8e.png', 'Бронза 2', 55),
    (range(1160, 1220), 'https://i.imgur.com/TkUqBsD.png', 'Бронза 3', 50),
    (range(1220, 1280), 'https://i.imgur.com/WSOnsHc.png', 'Бронза 4', 50),
    (range(1280, 1340), 'https://i.imgur.com/bIVnTrp.png', 'Бронза 5', 45),
    (range(1340, 1400), 'https://i.imgur.com/YWT7SbH.png', 'Бронза 6', 45),

    (range(1400, 1440), 'https://i.imgur.com/yx2M1Tm.png', 'Серебро 1', 40),
    (range(1440, 1480), 'https://i.imgur.com/qOvFcoL.png', 'Серебро 2', 40),
    (range(1480, 1520), 'https://i.imgur.com/7wy6xxV.png', 'Серебро 3', 40),
    (range(1520, 1560), 'https://i.imgur.com/vSNTJWw.png', 'Серебро 4', 35),
    (range(1560, 1600), 'https://i.imgur.com/R8ZKpS5.png', 'Серебро 5', 35),
    (range(1600, 1650), 'https://i.imgur.com/gYVyfxs.png', 'Серебро 6', 35),

    (range(1650, 1690), 'https://i.imgur.com/lt25mUK.png', 'Золото 1', 30),
    (range(1690, 1730), 'https://i.imgur.com/JYbfWt6.png', 'Золото 2', 30),
    (range(1730, 1770), 'https://i.imgur.com/qax6ldG.png', 'Золото 3', 30),
    (range(1770, 1810), 'https://i.imgur.com/0FJ7Xyw.png', 'Золото 4', 25),
    (range(1810, 1850), 'https://i.imgur.com/JAdKmVk.png', 'Золото 5', 25),
    (range(1850, 1900), 'https://i.imgur.com/B9DfCPb.png', 'Золото 6', 25),

    (range(1900, 1940), 'https://i.imgur.com/xU2rLSK.png', 'Платина 1', 20),
    (range(1940, 1980), 'https://i.imgur.com/zbnkEvM.png', 'Платина 2', 20),
    (range(1980, 2020), 'https://i.imgur.com/N8OY1fr.png', 'Платина 3', 20),
    (range(2020, 2060), 'https://i.imgur.com/Tv3ATgf.png', 'Платина 4', 15),
    (range(2060, 2100), 'https://i.imgur.com/0Q4HS8r.png', 'Платина 5', 15),
    (range(2100, 2150), 'https://i.imgur.com/LnqpvKr.png', 'Платина 6', 15),

    (range(2150, 2190), 'https://i.imgur.com/u3tDWU6.png', 'Бриллиант 1', 10),
    (range(2190, 2230), 'https://i.imgur.com/Ks7r0Lj.png', 'Бриллиант 2', 10),
    (range(2230, 2270), 'https://i.imgur.com/9f5l9Dk.png', 'Бриллиант 3', 10),
    (range(2270, 2310), 'https://i.imgur.com/5hUQ7bN.png', 'Бриллиант 4', 5),
    (range(2310, 2350), 'https://i.imgur.com/luuN1JH.png', 'Бриллиант 5', 5),
    (range(2350, 2400), 'https://i.imgur.com/0VCD9Mn.png', 'Бриллиант 6', 5),

    (range(2400, 5000), 'https://i.imgur.com/vG8Vhac.png', 'Оникс', 3),

)

#   Получение рабочей директории МОДУЛЯ
cwd = str(Path(__file__).parents[0])


class Elo:
    """Расчет рейтинга по системе Elo
    Ra - rating игрока 1
    Rb - rating игрока 2
    Sa - счет игрока 1
    Sb - счет игрока 2"""

    def __init__(self, Ra: int, Rb, Sa, Sb):
        self.__Ra = Ra
        self.__Rb = Rb
        self.__Sa = Sa
        self.__Sb = Sb

    def __We(self):
        """Ожидаемый результат боя"""

        return 1 / (1 + 10 ** ((self.__Rb - self.__Ra) / 400))

    def __W(self):
        """Результат боя"""

        return 1 if self.__Sa > self.__Sb else 0.5 if self.__Sa == self.__Sb else 0

    def __G(self):
        """Бонус за итоговый счет дуэли.
        ELOW - Elo rating win
        ELOL - Elo rating lose
        Если счет равен, присужу победу тому, у кого меньше рейтинг"""

        if self.__Sa > self.__Sb:
            ELOW = self.__Ra
            ELOL = self.__Rb
        elif self.__Sa < self.__Sb:
            ELOW = self.__Rb
            ELOL = self.__Ra
        else:
            return 3

        G = math.log((abs(self.__Sa - self.__Sb) + 1) * (2.2 / ((ELOW - ELOL) * .001 + 2.2)))
        return G if G < 3 else 3

    def __K(self) -> int:
        """Коэффициент в зависимости от рейтинга."""
        for rating_list in RATING:
            if self.__Ra in rating_list[0]:
                return rating_list[3]

    def new_elo_rating(self):
        """Новый рейтинг"""
        return round(self.__Ra + self.__K() * self.__G() * (self.__W() - self.__We()))


def rating_img(user_rating: int) -> tuple:
    """Parsing списка рейтинга"""
    for rating_list in RATING:
        if user_rating in rating_list[0]:
            return rating_list[1], rating_list[2]


class RankingSystem(commands.Cog, name='ранговая система'):
    """Модуль ранговой системы. Позволяет высчитать рейтинг, по статистике побед и поражений, использует систему Elo.
    """  # help doc

    def __init__(self, bot):
        self.bot = bot

        with open(os.path.join(cwd, 'config', 'ranking', 'rating.json'), 'r') as f:
            # Чтение файла конфигурации для рейтинга
            rating_config = json.loads(f.read())
            # Список ролей, выдаваемых за рейтинг.
            self.RATING_ROLE = rating_config['RATING_ROLE']
            # Включение или отключение выдачи ролей за рейтинг
            self.ROLE_FOR_RATING = rating_config['ROLE_FOR_RATING']
            # Канал в котором работает бот
            self.WORK_CHANNEL = os.environ.get('WORK_CHANNEL', rating_config['WORK_CHANNEL'])
            # Таймаут ожидания, для подтверждения дуэли
            self.TIMEOUT = int(os.environ.get('TIMEOUT', rating_config['TIMEOUT']))

    @commands.Cog.listener()
    async def on_ready(self):
        print('Расширение RankingSystem, успешно загружено.')

    @commands.command(name='add', hidden=True)
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, member: discord.Member, user_rating):
        with Database() as db:
            db.new_rating(user_id=member.id, user_rating=user_rating, user_loses=0, user_wins=0)
        await ctx.send(f'Пользователь {member.display_name} добавлен.')

    @commands.command(name='remove', hidden=True)
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, member: discord.Member):
        with Database() as db:
            db.remove_user(member.id)
        await ctx.send(f'Пользователь {member.display_name}, удален из рейтинга.')

    @commands.command(name='info', aliases=['инфо'], help='Показывает информацию о вас.')
    async def info(self, ctx):
        with Database() as db:
            user_info = db.get_info(ctx.author.id)

        emb = discord.Embed(
            title=f'{ctx.author.name}',
            type='rich',
            colour=ctx.author.top_role.color
        )

        if user_info:
            rating_league = rating_img(user_info[1])
            emb.add_field(name='Рейтинг: ', value=f'{user_info[1]}')

            if Database().get_champion(ctx.author.id):
                emb.add_field(name='Ранг: ', value='Чемпион')
                emb.set_thumbnail(url='https://i.imgur.com/xoIMHh2.png')
            else:
                emb.add_field(name='Лига: ', value=f'{rating_league[1]}')
                emb.set_thumbnail(url=rating_league[0])

            if user_info[2] > 1 and user_info[3] > 1:
                kill_death = user_info[2] / user_info[3]
                kill_death = f'{kill_death:.2f}'
                emb.add_field(name='K/D:', value=f'{kill_death}', inline=False)
        else:
            emb.set_thumbnail(url=RATING[0][1])
            emb.add_field(name='Ранг:', value=RATING[0][2])
        await ctx.send(embed=emb)

    @commands.command(name='roles', aliases=['роли', 'role', 'роль'])
    async def rating_roles(self, ctx):
        """Показывает все роли, выдаваемые за рейтинг."""

        if self.ROLE_FOR_RATING:
            emb = discord.Embed(title='Роли за рейтинг',
                                description='Роли выдаются автоматически,\nпри достижении указанного рейтинга.',
                                type='rich',
                                timestamp=datetime.datetime.utcnow(),
                                colour=discord.Color.green())
            for role in self.RATING_ROLE:
                emb.add_field(name=f'{role[1]}',
                              value=f'{role[0]}',
                              inline=False)

            await ctx.send(embed=emb)
        else:
            await ctx.send('В данный момент, роли за рейтинг не выдаются')

    @commands.command(name='duel', aliases=['дуэль'])
    async def duel(self, ctx, member: discord.Member, *counts: str):
        """Внесение данных о дуэли в базу.\nФормат: "!duel @Соперник победы поражения"\n
        Помните, что необходимо именно упомянуть соперника."""  # help doc
        if member.id == ctx.author.id or member.bot:
            await ctx.send('Ха-ха, нет, даже не думай, что я на это поведусь.')
            return

        if len(counts) == 0:

            await ctx.send('ОШИБКА: Отсутствует результат дуэли.')
            return

        elif len(counts) == 1:  # В случае если есть только одно значение

            for i in ['/', '-', r'\\', ',', '.', ' ', '|']:
                if len(counts) == 1:
                    counts = counts[0].split(i)  # разделяет значение по символу в []

            try:

                counts = [int(count) if int(count) > 0 else 1 for count in counts]  # Конвертирование в int != 0

            except ValueError:

                await ctx.send('ОШИБКА: Данные, которые вы ввели, не получается преобразовать в число.')

                return

        if len(counts) == 2:
            # добавление пользователей в таблицу, если их там нет.
            if not Database().check_user(ctx.author.id):
                with Database() as db:
                    db.new_rating(user_id=ctx.author.id, user_wins=0, user_loses=0, user_rating=1400)

            if not Database().check_user(member.id):
                with Database() as db:
                    db.new_rating(user_id=member.id, user_wins=0, user_loses=0, user_rating=1400)

            try:
                counts = list(map(int, counts))
            except ValueError:
                await ctx.send('ОШИБКА: Данные, которые вы ввели, не получается преобразовать в число.')
                return
            # отправления сообщения с эмоциями подтверждения/отказа
            message = await ctx.send(f'{member.mention} подтвердите результат дуэли. \n'
                                     f'```{ctx.author.display_name} {counts[0]} | {counts[1]} {member.display_name}```')

            emote = ['✅', '🚫']
            for e in emote:
                await message.add_reaction(e)

            def check(reaction_cls, user_cls):
                return (reaction_cls.message.id == message.id) and (user_cls.id == member.id) and (str(reaction_cls) in emote)

            # =========== Ожидание эмоции.
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=self.TIMEOUT)
            except asyncio.TimeoutError:  # Если время(TIMEOUT) подтверждения истекло.
                await message.edit(
                    content=f'~~```{ctx.author.display_name} {counts[0]} | {counts[1]} {member.display_name}```~~')

                for e in emote:
                    await message.clear_reaction(e)
                return
            # =========== Если эмоция подтверждения.
            if str(reaction) == emote[0]:
                with Database() as db:
                    first_men = db.get_info(ctx.author.id)

                    second_men = db.get_info(member.id)

                    first_men_rating = Elo(int(first_men[1]), int(second_men[1]), int(counts[0]),
                                           int(counts[1])).new_elo_rating()
                    second_men_rating = Elo(int(second_men[1]), int(first_men[1]), int(counts[1]),
                                            int(counts[0])).new_elo_rating()
                    # Добавление роли автору и сопернику, если они набрали необходимое значение рейтинга.
                    if self.ROLE_FOR_RATING:
                        for i in self.RATING_ROLE:
                            if first_men_rating >= i[0] and ctx.guild.get_role(i[2]) not in ctx.author.roles:
                                await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name=i[1]))
                                emb = discord.Embed(
                                    title='Поздравляю.',
                                    description='Вы набрали достаточно очков рейтинга, для получения роли.',
                                    type='rich',
                                    colour=ctx.guild.get_role(i[2]).color
                                )
                                emb.set_thumbnail(url=rating_img(first_men_rating)[0])
                                emb.add_field(name='Ваш рейтинг:', value=str(first_men_rating))
                                emb.add_field(name='Полученная роль:', value=i[1])
                                await ctx.author.send(embed=emb)

                            if second_men_rating >= i[0] and ctx.guild.get_role(i[2]) not in member.roles:
                                await member.add_roles(discord.utils.get(ctx.guild.roles, name=i[1]))
                                emb = discord.Embed(
                                    title='Поздравляю.',
                                    description='Вы набрали достаточно очков рейтинга, для получения роли.',
                                    type='rich',
                                    colour=ctx.guild.get_role(i[2]).color
                                )
                                emb.set_thumbnail(url=rating_img(second_men_rating)[0])
                                emb.add_field(name='Ваш рейтинг:', value=str(second_men_rating))
                                emb.add_field(name='Полученная роль:', value=i[1])
                                await member.send(embed=emb)

                    # добавление рейтинга в таблицу.
                    db.new_rating(first_men[0], first_men_rating, counts[0], counts[1])
                    db.new_rating(second_men[0], second_men_rating, counts[1], counts[0])

                    # Вычисления, на сколько изменился рейтинг.
                    first_men_rating -= int(first_men[1])
                    second_men_rating -= int(second_men[1])

                await message.edit(content=f'```{first_men_rating} {ctx.author.display_name} {counts[0]} |'
                                           f' {counts[1]} {member.display_name} {second_men_rating}```')
                for e in emote:
                    await message.clear_reaction(e)

            # =========== Если эмоция отказа.
            if str(reaction) == emote[1]:
                await message.edit(
                    content=f'~~```{ctx.author.display_name} {counts[0]} | {counts[1]} {member.display_name}```~~')
                for e in emote:
                    await message.clear_reaction(e)

        else:
            await ctx.send('ОШИБКА: Результат дуэли указывается в формате "победы поражения".')
            return

    @commands.command(name='top', aliases=['топ'], help='Показывает топ по рейтингу.')
    async def top(self, ctx, count='5'):
        try:
            count = int(count)
            if count not in range(0, 11):
                count = 5
        except ValueError:
            count = 5

        with Database() as db:
            user_top = db.get_top(count)

        if user_top:
            emb = discord.Embed(
                title=f'Топ {count} игроков:',
                type='rich',
                timestamp=datetime.datetime.utcnow(),
                colour=discord.Guild.get_member(ctx.guild, user_top[0][0]).top_role.colour
            )

            emb.set_thumbnail(url=discord.Guild.get_member(ctx.guild, user_top[0][0]).avatar_url)
            top_count = 1

            for i in user_top:
                user = discord.Guild.get_member(ctx.guild, i[0])
                emb.add_field(name=f'{top_count} место:', value=f'{i[1]} - {user.display_name}', inline=False)
                top_count += 1

            emb.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        else:
            emb = discord.Embed(title='ОШИБКА: Топ игроков, пуст.')

        await ctx.send(embed=emb)


def setup(bot):
    bot.add_cog(RankingSystem(bot))
