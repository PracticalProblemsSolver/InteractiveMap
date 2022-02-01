class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Rectangle:
    def __init__(self, point, w, h):
        self.point = point
        self.w = w
        self.h = h
        self.west = self.point - self.w
        self.east = self.point + self.w
        self.north = self.point - self.h
        self.south = self.point + self.h


class QuadTree:
    def __init__(self, boundary, capacity=4):
        self.capacity = capacity
        self.boundary = boundary
        self.point_list = []
        self.divided = False
