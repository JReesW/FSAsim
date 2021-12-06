import pygame
import pygame.gfxdraw
import math

from algorithm import *
from uielements import *


backgroundColor = (220, 220, 220)
black = (0, 0, 0)
alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"


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
        self.selectedT = None
        self.arrow = None
        self.automaton = Automaton()

        self.drag = 0
        self.dragpos = (0, 0)
        self.mousepos = 0

    def handle_events(self, events):
        super().handle_events(events)

        pos = pygame.mouse.get_pos()
        self.mousepos = pos

        for event in events:
            # Check if the left mouse button is down
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                found = False
                # Check if the mouse click happened on a transition arrow
                for (s, v), (e, m) in self.automaton.transitions.items():
                    a = self.automaton.states[s]
                    b = self.automaton.states[e]
                    c, r = circle_from_3_points(a, mid := from_vector(a, b, m), b)

                    # Check if the arrow is curved
                    if c is not None:
                        s_angle, e_angle, rev = adjusted_angles(a, mid, b)
                        polygon = arc_to_polygon(c, r, 3, s_angle, e_angle, not rev)

                        for p in polygon:
                            if math.dist(p, pos) < 5 and self.arrow is None:
                                self.selected = None
                                self.selectedT = (s, v)
                                found = True
                                self.drag = 1
                                self.dragpos = pos
                                break
                    else:
                        self.automaton.transitions[(s, v)] = (e, (0, 0))
                        if point_to_segment(pos, a, b) < 7 and self.arrow is None:
                            self.selected = None
                            self.selectedT = (s, v)
                            found = True
                            self.drag = 1
                            self.dragpos = pos
                            break
                # Check if the mouse click happened inside a state circle
                for s in self.automaton.states:
                    if math.dist(self.automaton.states[s], pos) < 30:
                        # Check if an arrow connection is being made
                        if self.arrow is not None:
                            # Add a transition to the automaton
                            val = len([s for (s, v) in self.automaton.transitions if s == self.selected])
                            vector = (100, 0) if self.selected == s else (0, 0)
                            self.automaton.add_transition(self.selected, s, str(val), force_vector=vector)
                        else:
                            # Set the clicked on state as the currently selected state
                            self.selected = s
                            self.selectedT = None
                            # Set the dragging counter to 1, to initiate dragging
                            self.drag = 1
                            self.dragpos = pos
                        found = True
                # If no state was detected, deselect the currently selected object
                if not found:
                    self.selected = None
                    self.selectedT = None
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
                self.automaton.set_start(self.selected)
            # Change the bridging value of the transition
            elif event.type == pygame.KEYDOWN and self.selectedT is not None:
                if event.key == pygame.K_COMMA:
                    for a in alphabet:
                        if a not in self.selectedT[1].split(','):
                            e, m = self.automaton.transitions[self.selectedT]
                            self.automaton.remove_transition(self.selectedT)
                            new_v = self.selectedT[1] + f",{a}"
                            self.automaton.add_transition(self.selectedT[0], e, new_v, force_vector=m)
                            self.selectedT = (self.selectedT[0], new_v)
                            break
                elif event.key == pygame.K_BACKSPACE:
                    if len(spl := self.selectedT[1].split(',')) > 1:
                        e, m = self.automaton.transitions[self.selectedT]
                        self.automaton.remove_transition(self.selectedT)
                        new_v = ','.join(spl[:-1])
                        self.automaton.add_transition(self.selectedT[0], e, new_v, force_vector=m)
                        self.selectedT = (self.selectedT[0], new_v)
                else:
                    for a in alphabet:
                        if pygame.key.get_pressed()[getattr(pygame, f"K_{a}")]:
                            e, m = self.automaton.transitions[self.selectedT]
                            self.automaton.remove_transition(self.selectedT)
                            new_v = ','.join(self.selectedT[1].split(',')[:-1] + [a])
                            self.automaton.add_transition(self.selectedT[0], e, new_v, force_vector=m)
                            self.selectedT = (self.selectedT[0], new_v)
                            break

        # If 10 frames of holding the mouse down have passed,
        # and the mouse has moved more than 10 px from the starting position of the drag
        if self.drag == 10 and math.dist(pos, self.dragpos) > 10:
            # Set the dragging state to 11, where the actual dragging happens
            self.drag = 11
        elif self.drag == 11:
            # Move the state to where the mouse is positioned if the selected element is a state
            if self.selected is not None:
                hor = pos[0]
                ver = pos[1]
                without_self = [v for k, v in self.automaton.states.items() if k != self.selected]
                for (h, _) in without_self:
                    if abs(h - pos[0]) <= 5:
                        hor = h
                        break
                for (_, v) in without_self:
                    if abs(v - pos[1]) <= 5:
                        ver = v
                        break
                self.automaton.states[self.selected] = (hor, ver)
            # Otherwise, curve the selected arrow to the mouse position
            elif self.selectedT is not None:
                s, v = self.selectedT
                e, _ = self.automaton.transitions[self.selectedT]
                mid = vectorize(self.automaton.states[s], self.mousepos, self.automaton.states[e])
                self.automaton.transitions[(s, v)] = (e, mid)
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
        # Delete the currently selected transition when the delete key has been pressed
        elif pygame.key.get_pressed()[pygame.K_DELETE] and self.selectedT is not None:
            self.automaton.remove_transition(self.selectedT)
            self.selectedT = None
        else:
            self.arrow = None

    def render(self, surface):
        super().render(surface)

        # Show instructions on screen
        text(surface, "a - Toggle acceptor", (20, 670), regularfont, black)
        text(surface, "s - Set starting state", (20, 650), regularfont, black)
        text(surface, "left crtl + click - Create state", (20, 630), regularfont, black)
        text(surface, "shift + click - Create transition", (20, 610), regularfont, black)

        # Draw a circle for each state
        for s in self.automaton.states:
            color = (150, 150, 255) if s == self.selected else black
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
        for (s, v), (e, m) in self.automaton.transitions.items():
            start = self.automaton.states[s]
            end = self.automaton.states[e]
            mid = from_vector(start, end, m)

            color = (150, 150, 255) if (s, v) == self.selectedT else black
            path = draw_arc(surface, start, mid, end, color, return_path=True)

            # Arrow head
            center, radius = circle_from_3_points(start, mid, end)
            if center is not None:
                pathmid = len(path)//2
                angle = get_angle(path[pathmid-2], path[pathmid-1])
                adjusted_end = between(path[pathmid], path[pathmid-1], 0.5)
            else:
                angle = get_angle(start, end)
                adjusted_end = (end[0] + math.cos(angle) * 30, end[1] + math.sin(angle) * 30)
            arrow_l = (adjusted_end[0] + (math.cos(angle - 0.5) * 10),
                       adjusted_end[1] + (math.sin(angle - 0.5) * 10))
            arrow_r = (adjusted_end[0] + (math.cos(angle + 0.5) * 10),
                       adjusted_end[1] + (math.sin(angle + 0.5) * 10))

            pygame.draw.polygon(surface, color, [adjusted_end, arrow_l, arrow_r], width=0)

            # Arrow value
            if center is not None:
                textmid = between(path[len(path)//4], path[3*len(path)//4], 0.5)
            else:
                textmid = between(start, end, 0.5)
            txt, rect = regularfont.render(str(v), color)
            rectc = (textmid[0] - rect.width // 2, textmid[1] - rect.height // 2)
            pygame.draw.rect(surface, backgroundColor, pygame.Rect(rectc[0]-5, rectc[1]-5, rect.w+10, rect.h+10), 0)
            surface.blit(txt, rectc)

        # Draw an arrow from the selected circle to the mouse when holding shift
        if self.arrow is not None:
            # Similar to above
            x = self.automaton.states[self.selected][0]
            y = self.automaton.states[self.selected][1]
            angle = math.atan2(y - self.arrow[1], x - self.arrow[0])
            adjusted_start = (x - (math.cos(angle) * 30), y - (math.sin(angle) * 30))
            adjusted_end = (self.arrow[0] + (math.cos(angle) * 3), self.arrow[1] + (math.sin(angle) * 3))
            pygame.draw.line(surface, black, adjusted_start, adjusted_end, 3)

            # Arrow head
            arrow_l = (self.arrow[0] + (math.cos(angle - 0.5) * 10), self.arrow[1] + (math.sin(angle - 0.5) * 10))
            arrow_r = (self.arrow[0] + (math.cos(angle + 0.5) * 10), self.arrow[1] + (math.sin(angle + 0.5) * 10))
            pygame.draw.polygon(surface, black, [self.arrow, arrow_l, arrow_r], width=0)
