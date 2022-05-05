"""K Dimensional tree module"""
from math import pow


class KDimensionalTree:
    """
    K-dimensional tree class.
    Contains necessary methods to
    work with k-d tree.
    """
    def __init__(self, k=2):
        self.dimensions = k

    def build(self, points, depth=0):
        """
        Method builds a k-d tree by given list of points

        :param points: List of points [x,y]
        :type points: list
        :param depth: Depth of the recursion
        :type depth: int
        :return: Built k-d tree
        :rtype: dict
        """
        points_number = len(points)
        if not points_number:
            return None
        axis = depth % self.dimensions
        sorted_points = sorted(points, key=lambda point: point[axis])
        return {
            'point': sorted_points[int(points_number / 2)],
            'left': self.build(sorted_points[:(int(points_number / 2))], depth + 1),
            'right': self.build(sorted_points[(int(points_number / 2) + 1):], depth + 1)
        }

    def euclidean_distance(self, point_1, point_2):
        """
        Method counts euclidean distance between two points

        :param point_1: First point [x,y]
        :type point_1: list
        :param point_2: Second point [x,y]
        :type point_2: list
        :return: Distance
        :rtype: float
        """
        return pow(point_2[0] - point_1[0], 2) + pow(point_2[1] - point_1[1], 2)

    def best_of_two(self, benchmark, point_1, point_2):
        """
        Method finds closest of two points

        :param benchmark: Benchmark point [x,y]
        :type benchmark: list
        :param point_1: First point [x,y]
        :type point_1: list
        :param point_2: Second point [x,y]
        :type point_2: list
        :return: Closest point
        :rtype: list
        """
        if point_1 is None:
            return point_2
        if point_2 is None:
            return point_1
        if self.euclidean_distance(benchmark, point_1) < \
                self.euclidean_distance(benchmark, point_2):
            return point_1
        else:
            return point_2

    def find_closest(self, tree, benchmark, depth=0):
        """
        Main method that finds closest to the benchmark point

        :param tree: Built k-d tree
        :type tree: dict
        :param benchmark: Benchmark point
        :type benchmark: list
        :param depth: Depth of the recursion
        :type depth: int
        :return: Closest point
        :rtype: list
        """
        if tree is None:
            return None
        axis = depth % self.dimensions
        if benchmark[axis] < tree['point'][axis]:
            next_branch = tree['left']
            opposite_branch = tree['right']
        else:
            next_branch = tree['right']
            opposite_branch = tree['left']
        best = self.best_of_two(benchmark,
                                self.find_closest(next_branch,
                                                  benchmark,
                                                  depth + 1),
                                tree['point'])
        if self.euclidean_distance(benchmark, best) \
                > pow(benchmark[axis] - tree['point'][axis], 2):
            best = self.best_of_two(benchmark,
                                    self.find_closest(opposite_branch,
                                                      benchmark,
                                                      depth + 1),
                                    best)
        return best
