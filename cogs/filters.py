from PIL import Image, ImageFilter, ImageOps, ImageEnhance, ImageDraw, ImageFont
from discord.ext import commands
from .image_handling import get_image, send_image


def wrap_line(draw, font, line, width):
    # check if line already fits
    size = draw.textsize(line, font)
    if size[0] < width:
        return line, ""
    space = line.find(' ', 0)
    if space == -1:  # There's only one word
        return line, ""
    # the first 'previous space', is the first space
    prev_space = space
    while space != -1:
        size = draw.textsize(line[:space], font=font)
        if size[0] >= width:
            return line[:prev_space], line[prev_space + 1:]
        prev_space = space
        space = line.find(' ', prev_space + 1)
    return line[:prev_space], line[prev_space + 1:]


def wrap_text(draw, font, text, width):
    result = ""
    for remaining_line in text.splitlines():
        if not remaining_line:
            result += "\n"
        while remaining_line:
            line, remaining_line = wrap_line(draw, font, remaining_line, width)
            result += line
            result += '\n'
    return result.rstrip()


class Filters:

    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def blur(self, ctx):
        image, image_message = await get_image(ctx)
        if not image:
            return

        image = image.filter(ImageFilter.BLUR)

        await send_image(ctx, image, image_message)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def invert(self, ctx):
        image, image_message = await get_image(ctx)
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

        await send_image(ctx, image, image_message)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def flipv(self, ctx):
        image, image_message = await get_image(ctx)
        if not image:
            return

        image = ImageOps.flip(image)

        await send_image(ctx, image, image_message)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def fliph(self, ctx):
        image, image_message = await get_image(ctx)
        if not image:
            return

        image = ImageOps.mirror(image)
        await send_image(ctx, image, image_message)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def symm(self, ctx, side: str = "left"):
        side = side.lower()
        if side not in ('left', 'right', 'up', 'down'):
            return await ctx.send("Valid sides are 'left', 'right', 'up', and 'down'.")
        image, image_message = await get_image(ctx)
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

        await send_image(ctx, image, image_message)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def posterize(self, ctx):
        image, image_message = await get_image(ctx)
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

        await send_image(ctx, image, image_message)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def shrink(self, ctx, per: int = 5):
        if not (1 <= per <= 99):
            return await ctx.send("Percentage must be between 1 and 99")
        image, image_message = await get_image(ctx)
        if not image:
            return

        image = image.convert("RGBA")
        w = image.width * per // 100
        h = image.height * per // 100
        image.resize((w, h), resample=Image.LANCZOS)

        await send_image(ctx, image, image_message)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def glitch(self, ctx):
        image, image_message = await get_image(ctx)
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

        await send_image(ctx, image, image_message)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def edges(self, ctx):
        image, image_message = await get_image(ctx)
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

        await send_image(ctx, image, image_message)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def rotate(self, ctx, rotation: str = 'right'):
        rotation = rotation.lower()
        if rotation not in ('left', 'right'):
            return await ctx.send("Rotation must be 'left' or 'right'.")
        image, image_message = await get_image(ctx)
        if not image:
            return

        if rotation == 'left':
            image = image.transpose(Image.ROTATE_90)
        else:
            image = image.transpose(Image.ROTATE_270)

        await send_image(ctx, image, image_message)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def impact(self, ctx, *, text: str):
        image, image_message = await get_image(ctx)
        if not image:
            return

        font_size = image.width // 10
        try:
            font = ImageFont.truetype(font="fonts/impact.ttf", size=font_size)
        except IOError:
            return await ctx.send("Couldn't open the font.")
        draw = ImageDraw.Draw(image)
        text = wrap_text(draw, font, text, image.width)
        text_size = draw.textsize(text, font)
        x, y = ((image.width - text_size[0]) // 2, 3)

        radius = font_size // 20
        draw.text((x-radius, y-radius), text, font=font, fill=(0, 0, 0, 255), align="center")
        draw.text((x-radius, y+radius), text, font=font, fill=(0, 0, 0, 255), align="center")
        draw.text((x+radius, y-radius), text, font=font, fill=(0, 0, 0, 255), align="center")
        draw.text((x+radius, y+radius), text, font=font, fill=(0, 0, 0, 255), align="center")

        draw.text((x, y), text, font=font, align="center")

        await send_image(ctx, image, image_message)


def setup(bot):
    bot.add_cog(Filters(bot))
