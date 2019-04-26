import discord
from discord.ext import commands

from sys import stderr
import logging
import os
import traceback

logging.basicConfig(filename="monarchbot.log", level=logging.INFO)

initial_extensions = ['cogs.frames',
                      'cogs.filters']

prefix = "-"
bot = commands.Bot(command_prefix=prefix)

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except (discord.ClientException, ImportError):
            print(f'Failed to load extension {extension}.', file=stderr)
            traceback.print_exc()


@bot.event
async def on_ready():
    """http://discordpy.readthedocs.io/en/rewrite/api.html#discord.on_ready"""

    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')

    print(f'Successfully logged in and booted...!')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        return await ctx.send(error)
    print(f'Ignoring exception in command {ctx.command}:', file=stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=stderr)


bot.run(os.environ['TOKEN'], bot=True, reconnect=True)
