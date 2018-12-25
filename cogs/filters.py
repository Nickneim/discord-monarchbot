import discord
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
from discord.ext import commands


def get_message_image(message):
    """Returns the first attachment from 'message' if it exists and it's a recognized image, otherwise returns None"""
    if message.attachments:
        attachment = message.attachments[0]
        if attachment.filename.endswith(('.jpg', '.jpeg', '.png')):
            return attachment
    return None


async def download_last_image(ctx, path=None, limit=20):
    """
    Downloads the last image in the last 'limit' messages in the 'ctx' channel
    to 'path' (defaults to <channel_id>.png)
    """
    if path is None:
        path = str(ctx.channel.id) + '.png'
    image = get_message_image(ctx.message)
    if image:
        await image.save(path)
        return True
    async for m in ctx.history(before=ctx.message, limit=limit):
        image = get_message_image(m)
        if image:
            await image.save(path)
            return True
    return False


class Filters:

    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def blur(self, ctx):
        await ctx.send("**processing...**")
        image_path = str(ctx.channel.id) + '.png'
        if not await download_last_image(ctx, path=image_path):
            return await ctx.send("Couldn't find valid image.")
        try:
            image = Image.open(image_path)
        except IOError:
            return await ctx.send("Last image isn't valid.")
        image = image.filter(ImageFilter.BLUR)
        try:
            image.save(image_path)
        except IOError:
            return await ctx.send("Image couldn't be saved.")
        await ctx.send(file=discord.File(image_path))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def invert(self, ctx):
        await ctx.send("**processing...**")
        image_path = str(ctx.channel.id) + '.png'
        if not await download_last_image(ctx, path=image_path):
            return await ctx.send("Couldn't find valid image.")
        try:
            image = Image.open(image_path)
        except IOError:
            return await ctx.send("Last image isn't valid.")
        try:
            alpha = image.getchannel('A')
        except ValueError:
            alpha = None
        image = image.convert("RGB")
        image = ImageOps.invert(image)
        if alpha:
            image.putalpha(alpha)
        try:
            image.save(image_path)
        except IOError:
            return await ctx.send("Image couldn't be saved.")
        await ctx.send(file=discord.File(image_path))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def flipv(self, ctx):
        await ctx.send("**processing...**")
        image_path = str(ctx.channel.id) + '.png'
        if not await download_last_image(ctx, path=image_path):
            return await ctx.send("Couldn't find valid image.")
        try:
            image = Image.open(image_path)
        except IOError:
            return await ctx.send("Last image isn't valid.")
        image = ImageOps.flip(image)
        try:
            image.save(image_path)
        except IOError:
            return await ctx.send("Image couldn't be saved.")
        await ctx.send(file=discord.File(image_path))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def fliph(self, ctx):
        await ctx.send("**processing...**")
        image_path = str(ctx.channel.id) + '.png'
        if not await download_last_image(ctx, path=image_path):
            return await ctx.send("Couldn't find valid image.")
        try:
            image = Image.open(image_path)
        except IOError:
            return await ctx.send("Last image isn't valid.")
        image = ImageOps.mirror(image)
        try:
            image.save(image_path)
        except IOError:
            return await ctx.send("Image couldn't be saved.")
        await ctx.send(file=discord.File(image_path))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def symm(self, ctx, side: str = "left"):
        side = side.lower()
        if side not in ('left', 'right', 'up', 'down'):
            return await ctx.send("Valid sides are 'left', 'right', 'up', and 'down'.")
        await ctx.send("**processing...**")
        image_path = str(ctx.channel.id) + '.png'
        if not await download_last_image(ctx, path=image_path):
            return await ctx.send("Couldn't find valid image.")
        try:
            image = Image.open(image_path)
        except IOError:
            return await ctx.send("Last image isn't valid.")
        w, h = image.size
        if side == 'left':
            crop = image.crop((0, 0, w//2, h))
            crop = ImageOps.mirror(crop)
            image.paste(crop, (round(w / 2 + 0.1), 0))
        elif side == 'right':
            crop = image.crop((round(w / 2 + 0.1), 0, w, h))
            crop = ImageOps.mirror(crop)
            image.paste(crop, (0, 0))
        elif side == 'up':
            crop = image.crop((0, 0, w, h//2))
            crop = ImageOps.flip(crop)
            image.paste(crop, (0, round(h / 2 + 0.1)))
        elif side == 'down':
            crop = image.crop((0, round(h / 2 + 0.1), w, h))
            crop = ImageOps.flip(crop)
            image.paste(crop, (0, 0))
        try:
            image.save(image_path)
        except IOError:
            return await ctx.send("Image couldn't be saved.")
        await ctx.send(file=discord.File(image_path))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def posterize(self, ctx):
        await ctx.send("**processing...**")
        image_path = str(ctx.channel.id) + '.png'
        if not await download_last_image(ctx, path=image_path):
            return await ctx.send("Couldn't find valid image.")
        try:
            image = Image.open(image_path)
        except IOError:
            return await ctx.send("Last image isn't valid.")
        try:
            alpha = image.getchannel('A')
        except ValueError:
            alpha = None
        image = image.convert("RGB")
        image = ImageOps.posterize(image, 2)
        if alpha:
            image.putalpha(alpha)
        try:
            image.save(image_path)
        except IOError:
            return await ctx.send("Image couldn't be saved.")
        await ctx.send(file=discord.File(image_path))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def shrink(self, ctx, per: int = 5):
        await ctx.send("**processing...**")
        if not (1 <= per <= 99):
            return await ctx.send("Percentage must be between 1 and 99")
        else:
            per = 5
        image_path = str(ctx.channel.id) + '.png'
        if not await download_last_image(ctx, path=image_path):
            return await ctx.send("Couldn't find valid image.")
        try:
            image = Image.open(image_path)
        except IOError:
            return await ctx.send("Last image isn't valid.")
        image = image.convert("RGBA")
        w = image.width * per // 100
        h = image.height * per // 100
        image.resize((w, h), resample=Image.LANCZOS)
        try:
            image.save(image_path)
        except IOError:
            return await ctx.send("Image couldn't be saved.")
        await ctx.send(file=discord.File(image_path))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def glitch(self, ctx):
        await ctx.send("**processing...**")
        image_path = str(ctx.channel.id) + '.png'
        if not await download_last_image(ctx, path=image_path):
            return await ctx.send("Couldn't find valid image.")
        try:
            image = Image.open(image_path)
        except IOError:
            return await ctx.send("Last image isn't valid.")
        w, h = image.width, image.height
        image = image.resize((int(w ** .75), int(h ** .75)), resample=Image.LANCZOS)
        image = image.resize((int(w ** .88), int(h ** .88)), resample=Image.BILINEAR)
        image = image.resize((int(w ** .9), int(h ** .9)), resample=Image.BICUBIC)
        image = image.resize((w, h), resample=Image.BICUBIC)
        try:
            alpha = image.getchannel('A')
        except ValueError:
            alpha = None
        image = image.convert("RGB")
        image = ImageOps.posterize(image, 4)
        if alpha:
            image.putalpha(alpha)
        image = ImageEnhance.Sharpness(image).enhance(100.0)
        try:
            image.save(image_path)
        except IOError:
            return await ctx.send("Image couldn't be saved.")
        await ctx.send(file=discord.File(image_path))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def edges(self, ctx):
        await ctx.send("**processing...**")
        image_path = str(ctx.channel.id) + '.png'
        if not await download_last_image(ctx, path=image_path):
            return await ctx.send("Couldn't find valid image.")
        try:
            image = Image.open(image_path)
        except IOError:
            return await ctx.send("Last image isn't valid.")
        try:
            alpha = image.getchannel('A')
        except ValueError:
            alpha = None
        image = image.filter(ImageFilter.SMOOTH)
        image = image.filter(ImageFilter.CONTOUR)
        image = image.convert("RGB")
        image = ImageOps.invert(image)
        image = ImageOps.grayscale(image)
        image = image.convert("RGBA")
        if alpha:
            image.putalpha(alpha)
        try:
            image.save(image_path)
        except IOError:
            return await ctx.send("Image couldn't be saved.")
        await ctx.send(file=discord.File(image_path))


def setup(bot):
    bot.add_cog(Filters(bot))
