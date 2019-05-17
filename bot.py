import discord
from discord.ext import commands
import logging
import os

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
            logging.warning(f'Failed to load extension {extension}.')


@bot.event
async def on_ready():
    """http://discordpy.readthedocs.io/en/rewrite/api.html#discord.on_ready"""

    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')

    print(f'Successfully logged in and booted...!')


bot.run(os.environ['TOKEN'], bot=True, reconnect=True)
