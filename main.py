import discord
import utils
from discord.ext import commands

extensions = ["uv"]
bot = commands.Bot(command_prefix="$", description="UV mapping bot")

if __name__ == '__main__':
    for extension in extensions:
        bot.load_extension(extension)

@bot.event
async def on_ready():
    utils.log(f"Logged in as: {bot.user.name} (ID: {bot.user.id})")
    utils.log(f"Using discord.py version: {discord.__version__}")


@bot.command(aliases=['reload', 'restart'], pass_context=True)
async def _reload(ctx, *, extension_arg: str = None):
    if ctx.message.author.id != 586753708432424978:
        utils.log(f"User {ctx.message.author.id} attempted unauthorized reload operation")
        await ctx.send("You aren't allowed to do that.")
        return



    if extension_arg is None: # generic call
        utils.log("Received call to reload all modules:")
        for extension in extensions:
            utils.log(f"  Reloading {extension}...")
            bot.unload_extension(extension)
            bot.load_extension(extension)
            utils.log(f"{extension} successfully reloaded.")
        utils.log("All extensions successfully reloaded.")
        await ctx.send("All extensions successfully reloaded.")
    else:
        if not (extension_arg in extensions):
            utils.log(f"Couldn't find module {extension_arg}")
            await ctx.send(f"Extension {extension_arg} not found.")
        else:
            utils.log(f"Received call to reload module {extension_arg}.")
            utils.log(f"Reloading {extension_arg}...")
            bot.unload_extension(extension_arg)
            bot.load_extension(extension_arg)
            utils.log(f"Successfully reloaded extension {extension_arg}.")
            await ctx.send(f"Successfully reloaded extension {extension_arg}.")

token_file = open("token.txt")
token = token_file.read()
token_file.close()
bot.run(token, bot=True, reconnect=True)
