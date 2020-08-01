import discord
import typing
import aiohttp
import utils
from discord.ext import commands

class ImageURLData(commands.Converter):
    async def convert(self, ctx, argument):
        if utils.is_url(argument):
            async with aiohttp.ClientSession() as session:
                async with session.get(argument) as response:
                    if response.status == 200:
                        img_data = response.read()
                        return img_data
        else:
            raise discord.ext.commands.BadArgument()

class UserAvatarData(commands.UserConverter):
    async def convert(self, ctx, argument):
        user = await super().convert(ctx, argument)
        asset = user.avatar_url_as(format="png")
        img_data = await asset.read()
        return img_data

class EmojiImageData(commands.PartialEmojiConverter):
    async def convert(self, ctx, argument):
        partialemoji = await super().convert(ctx, argument)
        asset = partialemoji.url
        img_data = await asset.read()
        return img_data

class AttachmentData(commands.Converter):
    async def convert(self, ctx, argument):
        if len(ctx.message.attachments) > 0:
            # Select only the first attachment with an image extension
            # The bot could probably be adapted to do multiple renders,
            # but I don't want one user clogging up the entire queue. 
            #
            # Maybe a maximum of 3 to 5? It's something to look into

            attachment = self.get_valid_attachment(ctx.message.attachments)
            if attachment is None:
                raise discord.ext.commands.BadArgument() # no attachments with correct type

            img_data = await attachment.read()
            return img_data
        else:
            raise discord.ext.commands.BadArgument()
    
    @staticmethod
    def get_valid_attachment(attachments):
        for a in attachments:
            for e in utils.image_extensions:
                if a.endswith(f".{e}"):
                    return a
        
        # if loop terminated without a return, give None for error handling
        return None
            


class UVCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='map', aliases=['uv'])
    async def prepare_render(
        self, ctx, 
        shape: str,
        texture_arg: typing.Union[ImageURLData, UserAvatarData, EmojiImageData, AttachmentData]
        ):
        """
        Converters grab texture data, this saves it and queues up the job 
        """
        


"""
how to use arbitrary textures:

1. copy base blend file and texture to its own folder
2. run python script in blend file to grab filepath of texture in that folder and set the texture reference to it
3. render
"""

def setup(bot):
    bot.add_cog(UVCog(bot))
    