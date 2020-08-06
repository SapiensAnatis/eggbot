import discord
import typing
import aiohttp
import utils
import os
import shutil
import asyncio
from discord.ext import commands


"""
Converters to grab texture data using discord.ext.commands
"""
class ImageURLData(commands.Converter):
    async def convert(self, ctx, argument):
        if utils.is_url(argument):
            async with aiohttp.ClientSession() as session:
                async with session.get(argument) as response:
                    if response.status == 200:
                        img_data = await response.read()
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
        if argument == "attachment" or argument == "a":
            if len(ctx.message.attachments) > 0:
                # Select only the first attachment with an image extension
                # The bot could probably be adapted to do multiple renders,
                # but I don't want one user clogging up the entire queue. 
                
                # Maybe a maximum of 3 to 5? It's something to look into

                attachment = self.get_valid_attachment(ctx.message.attachments)

                if attachment is None:
                    raise discord.ext.commands.BadArgument() # no attachments w/ correct type

                img_data = await attachment.read()
                return img_data
            else:
                raise discord.ext.commands.BadArgument()
        else:
            raise discord.ext.commands.BadArgument()
    
    @staticmethod
    def get_valid_attachment(attachments):
        for a in attachments:
            for e in utils.image_extensions:
                if a.url.endswith(f".{e}"):
                    return a
        
        # if loop terminated without a return, give None for error handling
        return None
            


class UVCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Reset job ID as zero
        self.job_id = 0
        # Clear directory
        utils.log("Purging non-essential files...")
        non_core_file_ends = ["_model.blend", "_model.blend1", "_texture.image", "_script.py", "_result.png"]
        for f in os.listdir(utils.get_bot_dir()):
            for e in non_core_file_ends:
                if f.endswith(e):
                    print("\tRemoving:", f)
                    os.remove(f)
            
        # Get valid shapes list
        self.blend_files_dir = os.path.join(utils.get_bot_dir(), "models")
        blend_files = [f for f in os.listdir(self.blend_files_dir) if f.endswith(".blend")]
        self.shapes = [f[:-6] for f in blend_files]
        
        # Canned error messages that I didn't want to repeat
        self.no_img_data_err = ("Could not get any image data from your message.\n" +
                           "I can take image data from image URLs, user avatars " +
                           "(@mention or id), emojis, and image attachments.")
        
        self.no_valid_shape_err = "You must give a valid shape. Options are:"
        for s in self.shapes:
            self.no_valid_shape_err += f"\n\t• {s}"

    @commands.command(name='map', aliases=['uv'])
    async def prepare_render(
        self, 
        ctx, 
        shape: str,
        tex_data: typing.Union[
            ImageURLData, UserAvatarData, EmojiImageData, AttachmentData
        ]
    ):
        f"""
        Render a shape with a custom texture.
        Arguments:
            - shape: any of {self.shapes}
            - tex_data: can be a URL, user mention/ID, emoji or image attachment ({utils.image_extensions})
        """
        # Check that shape is valid
        if not (shape in self.shapes):
            await ctx.send(self.no_valid_shape_err)
            return
        
        # Set job ID to requester id
        self.job_id = ctx.message.author.id
        
        # Would love to do async file I/O just for overkill purposes but that's more trouble
        # than it's worth, even for showoff points

        # Save texture image file
        with open(f"job{self.job_id}_texture.image", "wb") as f: 
            # Blender doesn't really care what the extension is
            f.write(tex_data)
        
        # Copy .blend file
        blend_filepath_src = os.path.join(self.blend_files_dir, shape + ".blend")
        blend_filepath_dst = os.path.join(utils.get_bot_dir(), f"job{self.job_id}_model.blend")
        shutil.copy(blend_filepath_src, blend_filepath_dst)

        # Generate script to apply texture
        with open(f"job{self.job_id}_script.py", "w") as f:
            f.write(
f"""import bpy
bpy.data.images[\"texture\"].filepath = "//job{self.job_id}_texture.image"
bpy.ops.wm.save_as_mainfile(filepath="job{self.job_id}_model.blend")"""
            )
        
        # Render
        proc = await asyncio.create_subprocess_shell(
                f"blender -b job{self.job_id}_model.blend -P job{self.job_id}_script.py -o //f#_job{self.job_id}_result.png -f 1 ",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
        )

        await proc.communicate()
        utils.log(f'Render of job {self.job_id} completed.')
        await ctx.send(f"{ctx.message.author.mention}", file=discord.File(f"f1_job{self.job_id}_result.png"))



    @prepare_render.error
    async def prepare_render_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == "shape":
                await ctx.send(self.no_valid_shape_err)
            if error.param.name == "tex_data":
                await ctx.send(self.no_img_data_err)
                           
        elif isinstance(error, commands.BadUnionArgument):
            await ctx.send(self.no_img_data_err)
        
        else:
            print(error)

def setup(bot):
    bot.add_cog(UVCog(bot))
    