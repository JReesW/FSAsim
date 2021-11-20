import pygame
import scenes

# This module contains elements used by the UI (buttons, etc.)


pygame.freetype.init()
smallerfont = pygame.freetype.SysFont('Mono', 13)
timefont = pygame.freetype.SysFont('Mono', 17)
regularfont = pygame.freetype.SysFont('Mono', 20)
biggerfont = pygame.freetype.SysFont('Mono', 40)


# Add text to a surface
def text(surface, message, pos, font, color):
    """
    Draws text to a given surface

    :param surface: the surface to draw to
    :param message: the text to draw
    :param pos: the position of the drawing on the surface (topleft)
    :param font: the font to draw the text with
    :param color: the color of the text
    """
    t, _ = font.render(message, color)
    surface.blit(t, pos)


# Class representing a clickable button
class Button:
    """
    A button that can be pressed and then executes a function on the given scene
    """
    def __init__(self, rect, txt, funcs, args, scene):
        self.rect = rect
        self.text = txt
        self.color = (220, 220, 220)
        self.bordercolor = (206, 30, 66)
        self.textcolor = (20, 20, 20)
        self.funcs = funcs
        self.args = args
        self.scene = scene

    # Change color on hover
    def hover(self, mousepos):
        """
        Changes the color of the button when the mouse is positioned on top of it

        :param mousepos: the position of the mouse
        """
        if self.rect.collidepoint(mousepos):
            # Become darker when mouse is hovering over button
            self.color = tuple([self.color[i] - 2 if self.color[i] > 200 else self.color[i] for i in range(3)])
        else:
            # Become lighter when no mouse is hovering over button
            self.color = tuple([self.color[i] + 2 if self.color[i] < 220 else self.color[i] for i in range(3)])

    # Draw the button
    def render(self):
        """
        Return a surface containing the rendered button

        :return: the button surface
        """
        surface = pygame.Surface(self.rect.size)

        # Background and border
        pygame.draw.rect(surface, self.color, pygame.Rect(1, 1, self.rect.width - 2, self.rect.height - 2), 0)
        pygame.draw.rect(surface, self.bordercolor, pygame.Rect(0, 0, self.rect.width - 1, self.rect.height - 1), 2)

        # Text
        txt, rect = regularfont.render(self.text, self.textcolor)
        surface.blit(txt, (surface.get_width() // 2 - rect.width // 2, 10))

        return surface

    def handle_events(self, events, overridemouse=None):
        mousepos = pygame.mouse.get_pos()
        if overridemouse is not None:
            mousepos = overridemouse

        self.hover(mousepos)

        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                if self.rect.collidepoint(mousepos):
                    for func in self.funcs:
                        self.scene.execute(func, self.args)


class TextBox:
    """
    A text box which can be activated by being clicked on, after which text can be written into it
    """
    def __init__(self, rect):
        self.rect = rect
        self.text = ""
        self.active = False
        self.buffer = 0

    def get_text(self):
        """
        Return the text written into this text box

        :return: the text
        """
        return self.text

    def clear_text(self):
        """
        Clear the text written in this text box

        :return: void
        """
        self.text = ""

    def set_text(self, s):
        """
        Force change the input to the given string

        :param s: a string
        :return: void
        """
        self.text = s

    def render(self):
        """
        Return a surface containing the rendered text box

        :return: the text box surface
        """
        surface = pygame.Surface(self.rect.size)

        # Background and border
        bordercolor = (180, 140, 255) if self.active else (20, 20, 20)
        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(1, 1, self.rect.width - 2, self.rect.height - 2), 0)
        pygame.draw.rect(surface, bordercolor, pygame.Rect(0, 0, self.rect.width - 1, self.rect.height - 1), 2)

        # Text
        text(surface, self.text, (10, 10), regularfont, (0, 0, 0))

        return surface

    def handle_events(self, events, overridemouse=None):
        mousepos = pygame.mouse.get_pos()
        if overridemouse is not None:
            mousepos = overridemouse

        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                self.active = self.rect.collidepoint(mousepos)

            if event.type == pygame.KEYDOWN:
                if self.active:
                    if event.key == pygame.K_RETURN:
                        self.active = False
                    elif event.key != pygame.K_BACKSPACE:
                        self.text += event.unicode

        if pygame.key.get_pressed()[pygame.K_BACKSPACE] and self.active:
            if self.buffer == 0:
                self.text = self.text[:-1]
                self.buffer = 1
            else:
                self.buffer += 1
                if self.buffer > 40 and self.buffer % 3 == 0:
                    self.text = self.text[:-1]
        else:
            self.buffer = 0


# class Table:
#     """
#     A table which can store data entries and displays them.
#     Has scrolling features and the ability to select entries and view more info.
#     """
#     def __init__(self, rect, scene):
#         self.rect = rect
#         self.entries = {}
#         self.scroll = 0
#         self.selected = None
#         self.selectable = True
#         self.scene = scene
#
#     def set_entries(self, entries):
#         """
#         Add a given list of entries to the table
#
#         :param entries: a list of entries
#         """
#         self.entries = entries
#
#     def clear(self):
#         """
#         Removes all entries from the table
#         """
#         self.entries = []
#
#     def render(self):
#         """
#         Return a surface containing the rendered table
#
#         :return: the table surface
#         """
#         surface = pygame.Surface(self.rect.size)
#         bordercolor = (180, 180, 180)
#         pygame.draw.rect(surface, (140, 140, 140), pygame.Rect(1, 1, self.rect.width - 2, self.rect.height - 2), 0)
#
#         # Entries
#         for i in range(max(5, len(self.entries))):
#             color = (220, 220, 220) if i % 2 == 0 else (200, 200, 200)
#             rect = pygame.Rect(0, (i * 100) - self.scroll, self.rect.width - 25, 100)
#             pygame.draw.rect(surface, color, rect, 0)
#
#             if i < len(self.entries):
#                 text(surface, f"oorzaak:    {self.entries[i][0]}", (10, rect.top + 10), smallerfont, (0, 0, 0))
#                 text(surface, f"geo:        {self.entries[i][1]}", (10, rect.top + 27), smallerfont, (0, 0, 0))
#                 text(surface, f"techniek:   {self.entries[i][2]}", (10, rect.top + 44), smallerfont, (0, 0, 0))
#                 text(surface, f"prioriteit: {self.entries[i][3]}", (10, rect.top + 61), smallerfont, (0, 0, 0))
#                 text(surface, f"Meldtijd:   {self.entries[i][4]}", (10, rect.top + 78), smallerfont, (0, 0, 0))
#
#                 text(surface, "Duur:", (200, rect.top + 15), regularfont, (0, 0, 0))
#                 if (mins := int(self.entries[i][5])) > 60:
#                     time = f"{mins//60}h {mins % 60}m"
#                 else:
#                     time = f"{mins}m"
#                 #time = f"{int(self.entries[i][5])}m" if int(self.entries[i][5]) < 60 else int(self.entries[i][5])
#                 text(surface, time, (200, rect.top + 45), timefont, (0, 0, 0))
#
#         # Scroll bar
#         barheight = min(1.0, (self.rect.height / 100) / max(1, len(self.entries)))  # height of the bar
#         bartop = self.scroll / (max(1, len(self.entries)) * 100)  # distance from top
#         scrollrect = pygame.Rect(self.rect.width - 20, 5 + (self.rect.height * bartop), 15, (self.rect.height - 10) * barheight - 3)
#         pygame.draw.rect(surface, (250, 250, 250), scrollrect, 0)
#
#         pygame.draw.rect(surface, bordercolor, pygame.Rect(0, 0, self.rect.width - 1, self.rect.height - 1), 2)
#         pygame.draw.line(surface, bordercolor, (self.rect.width - 25, 0), (self.rect.width - 25, self.rect.height), 2)
#
#         return surface
#
#     def handle_events(self, events, overridemouse=None):
#         mousepos = pygame.mouse.get_pos()
#         if overridemouse is not None:
#             mousepos = overridemouse
#
#         for event in events:
#             # Check if the mouse is being used while positioned over the table
#             if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(mousepos):
#                 # Scrolling upwards
#                 if event.button == 4 and self.scroll > 0:
#                     self.scroll -= 6
#                     self.scroll = max(self.scroll, 0)
#                 # Scrolling downwards
#                 elif event.button == 5 and self.scroll + self.rect.height < 100 * len(self.entries):
#                     self.scroll += 6
#                     self.scroll = min(self.scroll, 100 * len(self.entries) - self.rect.height)
#                 # Clicking with the rightmouse button
#                 elif event.button == 1:
#                     # Check if the mouse is positioned over the scroll bar
#                     if pygame.Rect(self.rect.right - 25, self.rect.top, 25, self.rect.height).collidepoint(mousepos):
#                         # Calculate how far the list must scroll so that the middle of the scroll bar lands
#                         # where the mouse was clicked. The scroll bar cannot exceed its boundaries.
#                         barhalf = (min(1.0, 5 / max(1, len(self.entries))) * self.rect.height) / 2
#                         relativemouse = min(max(0, mousepos[1] - self.rect.top - barhalf - 5), self.rect.height - (2 * barhalf))
#                         span = abs((barhalf - 5) - (self.rect.height - barhalf - 5))
#                         self.scroll = int((relativemouse / max(1, span)) * max(0, (len(self.entries) * 100) - self.rect.height))
