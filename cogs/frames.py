from discord.ext import commands
from PIL import Image
from .image_handling import get_image, send_image, get_frame


def frame_on_image(frame, image):
    """Modifies image by resizing image to its size and pasting it"""
    frame = frame.resize(image.size, Image.LANCZOS)
    image.paste(frame, (0, 0), frame)


def image_inside_frame(image, frame, box):
    """Modifies frame by inserting image in box part of frame"""
    box_size = (box[2]-box[0], box[3]-box[1])
    image = image.resize(box_size, Image.LANCZOS)
    frame_crop = frame.crop(box)
    frame.paste(image, box)
    frame.paste(frame_crop, box, frame_crop)


class Frames:

    frames = ['ac', 'acab', 'al', 'amouranth', 'bann', 'beatles', 'bjork', 'blond',
              'blood', 'bop', 'brazzers', 'bulge', 'can', 'cat', 'cj1', 'cnid',
              'coil1', 'coil2', 'comic1', 'comic2', 'commie', 'conway', 'cooper1', 'cooper2', 'cowboy',
              'crosshair', 'cry', 'dab1', 'damn', 'dg', 'dick', 'die', 'dole', 'elon', 'forklift', 'fuckyou',
              'funwaa', 'gag', 'garf2', 'garf3', 'garf4', 'garf5', 'gay',
              'general', 'grinch', 'hhill', 'hillary', 'idub1', 'idub2', 'idub3', 'idub4', 'idub5', 'idub6',
              'ifunny', 'jempy', 'jf1', 'jf2', 'kim', 'knife', 'knuckle', 'liberal', 'lilpeep', 'lilpump',
              'lrd', 'lynch', 'madvillainy', 'mark', 'meme1', 'nmh',
              'obama2', 'parental', 'pickle', 'piss', 'preg', 'qotsa', 'rh', 'sam',
              'sb', 'shapiro', 'shrek', 'shutterstock', 'sketch', 'socks', 'sonic', 'spaghett',
              'spongebob', 'ss', 'swans', 'swear1', 'swear2', 'sy', 'television', 'testframe', 'tmay',
              'tp', 'trigger', 'trump', 'unlock', 'vine1', 'vu', 'warcrime', 'wasted', 'wish',
              'wtc2', 'zucc', 'zucc1', 'zucc2', 'zucc3', 'zucc4']

    templates = {
        # name: (left, top, right, bottom),
        'altright': (9, 195, 897, 687),
        'buzzfeed': (16, 86, 587, 416),
        'calvin': (0, 0, 300, 28),
        'clash': (59, 0, 342, 225),
        'cruz': (75, 26, 459, 344),
        'funeral': (46, 55, 356, 183),
        'garf1': (35, 48, 264, 238),
        'gccx1': (0, 49, 640, 431),
        'gccx2': (0, 19, 259, 173),
        'jones': (503, 0, 1187, 717),
        'mars': (204, 0, 534, 246),
        'memri': (28, 9, 661, 297),
        'n64': (119, 67, 377, 325),
        'nut': (0, 87, 714, 633),
        'obama1': (7, 90, 448, 378),
        'picard': (0, 0, 600, 307),
        'porn': (15, 82, 776, 502),
        'rapper': (0, 66, 522, 510),
        'science': (0, 147, 1000, 833),
        'son': (0, 86, 569, 613),
        'wedding': (158, 12, 394, 257),
        'wtc1': (0, 0, 300, 238),
    }

    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(aliases=frames)
    async def frame(self, ctx):
        frame_name = ctx.invoked_with
        if frame_name == 'frame':
            return
        image, image_message = await get_image(ctx)
        if not image:
            return
        frame = await get_frame(ctx, frame_name)
        if not frame:
            return

        frame_on_image(frame, image)

        await send_image(ctx, image, image_message)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(aliases=list(templates))
    async def template(self, ctx):
        frame_name = ctx.invoked_with
        if frame_name == 'template':
            return
        image, image_message = await get_image(ctx)
        if not image:
            return
        frame = await get_frame(ctx, frame_name)
        if not frame:
            return

        image_inside_frame(image, frame, Frames.templates[frame_name])

        await send_image(ctx, frame, image_message)

    @commands.cooldown(1, 5, commands.BucketType.default)
    @commands.command()
    async def addtestframe(self, ctx):
        test_image, image_message = await get_image(ctx)
        if not test_image:
            return

        try:
            test_image.convert("RGBA").save("frames/testframe.png")
        except IOError:
            return await ctx.send("Image couldn't be saved.")
        return await ctx.send("Changed test frame")


def setup(client):
    client.add_cog(Frames(client))
