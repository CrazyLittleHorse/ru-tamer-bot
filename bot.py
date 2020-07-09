#   Библиотеки
import asyncio
import discord
from discord.ext import commands
import json
from pathlib import Path
import logging
import os

#   Получение рабочей директории бота
cwd = str(Path(__file__).parents[0])
#   Подключение и основные настройки бота
try:

    with open(os.path.join(cwd, 'config', 'config.json')) as j:
        config_file = json.load(j)

except FileNotFoundError:
    config_file = None

#   Включение логгирования
logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix=os.environ.get('PREFIX', config_file['prefix']),
                   case_insensitive=True,
                   owner_id=os.environ.get('OWNER', config_file['owner']))


@bot.event
async def on_ready():
    print(f'{"#" * 35}\n{bot.user.name} готов к работе.\nРабочий каталог: {cwd}\n{"#" * 35}')


@bot.event
async def on_command_error(ctx, error):
    print(f'В сообщении от {ctx.author}: "{ctx.message.content}" Ошибка: {error}')

    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f'ОШИБКА: команда {ctx.message.content.split()[0]} не найдена.')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'ОШИБКА: у {ctx.author.mention} '
                       f'недостаточно прав '
                       f'для использования команды {ctx.message.content.split()[0]}')
    if isinstance(error, commands.MissingRole):
        await ctx.send(f'ОШИБКА: у {ctx.author.mention} '
                       f'отсутствует роль {error.missing_role} '
                       f'для использования команды {ctx.message.content.split()[0]}')


@bot.event
async def on_message(message):
    #   Игнорирование сообщений от ботов
    if message.author.bot:
        return

    if message.channel.id == int(os.environ.get('WORK_CHANNEL')):
        await bot.process_commands(message)


@bot.command(name='purge', help='Удаляет необходимое количество сообщений из канала.', hidden=True)
@commands.has_permissions(administrator=True)
async def purge_message(ctx, limit: int):
    await ctx.channel.purge(limit=limit)


@bot.command(name='rex', hidden=True)
@commands.has_permissions(administrator=True)
async def extension_reload(ctx, ext_name):
    bot.reload_extension(f'Extensions.{ext_name}')


@bot.command(name='lex', hidden=True)
@commands.has_permissions(administrator=True)
async def extension_load(ctx, ext_name):
    bot.load_extension(f'Extensions.{ext_name}')


@bot.command(name='uex', hidden=True)
@commands.has_permissions(administrator=True)
async def extension_unload(ctx, ext_name):
    bot.unload_extension(f'Extensions.{ext_name}')


@bot.command(name='ex', hidden=True)
@commands.has_permissions(administrator=True)
async def extensions_menu(ctx, ext_name):
    for filename in os.listdir(os.path.join(cwd, 'Extensions')):
        if filename.endswith('.py') and filename == f'{ext_name.lower()}.py' and not filename.startswith('_'):

            msg = await ctx.send(f'```Модуль {ext_name} найден.\nЧто вы хотите с ним сделать?```')

            ex_reactions = ['📥', '♻', '📤']

            for r in ex_reactions:
                await msg.add_reaction(r)

            def check(reaction, user):
                """
                Проверка на добавление эмоции.
                :type reaction discord.Reaction
                :type user: discord.User
                """
                return (reaction.message.id == msg.id) and (user.id == ctx.author.id) and (
                            str(reaction) in ex_reactions)

            try:
                reaction, user = await bot.wait_for('reaction_add', check=check, timeout=10)
            except asyncio.TimeoutError:
                reaction = None
                await msg.delete()
                await ctx.message.delete()

            if str(reaction) == ex_reactions[0]:
                bot.load_extension(f'Extensions.{ext_name.lower()}')
                await msg.edit(content=f'```Модуль {ext_name}, успешно загружен.```')
            elif str(reaction) == ex_reactions[1]:
                bot.reload_extension(f'Extensions.{ext_name.lower()}')
                await msg.edit(content=f'```Модуль {ext_name}, успешно перезагружен.```')
            elif str(reaction) == ex_reactions[2]:
                bot.unload_extension(f'Extensions.{ext_name.lower()}')
                await msg.edit(content=f'```Модуль {ext_name}, успешно отключен.```')
            await ctx.message.delete()
            for r in ex_reactions:
                await msg.clear_reaction(r)
            return
    await ctx.send(f'```Модуль {ext_name} не найден```')


if __name__ == '__main__':

    for file in os.listdir(os.path.join(cwd, 'Extensions')):
        if file.endswith('.py') and not file.startswith('_'):
            bot.load_extension(f'Extensions.{file[:-3]}')

    bot.run(os.environ.get("BOT_TOKEN", config_file['token']))
