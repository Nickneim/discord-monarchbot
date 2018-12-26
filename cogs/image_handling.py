import discord
import io
from PIL import Image


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
        await ctx.send("Last image isn't valid.")
        return None
    if not image:
        await ctx.send("Couldn't find valid image.")
        return None
    return image


async def send_image(ctx, image):
    with io.BytesIO() as f:
        try:
            image.save(f, format='png')
        except IOError:
            return await ctx.send("Image couldn't be saved.")
        f.seek(0)
        await ctx.send(file=discord.File(f, filename='image.png'))


async def get_frame(ctx, frame):
    frame_path = "frames/" + frame + ".png"
    try:
        return Image.open(frame_path)
    except IOError:
        await ctx.send("Couldn't open frame.")
        return None
