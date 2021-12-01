import math

import pygame
import pygame.gfxdraw


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
        self.transitions[(start, via)] = (end, (0, 0))

    def add_state(self, label, pos):
        self.states[label] = pos

    def remove_state(self, label):
        del self.states[label]

        self.transitions = {(s, v): (e, m) for (s, v), (e, m) in self.transitions.items() if label not in [s, e]}
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

    if radius > math.dist(a, c) * 5:
        return None, 0
    return (round(center_x), round(center_y)), round(radius)


def arc_to_polygon(center, r, width, start, stop, clockwise=True):
    x, y = center
    outer = []
    inner = []
    segments = r//2  # 200
    sign = 1 if clockwise else -1

    if stop < start:
        stop += math.tau

    if not clockwise:
        start += math.tau

    angle_segment = abs(start - stop) / segments

    for n in range(segments + 1):
        arc_x = x + r * math.cos(start + (n * angle_segment * sign))
        arc_y = y + r * math.sin(start + (n * angle_segment * sign))
        outer.append((arc_x, arc_y))

        arc_x = x + (r - width/2) * math.cos(start + (n * angle_segment * sign))
        arc_y = y + (r - width/2) * math.sin(start + (n * angle_segment * sign))
        inner.append((arc_x, arc_y))

    return outer + list(reversed(inner))


def draw_arc(surface, start, mid, end, color, return_path=False):
    center, radius = circle_from_3_points(start, mid, end)

    if center is not None:
        start_angle, end_angle, is_reversed = adjusted_angles(start, mid, end)

        path = arc_to_polygon(center, radius, 3, start_angle, end_angle, not is_reversed)
        pygame.gfxdraw.aapolygon(surface, path, color)
        pygame.gfxdraw.filled_polygon(surface, path, color)

        if return_path:
            return path
    else:
        x1, y1 = start
        x2, y2 = end

        # Calculate the angle between them and move the starting and ending points to the edge of the states
        angle = get_angle(start, end)
        adjusted_start = (x1 - (math.cos(angle) * 30), y1 - (math.sin(angle) * 30))
        adjusted_end = (x2 + (math.cos(angle) * 30), y2 + (math.sin(angle) * 30))
        pygame.draw.line(surface, color, adjusted_start, adjusted_end, 3)


# Get the angle from a to b, in radians
def get_angle(a, b):
    return math.atan2(a[1] - b[1], a[0] - b[0])


# Creates a vector from the middle of 'start' to 'end' that points towards 'mid'.
# Represented as the length of the vector and the rotational distance away from the angle of 'start' to 'end'
def vectorize(start, mid, end):
    midway = between(start, end, 0.5)

    main_angle = get_angle(midway, end)
    vec_angle = get_angle(midway, mid)
    angle = (vec_angle - main_angle) / math.pi

    distance = math.dist(midway, mid)

    return distance, angle


# Calculates the coordinates at the end of the given vector, reverse of above
def from_vector(start, end, vector):
    distance = vector[0]
    angle = vector[1] * math.pi

    midway = between(start, end, 0.5)
    length = distance  # math.dist(midway, end) * distance
    ang = get_angle(midway, end)

    x = midway[0] + length * (math.cos(ang - angle))
    y = midway[1] + length * (math.sin(ang - angle))

    return x, y


def adjusted_angles(start, mid, end):
    center, radius = circle_from_3_points(start, mid, end)

    if center is None:
        return None, None, None

    dx = end[0] - start[0]
    dy = end[1] - start[1]
    scale = math.sqrt(dx * dx + dy * dy)
    perpendicular = (dx * (mid[1] - start[1]) - dy * (mid[0] - start[0])) / scale
    is_reversed = perpendicular > 0
    reverse_scale = 1 if is_reversed else -1

    start_angle = get_angle(start, center) - reverse_scale * 30 / radius
    end_angle = get_angle(end, center) + reverse_scale * 30 / radius

    return start_angle, end_angle, is_reversed


# DISTANCE POINT TO LINE SEGMENT
def point_to_segment(pnt, start, end):
    def dot(v, w):
        x, y = v
        X, Y = w
        return x*X + y*Y

    def length(v):
        x, y = v
        return math.sqrt(x*x + y*y)

    def vector(b, e):
        x, y = b
        X, Y = e
        return X - x, Y - y

    def unit(v):
        x, y = v
        mag = length(v)
        return x / mag, y / mag

    def distance(p0, p1):
        return length(vector(p0, p1))

    def scale(v, sc):
        x, y = v
        return x * sc, y * sc

    line_vec = vector(start, end)
    pnt_vec = vector(start, pnt)
    line_len = length(line_vec)
    line_unitvec = unit(line_vec)
    pnt_vec_scaled = scale(pnt_vec, 1.0 / line_len)
    t = dot(line_unitvec, pnt_vec_scaled)
    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0
    nearest = scale(line_vec, t)
    dist = distance(nearest, pnt_vec)
    return dist
