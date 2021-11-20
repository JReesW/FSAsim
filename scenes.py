import pygame
import math
from uielements import *


backgroundColor = (220, 220, 220)


# Main Classes:

# Controls the scenes and handles transitions between them
class Director:
    """
    Directs which scene is active and sends handle_events(), update(), and render() to the active scene
    """

    def __init__(self):
        """
        Initialize the director, starting with a menu scene
        """
        self.scene = None
        self.switch(SimulateScene())

    # Takes the new scene as its current scene and adds itself to it
    def switch(self, scene):
        """
        Switch active scene to the given scene

        :param scene: the new active scene
        """
        self.scene = scene
        self.scene.director = self


# Scene base class
class Scene:
    """
    The basic scene class
    """

    def __init__(self):
        """
        Initialize the scene, declaring the director and ui attributes
        """
        self.director = None
        self.ui = {}

    def handle_events(self, events):
        """
        Handle events like keyboard or mouse input given via the events param

        :param events: a list of pygame events
        """
        for element in self.ui.values():
            element.handle_events(events)

    def update(self):
        """
        Update the state of this scene
        """
        pass

    def render(self, surface):
        """
        Draw to the given surface

        :param surface: the surface to draw to
        """
        # Clear screen
        surface.fill(backgroundColor)

        # UI element rendering
        for element in self.ui.values():
            surface.blit(element.render(), element.rect.topleft)

    def switch(self, scene, args=None):
        """
        Calls for its director to switch to the given scene. Applies the args to the scene

        :param scene: the scene to switch to
        :param args: possible arguments for the switch initialization
        """
        args = [] if args is None else args
        self.director.switch(scene(*args))

    @staticmethod
    def execute(func, args):
        """
        Execute a given function and pass args as arguments
        Can be called by buttons to call class methods

        :param func: the function to execute
        :param args: the arguments to pass to the function
        """
        func(*args)


"""
From this point forward there will be no docstrings for handle_events(), update(), and render()
as they have already been described above
"""


class MenuScene(Scene):
    """
    The main menu scene
    """
    def __init__(self):
        super().__init__()
        self.ui = {}

    def handle_events(self, events):
        super().handle_events(events)

    def render(self, surface):
        super().render(surface)


class SimulateScene(Scene):
    """
    The scene where the user can enter a finite state automata for simulation
    """
    def __init__(self):
        super().__init__()
        self.ui = {
        }
        self.states = []
        self.selected = None
        self.arrow = None

    def handle_events(self, events):
        super().handle_events(events)

        self.arrow = None

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                found = False
                for c, s in enumerate(self.states):
                    if math.dist(s, pos) < 30:
                        self.selected = c
                        found = True
                if not found:
                    self.states.append(pygame.mouse.get_pos())

        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            self.selected = None
        elif pygame.key.get_pressed()[pygame.K_LSHIFT] and self.selected is not None:
            self.arrow = pygame.mouse.get_pos()

    def render(self, surface):
        super().render(surface)
        for c, s in enumerate(self.states):
            color = (150, 150, 255) if c == self.selected else (0, 0, 0)
            pygame.draw.circle(surface, color, s, 30, 3)

        if self.arrow is not None:
            # For making the arrow start from the edge of a circle, rather than the center
            x = self.states[self.selected][0]
            y = self.states[self.selected][1]
            angle = math.atan2(y - self.arrow[1], x - self.arrow[0])
            adjusted_start = (x - (math.cos(angle) * 30), y - (math.sin(angle) * 30))
            adjusted_end = (self.arrow[0] + (math.cos(angle) * 3), self.arrow[1] + (math.sin(angle) * 3))
            pygame.draw.line(surface, (0, 0, 0), adjusted_start, adjusted_end, 3)

            # Arrow head
            arrow_l = (self.arrow[0] + (math.cos(angle - 0.5) * 10), self.arrow[1] + (math.sin(angle - 0.5) * 10))
            arrow_r = (self.arrow[0] + (math.cos(angle + 0.5) * 10), self.arrow[1] + (math.sin(angle + 0.5) * 10))
            pygame.draw.polygon(surface, (0, 0, 0), [self.arrow, arrow_l, arrow_r], width=0)
