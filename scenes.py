import pygame
import math

from algorithm import *
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
        self.selected = None
        self.arrow = None
        self.automaton = Automaton()

        self.drag = 0

    def handle_events(self, events):
        super().handle_events(events)

        pos = pygame.mouse.get_pos()

        for event in events:
            # Check if the left mouse button is down
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                found = False
                # Check if the mouse click happened inside a state circle
                for s in self.automaton.states:
                    if math.dist(self.automaton.states[s], pos) < 30:
                        # Check if an arrow connection is being made
                        if self.arrow is not None:
                            # Add a transition to the automaton
                            val = len([s for (s, v) in self.automaton.transitions if s == self.selected])
                            self.automaton.add_transition(self.selected, s, str(val))
                        else:
                            # Set the clicked on state as the currently selected state
                            self.selected = s
                            # Set the dragging counter to 1, to initiate dragging
                            self.drag = 1
                        found = True
                # If no state was detected, deselect the currently selected object
                if not found:
                    self.selected = None
                    # If the left CRTL button is being held, create a new state
                    if pygame.key.get_pressed()[pygame.K_LCTRL]:
                        i = 0
                        while (lbl := f"q{i}") in self.automaton.states.keys():
                            i += 1
                        self.automaton.states[lbl] = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                # Stop the dragging state when the left mouse button is released
                self.drag = 0
            # Check if the 'a' key was pressed, and if so, toggle the selected state being an acceptor
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_a and self.selected is not None:
                if self.selected not in self.automaton.acceptors:
                    self.automaton.add_acceptor(self.selected)
                else:
                    self.automaton.remove_acceptor(self.selected)
            # Check if the 's' key was pressed, and if so, set the selected state to be the starting state
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_s and self.selected is not None:
                self.automaton.start = self.selected

        # If 10 frames of holding the mouse down have passed,
        # and the mouse has moved more than 10 px from the state center
        if self.drag == 10 and math.dist(pos, self.automaton.states[self.selected]) > 10:
            # Set the dragging state to 11, where the actual dragging happens
            self.drag = 11
        elif self.drag == 11:
            # Move the state to where the mouse is positioned
            self.automaton.states[self.selected] = pos
        elif 0 < self.drag < 10:
            self.drag += 1

        # Deselect the currently selected object by pressing the escape key
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            self.selected = None
        # Create an arrow from the currently selected state to the mouse pointer
        elif pygame.key.get_pressed()[pygame.K_LSHIFT] and self.selected is not None:
            self.arrow = pygame.mouse.get_pos()
        # Delete the currently selected state when the delete key has been pressed
        elif pygame.key.get_pressed()[pygame.K_DELETE] and self.selected is not None:
            self.automaton.remove_state(self.selected)
            self.selected = None
        else:
            self.arrow = None

        if pygame.key.get_pressed()[pygame.K_e]:
            self.switch(StateSettingsScene, [self])

    def render(self, surface):
        super().render(surface)

        text(surface, "a - Toggle acceptor", (20, 670), regularfont, (0, 0, 0))
        text(surface, "s - Set starting state", (20, 650), regularfont, (0, 0, 0))
        text(surface, "left crtl + click - Create state", (20, 630), regularfont, (0, 0, 0))
        text(surface, "shift + click - Create transition", (20, 610), regularfont, (0, 0, 0))

        # Draw a circle for each state
        for s in self.automaton.states:
            color = (150, 150, 255) if s == self.selected else (0, 0, 0)
            pygame.draw.circle(surface, color, self.automaton.states[s], 30, 3)
            # Draw another smaller circle if the state is an accepting state
            if s in self.automaton.acceptors:
                pygame.draw.circle(surface, color, self.automaton.states[s], 22, 3)
            # Draw two lines when the state is the starting state
            if s == self.automaton.start:
                startpos = (self.automaton.states[s][0] - 30, self.automaton.states[s][1])
                endpos1 = (self.automaton.states[s][0] - 40, self.automaton.states[s][1] + 10)
                endpos2 = (self.automaton.states[s][0] - 40, self.automaton.states[s][1] - 10)
                pygame.draw.line(surface, color, startpos, endpos1, 3)
                pygame.draw.line(surface, color, startpos, endpos2, 3)

        # Draw an arrow for each transition
        for (s, v), e in self.automaton.transitions.items():
            # Get the points of the two connected states
            x1 = self.automaton.states[s][0]
            y1 = self.automaton.states[s][1]
            x2 = self.automaton.states[e][0]
            y2 = self.automaton.states[e][1]
            # Calculate the angle between them and move the starting and ending points to the edge of the states
            angle = math.atan2(y1 - y2, x1 - x2)
            adjusted_start = (x1 - (math.cos(angle) * 30), y1 - (math.sin(angle) * 30))
            adjusted_end = (x2 + (math.cos(angle) * 30), y2 + (math.sin(angle) * 30))
            pygame.draw.line(surface, (0, 0, 0), adjusted_start, adjusted_end, 3)

            # Arrow head
            arrow_l = (adjusted_end[0] + (math.cos(angle - 0.5) * 10), adjusted_end[1] + (math.sin(angle - 0.5) * 10))
            arrow_r = (adjusted_end[0] + (math.cos(angle + 0.5) * 10), adjusted_end[1] + (math.sin(angle + 0.5) * 10))
            pygame.draw.polygon(surface, (0, 0, 0), [adjusted_end, arrow_l, arrow_r], width=0)

        # Draw an arrow from the selected circle to the mouse when holding shift
        if self.arrow is not None:
            # Similar to above
            x = self.automaton.states[self.selected][0]
            y = self.automaton.states[self.selected][1]
            angle = math.atan2(y - self.arrow[1], x - self.arrow[0])
            adjusted_start = (x - (math.cos(angle) * 30), y - (math.sin(angle) * 30))
            adjusted_end = (self.arrow[0] + (math.cos(angle) * 3), self.arrow[1] + (math.sin(angle) * 3))
            pygame.draw.line(surface, (0, 0, 0), adjusted_start, adjusted_end, 3)

            # Arrow head
            arrow_l = (self.arrow[0] + (math.cos(angle - 0.5) * 10), self.arrow[1] + (math.sin(angle - 0.5) * 10))
            arrow_r = (self.arrow[0] + (math.cos(angle + 0.5) * 10), self.arrow[1] + (math.sin(angle + 0.5) * 10))
            pygame.draw.polygon(surface, (0, 0, 0), [self.arrow, arrow_l, arrow_r], width=0)

        pygame.draw.circle(surface, (0, 0, 0), (100, 100), 30, 3)
        pygame.draw.circle(surface, (0, 0, 0), (100, 400), 30, 3)
        # pygame.draw.arc(surface, (0, 0, 0))


class StateSettingsScene(Scene):
    def __init__(self, background):
        super().__init__()
        self.background = background

    def handle_events(self, events):
        pass

    def render(self, surface):
        self.background.render(surface)
        sr = pygame.display.get_surface().get_rect()
        veil = pygame.Surface(sr.size)
        pygame.draw.rect(veil, (20, 20, 20), surface.get_rect())
        veil.set_alpha(150)
        surface.blit(veil, (0, 0))
