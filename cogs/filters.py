import io
import discord
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
from discord.ext import commands


def get_message_attachment(message, allowed_extensions=('.jpg', '.jpeg', '.png')):
    """Returns the first attachment from 'message' if it exists and it's a recognized image, otherwise returns None"""
    if message.attachments:
        attachment = message.attachments[0]
        if attachment.filename.endswith(allowed_extensions):
            return attachment
    return None


async def get_last_image(ctx, limit=20):
    """
    Returns the last image in the last 'limit' messages in the 'ctx' channel
    Raises IOError if last image isn't a valid image
    """
    attachment = get_message_attachment(ctx.message)
    if attachment:
        f = io.BytesIO()
        await attachment.save(f)
        return Image.open(f)
    async for m in ctx.history(before=ctx.message, limit=limit):
        attachment = get_message_attachment(m)
        if attachment:
            f = io.BytesIO()
            await attachment.save(f)
            return Image.open(f)
    return None


async def get_image(ctx):
    await ctx.send("**processing...**")
    try:
        image = await get_last_image(ctx)
    except IOError:
        return await ctx.send("Last image isn't valid.")
    if not image:
        return await ctx.send("Couldn't find valid image.")


async def send_image(ctx, image):
    with io.BytesIO() as f:
        try:
            image.save(f, format='png')
        except IOError:
            return await ctx.send("Image couldn't be saved.")
        f.seek(0)
        await ctx.send(file=discord.File(f, filename='image.png'))


class Filters:

    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def blur(self, ctx):
        image = await get_image(ctx)
        if not image:
            return

        image = image.filter(ImageFilter.BLUR)

        await send_image(ctx, image)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def invert(self, ctx):
        image = await get_image(ctx)
        if not image:
            return

        try:
            alpha = image.getchannel('A')
        except ValueError:
            alpha = None
        image = image.convert("RGB")
        image = ImageOps.invert(image)
        if alpha:
            image.putalpha(alpha)

        await send_image(ctx, image)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def flipv(self, ctx):
        image = await get_image(ctx)
        if not image:
            return

        image = ImageOps.flip(image)

        await send_image(ctx, image)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def fliph(self, ctx):
        image = await get_image(ctx)
        if not image:
            return

        image = ImageOps.mirror(image)
        await send_image(ctx, image)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def symm(self, ctx, side: str = "left"):
        side = side.lower()
        if side not in ('left', 'right', 'up', 'down'):
            return await ctx.send("Valid sides are 'left', 'right', 'up', and 'down'.")
        image = await get_image(ctx)
        if not image:
            return

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

        await send_image(ctx, image)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def posterize(self, ctx):
        image = await get_image(ctx)
        if not image:
            return

        try:
            alpha = image.getchannel('A')
        except ValueError:
            alpha = None
        image = image.convert("RGB")
        image = ImageOps.posterize(image, 2)
        if alpha:
            image.putalpha(alpha)

        await send_image(ctx, image)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def shrink(self, ctx, per: int = 5):
        if not (1 <= per <= 99):
            return await ctx.send("Percentage must be between 1 and 99")
        image = await get_image(ctx)
        if not image:
            return

        image = image.convert("RGBA")
        w = image.width * per // 100
        h = image.height * per // 100
        image.resize((w, h), resample=Image.LANCZOS)

        await send_image(ctx, image)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def glitch(self, ctx):
        image = await get_image(ctx)
        if not image:
            return

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

        await send_image(ctx, image)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def edges(self, ctx):
        image = await get_image(ctx)
        if not image:
            return

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

        await send_image(ctx, image)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def rotate(self, ctx, rotation: str = 'right'):
        rotation = rotation.lower()
        if rotation not in ('left', 'right'):
            return await ctx.send("Rotation must be 'left' or 'right'.")
        image = await get_image(ctx)
        if not image:
            return

        if rotation == 'left':
            image = image.transpose(Image.ROTATE_90)
        else:
            image = image.transpose(Image.ROTATE_270)

        await send_image(ctx, image)


def setup(bot):
    bot.add_cog(Filters(bot))
