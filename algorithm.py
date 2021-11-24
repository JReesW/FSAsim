import math

import pygame
import pygame.gfxdraw
from pygame import Rect
from typing import Tuple


class StartError(Exception):
    pass


class AcceptError(Exception):
    pass


class Automaton:
    def __init__(self):
        self.states = {}
        self.transitions = {}
        self.acceptors = []
        self.start = None
        self.current = None

    def add_transition(self, start, end, via):
        self.transitions[(start, via)] = end

    def add_state(self, label, pos):
        self.states[label] = pos

    def remove_state(self, label):
        del self.states[label]

        self.transitions = {(s, v): e for (s, v), e in self.transitions.items() if label not in [s, e]}
        self.acceptors = [a for a in self.acceptors if a != label]
        if self.start == label:
            self.start = None

    def add_acceptor(self, label):
        self.acceptors.append(label)

    def remove_acceptor(self, label):
        self.acceptors.remove(label)

    def transition(self, label, letter):
        if (label, letter) in self.transitions:
            return self.transitions[(label, letter)]
        else:
            return None

    def run(self, string):
        if self.start is None:
            raise StartError
        if len(self.acceptors) == 0:
            raise AcceptError

        self.current = self.start
        steps = []

        for c in string:
            next = self.transition(self.current, c)
            if next is not None:
                steps.append((self.current, next))
                self.current = next
            else:
                return steps, (self.current, "Failed")

        if self.current in self.acceptors:
            return steps, (self.current, "Succeeded")
        else:
            return steps, (self.current, "Failed")


def bezier(points, segments):
    result = []

    for n in range(segments):
        dist = n / segments
        points_copy = [p for p in points]

        while len(points_copy) > 1:
            reduced = []
            for i in range(len(points_copy) - 1):
                reduced.append(between(points_copy[i], points_copy[i+1], dist))
            points_copy = reduced

        result.append(points_copy[0])

    return result


# Get the coordinate of the point
def between(a, b, segment):
    ax, ay = a
    bx, by = b

    distance = math.dist(a, b) * segment
    angle = math.atan2(ay - by, ax - bx)
    return round(ax - (math.cos(angle) * distance)), round(ay - (math.sin(angle) * distance))


# Circles, aka HELL
def circle_from_3_points(a, b, c):
    ax, ay, bx, by, cx, cy = *a, *b, *c
    temp = bx * bx + by * by
    bc = (ax * ax + ay * ay - temp) / 2
    cd = (temp - cx * cx - cy * cy) / 2
    det = (ax - bx) * (by - cy) - (bx - cx) * (ay - by)

    if abs(det) < 1.0e-6:
        return None, 0

    center_x = (bc * (by - cy) - cd * (ay - by)) / det
    center_y = ((ax - bx) * cd - (bx - cx) * bc) / det
    radius = math.sqrt((center_x - ax)**2 + (center_y - ay)**2)
    return (round(center_x), round(center_y)), round(radius)


def arc_to_polygon(center, r, width, start, stop, sign):
    x, y = center
    outer = []
    inner = []

    n = round(r * abs(stop - start) / 20)
    if n < 2:
        n = 2

    for i in range(n):
        delta = i / (n - 1)
        phi0 = start + (stop - start) * delta
        x0 = round(x + r * math.cos(phi0))
        y0 = round(y + r * math.sin(phi0))
        outer.append((x0, y0))
        phi1 = stop + (start - stop) * delta
        x1 = round(x + (r - width) * math.cos(phi1))
        y1 = round(y + (r - width) * math.sin(phi1))
        inner.append((x1, y1))

    return outer + inner


def draw_arc(surface, start, mid, end):
    center, radius = circle_from_3_points(start, mid, end)

    if center is not None:
        pygame.draw.circle(surface, (0, 0, 255), center, radius, 3)
        pygame.draw.circle(surface, (0, 0, 255), center, 2, 3)

        # i_start = sorted(intersections(center, radius, start), key=lambda x: math.dist(x, mid))[0]
        # i_end = sorted(intersections(center, radius, end), key=lambda x: math.dist(x, mid))[0]
        # i_start = intersections(center, radius, start)[1]
        # i_end = intersections(center, radius, end)[0]
        #
        # start_angle = get_angle(center, start) + math.pi
        # end_angle = get_angle(center, end) + math.pi

        dx = end[0] - start[0]
        dy = end[1] - start[1]
        scale = math.sqrt(dx * dx + dy * dy)
        parallel = (dx * (mid[0] - start[0]) + dy * (mid[1] - start[1])) / (scale * scale)
        perpendicular = (dx * (mid[1] - start[1]) - dy * (mid[0] - start[0])) / scale
        is_reversed = perpendicular > 0
        reverse_scale = 1 if is_reversed else -1
        start_angle = get_angle(start, center) - reverse_scale * 30 / radius
        end_angle = get_angle(end, center) + reverse_scale * 30 / radius
        start_x = center[0] + radius * math.cos(start_angle)
        start_y = center[1] + radius * math.sin(start_angle)
        end_x = center[0] + radius * math.cos(end_angle)
        end_y = center[1] + radius * math.sin(end_angle)

        if not is_reversed:
            start_angle, end_angle = end_angle, start_angle

        path = arc_to_polygon(center, radius, 3, start_angle, end_angle, -reverse_scale)
        pygame.gfxdraw.aapolygon(surface, path, (0, 0, 0))
        pygame.gfxdraw.filled_polygon(surface, path, (0, 0, 0))
    else:
        pass  # Regular line


def get_angle(a, b):
    return math.atan2(a[1] - b[1], a[0] - b[0])


def intersections(c0, r0, c1):
    x0, y0 = c0
    x1, y1 = c1
    r1 = 30

    d = math.dist(c0, c1)

    a = (r0 ** 2 - r1 ** 2 + d ** 2) / (2 * d)
    h = math.sqrt(r0 ** 2 - a ** 2)
    x2 = x0 + a * (x1 - x0) / d
    y2 = y0 + a * (y1 - y0) / d

    x3 = x2 + h * (y1 - y0) / d
    y3 = y2 - h * (x1 - x0) / d
    x4 = x2 - h * (y1 - y0) / d
    y4 = y2 + h * (x1 - x0) / d

    return (x3, y3), (x4, y4)


# test = Automaton()
#
# test.add_state("q0", (0, 0))
# test.add_state("q1", (0, 0))
# test.add_state("q2", (0, 0))
# test.add_state("q3", (0, 0))
#
# test.add_transition("q0", "q1", "0")
# test.add_transition("q0", "q0", "1")
# test.add_transition("q1", "q1", "0")
# test.add_transition("q1", "q2", "1")
# test.add_transition("q2", "q3", "0")
# test.add_transition("q2", "q0", "1")
# test.add_transition("q3", "q3", "0")
# test.add_transition("q3", "q3", "1")
#
# # test.start = "q0"
# # test.acceptors = ["q3"]
# test.remove_state("q2")
#
#
# print(test.states)
# print(test.transitions)
