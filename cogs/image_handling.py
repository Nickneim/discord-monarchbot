import discord
import io
from PIL import Image


def get_message_attachment(message, allowed_extensions=('.jpg', '.jpeg', '.png')):
    """Returns the first attachment from 'message' if it exists and it's a recognized image, otherwise returns None"""
    if message.attachments:
        attachment = message.attachments[0]
        if attachment.filename.lower().endswith(allowed_extensions):
            return attachment
    return None


def open_image(file):
    image = Image.open(file)
    try:
        exif = image._getexif()
    except AttributeError:
        orientation = None
    else:
        orientation = exif and exif.get(274)

    if image.width > 800 or image.height > 800:
        if image.width > image.height:
            width = 800
            height = image.height * 800 // image.width
        else:
            height = 800
            width = image.width * 800 // image.height
        image = image.resize((width, height), resample=Image.LANCZOS)

    if not orientation or orientation == 1:
        pass
    elif orientation == 2:
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
    elif orientation == 3:
        image = image.transpose(Image.ROTATE_180)
    elif orientation == 4:
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
    elif orientation == 5:
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        image = image.transpose(Image.ROTATE_270)
    elif orientation == 6:
        image = image.transpose(Image.ROTATE_270)
    elif orientation == 7:
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
        image = image.transpose(Image.ROTATE_270)
    elif orientation == 8:
        image = image.transpose(Image.ROTATE_90)
    return image


async def get_last_image(ctx, limit=100):
    """
    Returns the last image in the last 'limit' messages in the 'ctx' channel
    Raises IOError if last image isn't a valid image
    """
    attachment = get_message_attachment(ctx.message)
    if attachment:
        f = io.BytesIO()
        await attachment.save(f)
        return Image.open(f), ctx.message
    async for m in ctx.history(before=ctx.message, limit=limit):
        attachment = get_message_attachment(m)
        if attachment:
            f = io.BytesIO()
            await attachment.save(f)
            image = open_image(f)
            return image, m
    return None, None


async def get_image(ctx):
    await ctx.trigger_typing()
    try:
        image, message = await get_last_image(ctx)
    except IOError:
        await ctx.send("Last image isn't valid.")
        return None, None
    if not image:
        await ctx.send("Couldn't find valid image.")
        return None, None
    return image, message


async def send_image(ctx, image, image_message):
    with io.BytesIO() as f:
        try:
            image.save(f, format='png')
        except IOError:
            return await ctx.send("Image couldn't be saved.")
        f.seek(0)
        await ctx.send(file=discord.File(f, filename=ctx.invoked_with + '.png'))
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass
#    if image_message.author.id == ctx.me.id:
#        await image_message.delete()


async def get_frame(ctx, frame):
    frame_path = "frames/" + frame + ".png"
    try:
        return Image.open(frame_path)
    except IOError:
        await ctx.send("Couldn't open frame.")
        return None
