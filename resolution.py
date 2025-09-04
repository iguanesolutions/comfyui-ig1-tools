# pylint: disable=missing-module-docstring,disable=missing-class-docstring,missing-function-docstring,line-too-long
import math
from typing import List


class AspectRatio:
    def __init__(self, numerator: int, denominator: int):
        self.numerator = numerator
        self.denominator = denominator

    def value(self) -> float:
        return self.numerator / self.denominator

    def simplify(self) -> 'AspectRatio':
        divisor = greatest_common_denominator(self.numerator, self.denominator)
        if divisor == 1:
            return self
        return AspectRatio(self.numerator // divisor, self.denominator // divisor)

    def __str__(self) -> str:
        return f"{self.numerator}:{self.denominator}"

    def __eq__(self, ar: 'AspectRatio') -> bool:
        return self.numerator * ar.denominator == ar.numerator * self.denominator


class Resolution:
    def __init__(self, width: int, height: int, compatibility_step: int):
        self.width = width
        self.height = height
        self.compatibility_step = compatibility_step

    def aspect_ratio(self) -> AspectRatio:
        return AspectRatio(self.width, self.height).simplify()

    def has_better_compatibility(self) -> bool:
        return self.width % self.compatibility_step == 0 and self.height % self.compatibility_step == 0

    def can_contains(self, target: 'Resolution') -> bool:
        return self.width >= target.width and self.height >= target.height

    def __str__(self) -> str:
        return f"{self.width}×{self.height}"

    def __repr__(self) -> str:
        output = f"{self} ({self.total_pixels()} pixels with {self.aspect_ratio()} ratio)"
        if self.has_better_compatibility():
            output += " [Better Compatibility]"
        return output

    def total_pixels(self) -> int:
        return self.width * self.height

    def valid(self) -> bool:
        return self.width > 0 and self.height > 0


class ResolutionsList(List[Resolution]):
    def biggest_resolution(self) -> Resolution:
        return max(self, key=lambda res: res.total_pixels())

    def smallest_resolution(self) -> Resolution:
        return min(self, key=lambda res: res.total_pixels())

    def get_closest(self, target: Resolution) -> Resolution:
        closest = self[0]
        closest_distance = euclidean_distance([closest.width, closest.height], [
                                              target.width, target.height])
        for res in self:
            distance = euclidean_distance([res.width, res.height], [
                                          target.width, target.height])
            if distance < closest_distance:
                closest = res
                closest_distance = distance
        return closest

    def get_closest_equal_or_larger(self, target: Resolution) -> Resolution:
        closest_equal_or_larger = self[0]
        closest_distance = euclidean_distance(
            [closest_equal_or_larger.width, closest_equal_or_larger.height], [target.width, target.height])
        for res in self:
            distance = euclidean_distance([res.width, res.height], [
                                          target.width, target.height])
            if distance < closest_distance or not closest_equal_or_larger.can_contains(target):
                closest_equal_or_larger = res
                closest_distance = distance
        return closest_equal_or_larger


def euclidean_distance(a: List[float], b: List[float]) -> float:
    diff = [a_i - b_i for a_i, b_i in zip(a, b)]
    return math.sqrt(sum(x * x for x in diff))


def greatest_common_denominator(a: int, b: int) -> int:
    while b != 0:
        a, b = b, a % b
    return a
