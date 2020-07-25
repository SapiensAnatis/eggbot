import discord
import utils
from discord.ext import commands

initial_extensions = ["uv"]
bot = commands.Bot(command_prefix="$", description="UV mapping bot")

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

@bot.event
async def on_ready():
    utils.log(f"Logged in as: {bot.user.name} (ID: {bot.user.id})")
    utils.log(f"Using discord.py version: {discord.__version__}")


token_file = open("token.txt")
token = token_file.read()
token_file.close()
bot.run(token, bot=True, reconnect=True)
