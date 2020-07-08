"""
Hope this code helps! Anyone is free to use it under any circumstances, no crediting necessary. Note that it is absolutely
not perfect and other coders can definitely improve upon it, but it works and that's all that matters. ;)
You can join my Discord Server https://discord.gg/2fxKxJH for any questions or simply PM me @♿niztg#7532 on Discord for any questions.
Перевел на Русский Sanche
"""
import discord
from discord.ext import commands

colour = discord.Color.green()  # 0x00dcff


class Help(commands.Cog, name='помощь'):
    """Модуль помощи"""  # this is the cog description

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Расширение Help, успешно загружено.')

    @commands.command(name='категории')
    async def cogs(self, ctx):
        """≫ Показывает все доступные категории"""
        cogs = []
        for cog in self.client.cogs:
            cogs.append(
                f"`{cog}` • {self.client.cogs[cog].__doc__}")  # adds cogs and their description to list. if the cog doesnt have a description it will return as "None"
        await ctx.send(embed=discord.Embed(colour=colour, title=f"Все категории ({len(self.client.cogs)})",
                                           description=f"Используйте `{ctx.prefix}help <категория>` чтобы узнать больше!" + "\n\n" + "\n".join(
                                               cogs)))  # joins each item in the list with a new line

    @commands.command(aliases=['?', 'помощь'])
    async def help(self, ctx, *, command=None):
        """≫ Показывает все доступные команды и категории."""
        pre = ctx.prefix
        footer = f"Используйте '{pre}help [команда/категория]' для подробностей!"
        list_of_cogs = []
        walk_commands = []
        final_walk_command_list = []
        sc = []
        format = []
        try:
            for cog in self.client.cogs:
                list_of_cogs.append(cog)
            if command:
                cmd = self.client.get_command(command)
            else:
                cmd = None
            if not command:
                k = []
                for cog_name, cog_object in self.client.cogs.items():
                    cmds = []
                    for cmd in cog_object.get_commands():
                        if not cmd.hidden:
                            cmds.append(f"`{cmd.name}`")
                    k.append(f'➤ **{cog_name}**\n{"•".join(sorted(cmds))}\n')
                for wc in self.client.walk_commands():
                    if not wc.cog_name and not wc.hidden:
                        if isinstance(wc, commands.Group):
                            walk_commands.append(wc.name)
                            for scw in wc.commands:
                                sc.append(scw.name)
                        else:
                            walk_commands.append(wc.name)
                for item in walk_commands:
                    if item not in final_walk_command_list and item not in sc:
                        final_walk_command_list.append(item)
                for thing in final_walk_command_list:
                    format.append(f"`{thing}`")
                k.append("**Команды без категории**\n" + " • ".join(sorted(format)))
                await ctx.send("** **", embed=discord.Embed(colour=colour, title=f"{self.client.user.name} помощь",
                                                            description=f"Используйте `{pre}help [категория]` для "
                                                                        f"получения информации о категории.\nИли "
                                                                        f"используйте `{pre}help [команда]` для "
                                                                        f"получения информации о команде.\n\n" +
                                                                        "\n".join(
                                                                k)))
            elif command in list_of_cogs:
                i = []
                cog_doc = self.client.cogs[command].__doc__ or " "
                for cmd in self.client.cogs[command].get_commands():
                    if not cmd.aliases:
                        char = "\u200b"
                    else:
                        char = "•"
                    help_msg = cmd.help or "У этой команды нет описания"
                    i.append(f"→ `{cmd.name}{char}{'•'.join(cmd.aliases)} {cmd.signature}` • {help_msg}")
                await ctx.send(embed=discord.Embed(title=f"{command} категория", colour=colour,
                                                   description=cog_doc + "\n\n" + "\n".join(i)).set_footer(text=footer))
            elif command and cmd:
                help_msg = cmd.help or "У этой команды нет описания"
                parent = cmd.full_parent_name
                if len(cmd.aliases) > 0:
                    aliases = '•'.join(cmd.aliases)
                    cmd_alias_format = f'{cmd.name}•{aliases}'
                    if parent:
                        cmd_alias_format = f'{parent} {cmd_alias_format}'
                    alias = cmd_alias_format
                else:
                    alias = cmd.name if not parent else f'{parent} {cmd.name}'
                embed = discord.Embed(title=f"{alias} {cmd.signature}", description=help_msg, colour=colour)
                embed.set_footer(text=footer)
                if isinstance(cmd, commands.Group):
                    sub_cmds = []
                    for sub_cmd in cmd.commands:
                        schm = sub_cmd.help or "У этой команды нет описания"
                        if not sub_cmd.aliases:
                            char = "\u200b"
                        else:
                            char = "•"
                        sub_cmds.append(
                            f"→ `{cmd.name} {sub_cmd.name}{char}{'•'.join(sub_cmd.aliases)} {sub_cmd.signature}` • {schm}")
                    scs = "\n".join(sub_cmds)
                    await ctx.send(
                        embed=discord.Embed(title=f"{alias} {cmd.signature}", description=help_msg + "\n\n" + scs,
                                            colour=colour).set_footer(text=f"{footer} • → подкоманды"))
                else:
                    await ctx.send(embed=embed)
            else:
                await ctx.send(f"Команда {command}` не найдена.")
        except Exception as er:
            await ctx.send(er)


def setup(bot):
    bot.remove_command('help')
    bot.add_cog(Help(bot))
