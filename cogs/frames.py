from discord.ext import commands
from PIL import Image, ImageDraw
from .image_handling import get_image, send_image, get_frame, get_template
from .filters import filters, advanced_filters
import logging


def apply_frame(image, frame):
    """Modifies image by resizing image to its size and pasting it"""
    frame = frame.resize(image.size, Image.LANCZOS)
    image.paste(frame, (0, 0), frame)
    return image


def apply_template(image, template, box):
    """Modifies template by inserting image in box part of template"""
    box_size = (box[2]-box[0], box[3]-box[1])
    image = image.resize(box_size, Image.LANCZOS)
    template_crop = template.crop(box)
    template.paste(image, box)
    # we also paste the template over itself so the image is behind it
    template.paste(template_crop, box, template_crop)
    return template


def detect_template(image):
    """
    Detect an area of transparency and return the coordinates of the rectangle.
    If the image has no alpha channel returns None.
    :param image: Image
    :return: An (int, int, int, int) tuple or None.
    """
    try:
        image = image.getchannel('A')
    except ValueError:
        return None
    x1 = image.width
    y1 = image.height
    x2 = 0
    y2 = 0
    i = 0
    for pixel in image.getdata():
        if pixel != 255:
            x = i % image.width
            y = i // image.width
            if x < x1:
                x1 = x
            if y < y1:
                y1 = y
            if x > x2:
                x2 = x
            if y > y2:
                y2 = y
        i += 1
    return x1, y1, x2, y2


class Frames(commands.Cog):

    try:
        with open("frames/frames.txt") as f:
            frames = f.read().split()
    except FileNotFoundError:
        logging.warning("Couldn't find frames/frames.txt.")
        frames = []

    try:
        templates = {}
        with open("frames/templates.txt") as f:
            for line in f:
                template, *coords = line.split()
                try:
                    x1, y1, x2, y2 = [int(x) for x in coords]
                except ValueError as e:
                    logging.warning(e)
                else:
                    templates[template] = (x1, y1, x2, y2)
    except FileNotFoundError:
        logging.warning("Couldn't find frames/templates.txt")
        templates = {}

    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=frames.copy())
    async def frame(self, ctx):
        """Paste the frame on the last image."""
        frame_name = ctx.invoked_with
        if frame_name == 'frame':
            return
        image, image_message = await get_image(ctx)
        if not image:
            return
        frame = get_frame(frame_name)
        if not frame:
            return await ctx.send(f"Couldn't open frame '{frame_name}'.")

        image = apply_frame(image, frame)

        await send_image(ctx, image, image_message)


    @commands.command(aliases=list(templates))
    async def template(self, ctx):
        """Insert the last image in the template."""
        template_name = ctx.invoked_with
        if template_name == 'template':
            return
        image, image_message = await get_image(ctx)
        if not image:
            return
        template = get_template(template_name)
        if not template:
            return await ctx.send(f"Couldn't open template '{template_name}'.")

        image = apply_template(image, template, Frames.templates[template_name])

        await send_image(ctx, image, image_message)


    @commands.command()
    async def addtestframe(self, ctx):
        """Download the last image and add it as a test frame."""
        test_image, image_message = await get_image(ctx)
        if not test_image:
            return

        try:
            test_image.convert("RGBA").save("frames/testframe.png")
        except IOError:
            return await ctx.send("Image couldn't be saved.")
        return await ctx.send("Changed test frame")


    @commands.command()
    async def addtesttemplate(self, ctx, x1: int, y1: int, x2: int, y2: int):
        """Download the last image and add it as a test template."""
        if x1 >= x2 or y1 >= y2 or x1 < 0 or y1 < 0:
            return await ctx.send("Those coordinates don't seem valid.")

        test_image, image_message = await get_image(ctx)
        if not test_image:
            return
        if test_image.width < x2 or test_image.height < y2:
            return await ctx.send("Box goes outside of template.")

        try:
            test_image.convert("RGBA").save("frames/testtemplate.png")
            Frames.templates['testtemplate'] = (x1, y1, x2, y2)
        except IOError:
            return await ctx.send("Image couldn't be saved.")
        return await ctx.send("Changed test template.")


    @commands.command(name="addframe")
    async def _add_frame(self, ctx, frame_name: str):
        """Download the last image and add it as a frame."""
        if self.bot.get_command(frame_name):
            return await ctx.send("There's already a command with that name.")
        frame, frame_message = await get_image(ctx)
        if not frame:
            return
        try:
            frame.convert('RGBA').save(f'frames/{frame_name}.png')
        except IOError:
            return await ctx.send("Couldn't save the image.")

        with open('frames/frames.txt', 'a') as f:
            f.write(f'\n{frame_name}')
        command = self.bot.get_command('frame')
        command.aliases.append(frame_name)
        self.frames.append(frame_name)
        self.bot.all_commands[frame_name] = command
        await ctx.send(f"Added frame {frame_name}.")


    @commands.command(name="removeframe")
    async def _remove_frame(self, ctx, frame_name: str):
        """Remove a frame."""
        if frame_name not in self.frames:
            return await ctx.send("There's no frame with that name.")
        self.frames.remove(frame_name)
        self.bot.remove_command(frame_name)
        with open('frames/frames.txt', 'w') as f:
            f.write('\n'.join(self.frames))
        await ctx.send(f"Removed frame {frame_name}.")


    @commands.command(name="removetemplate")
    async def _remove_template(self, ctx, template_name: str):
        """Remove a template."""
        if template_name not in self.templates:
            return await ctx.send("There's no template with that name.")
        del self.templates[template_name]
        self.bot.remove_command(template_name)
        with open('frames/templates.txt', 'w') as f:
            first_template = True
            for template, coordinates in self.templates.items():
                x1, y1, x2, y2 = coordinates
                if first_template:
                    f.write(f'{template} {x1} {y1} {x2} {y2}')
                    first_template = False
                else:
                    f.write(f'\n{template} {x1} {y1} {x2} {y2}')
        await ctx.send(f"Removed template {template_name}.")


    @commands.command(name="movetemplate")
    async def move_template(self, ctx, template_name: str, x1: int, y1: int, x2: int, y2: int):
        """Move a template's rectangle to (x1, y1, x2, y2)."""
        if template_name not in self.templates:
            return await ctx.send("There's no template with that name.")
        if x1 >= x2 or y1 >= y2 or x1 < 0 or y1 < 0:
            return await ctx.send("Those coordinates don't seem valid.")
        
        template = get_template(template_name)
        if not template:
            return await ctx.send(f"Couldn't open template '{template_name}'.")
        if template.width < x2 or template.height < y2:
            return await ctx.send("Box goes outside of template.")
        
        self.templates[template_name] = (x1, y1, x2, y2)

        with open('frames/templates.txt', 'w') as f:
            first_template = True
            for template, coordinates in self.templates.items():
                x1, y1, x2, y2 = coordinates
                if first_template:
                    f.write(f'{template} {x1} {y1} {x2} {y2}')
                    first_template = False
                else:
                    f.write(f'\n{template} {x1} {y1} {x2} {y2}')
        await ctx.send(f"Moved template box of {template_name} to ({x1}, {y1}, {x2}, {y2}).")
    

    @commands.command(name="addtemplate")
    async def _add_template(self, ctx, template_name: str, x1: int, y1: int, x2: int, y2: int):
        """Download the last image and add it as a template with rectangle (x1, y1, x2, y2)."""
        if self.bot.get_command(template_name):
            return await ctx.send("There's already a command with that name.")
        if x1 >= x2 or y1 >= y2 or x1 < 0 or y1 < 0:
            return await ctx.send("Those coordinates don't seem valid.")

        template, template_message = await get_image(ctx)
        if not template:
            return
        if template.width < x2 or template.height < y2:
            return await ctx.send("Box goes outside of template.")

        try:
            template.convert('RGBA').save(f'frames/{template_name}.png')
        except IOError:
            return await ctx.send("Couldn't save the image.")

        with open('frames/templates.txt', 'a') as f:
            f.write(f'\n{template_name} {x1} {y1} {x2} {y2}')
        command = self.bot.get_command('template')
        command.aliases.append(template_name)
        Frames.templates[template_name] = (x1, y1, x2, y2)
        self.bot.all_commands[template_name] = command
        await ctx.send(f"Added template {template_name} with box ({x1}, {y1}, {x2}, {y2}).")


    @commands.command()
    async def check_template(self, ctx, template_name, x1: int = None, y1: int = None, x2: int = None, y2: int = None):
        """Draw a rectangle in a template. Rectangle defaults to the template's rectangle."""
        if template_name not in Frames.templates or template_name == 'template':
            return await ctx.send("There's no template with that name.")
        if x1 is not None:
            if y2 is None:
                return await ctx.send("Coordinates are partial and not valid.")
            elif x1 >= x2 or y1 >= y2 or x1 < 0 or y1 < 0:
                return await ctx.send("Those coordinates don't seem valid.")
        else:
            x1, y1, x2, y2 = Frames.templates[template_name]

        template = get_template(template_name)
        if not template:
            return await ctx.send(f"Couldn't open template '{template_name}'.")

        draw = ImageDraw.Draw(template)
        draw.rectangle((x1, y1, x2, y2), outline=(255, 0, 0, 255), width=2)

        await send_image(ctx, template, ctx.message)


    @commands.command(name="detecttemplate")
    async def _detect_template(self, ctx):
        """Detects a transparent rectangle for the last image as a template and draws it."""
        image, image_message = await get_image(ctx)
        if not image:
            return
        coords = detect_template(image)
        if coords is None:
            return await ctx.send("That image doesn't have an alpha channel.")
        draw = ImageDraw.Draw(image)
        draw.rectangle(coords, outline=(255, 0, 0, 255), width=2)
        await send_image(ctx, image, ctx.message)
        await ctx.send(str(coords))


    @commands.command()
    async def pipe(self, ctx, *, pipe_string: str):
        """Performs a series of frames and templates on an image"""
        command_list = pipe_string.split()
        advanced_filter_command = None
        for command_name in command_list:
            if advanced_filter_command:
                if advanced_filter_command == 'symm':
                    side = command_name.lower()
                    if side not in ('left', 'right', 'top', 'bottom'):
                        return await ctx.send("Valid sides are 'left', 'right', 'top', and 'bottom'.")
                elif advanced_filter_command == 'shrink':
                    try:
                        per = int(command_name)
                    except ValueError:
                        return await ctx.send("The percentage to shrink must be a number.")
                    if not (1 <= per <= 99):
                        return await ctx.send("Percentage must be between 1 and 99.")
                elif advanced_filter_command == 'rotate':
                    rotation = command_name.lower()
                    if rotation not in ('left', 'right'):
                        return await ctx.send("Rotation must be 'left' or 'right'.")
                advanced_filter_command = None
            elif command_name in Frames.frames:
                continue
            elif command_name in Frames.templates:
                continue
            elif command_name in filters:
                continue
            elif command_name in advanced_filters:
                advanced_filter_command = command_name
                continue
            else:
                return await ctx.send(f"{command_name} is not a frame or a template or a filter.")
        image, image_message = await get_image(ctx)
        if not image:
            return

        advanced_filter_command = None
        for command_name in command_list:
            if advanced_filter_command:
                if advanced_filter_command == 'symm':
                    side = command_name.lower()
                    image = advanced_filters['symm'](image, side)
                elif advanced_filter_command == 'shrink':
                    per = int(command_name)
                    image = advanced_filters['shrink'](image, per)
                elif advanced_filter_command == 'rotate':
                    rotation = command_name .lower()
                    image = advanced_filters['rotate'](image, rotation)
                advanced_filter_command = None
            elif command_name in Frames.frames:
                frame = get_frame(command_name)
                if not frame:
                    return await ctx.send(f"Couldn't open frame '{frame_name}'.")
                image = apply_frame(image, frame)
            elif command_name in Frames.templates:
                template = get_template(command_name)
                if not template:
                    return await ctx.send(f"Couldn't open template '{template_name}'.")
                image = apply_template(image, template, Frames.templates[command_name])
            elif command_name in filters:
                image = filters[command_name](image)
            elif command_name in advanced_filters:
                advanced_filter_command = command_name
        if advanced_filter_command:
            image = advanced_filters[command_name](image)
        await send_image(ctx, image, image_message)




def setup(client):
    client.add_cog(Frames(client))
