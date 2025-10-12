# pylint: disable=missing-module-docstring,disable=missing-class-docstring,missing-function-docstring,line-too-long
import math
from typing import List


def euclidean_distance(a: List[float], b: List[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def greatest_common_denominator(a: int, b: int) -> int:
    while b != 0:
        a, b = b, a % b
    return a


class AspectRatio:
    def __init__(self, numerator: int, denominator: int):
        self.numerator = numerator
        self.denominator = denominator

    def value(self) -> float:
        return self.numerator / self.denominator

    def simplify(self) -> "AspectRatio":
        divisor = greatest_common_denominator(self.numerator, self.denominator)
        if divisor == 1:
            return self
        return AspectRatio(self.numerator // divisor, self.denominator // divisor)

    def __str__(self):
        return f"{self.numerator}:{self.denominator}"

    def __eq__(self, other):
        if not isinstance(other, AspectRatio):
            return False
        simplified_self = self.simplify()
        simplified_other = other.simplify()
        return (simplified_self.numerator == simplified_other.numerator and
                simplified_self.denominator == simplified_other.denominator)


class Resolution:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def aspect_ratio(self) -> AspectRatio:
        return AspectRatio(self.width, self.height).simplify()

    def valid(self, patch: int, min: int, max: int) -> bool:
        return (self.width >= min and self.width % patch == 0 and self.width <= max and
                self.height >= min and self.height % patch == 0 and self.height <= max)

    def can_contains(self, target: "Resolution") -> bool:
        return self.width >= target.width and self.height >= target.height

    def total_pixels(self) -> int:
        return self.width * self.height

    def valid(self) -> bool:
        return self.width > 0 and self.height > 0

    def __str__(self):
        return f"{self.width}×{self.height}"

    def go_string(self) -> str:
        return f"{self.__str__()} ({self.total_pixels()} pixels with {self.aspect_ratio().__str__()} ratio)"


class ResolutionsList:
    def __init__(self, resolutions: List[Resolution] = []):
        self.resolutions = resolutions

    def biggest_resolution(self) -> Resolution:
        if not self.resolutions:
            return Resolution(0, 0)
        return max(self.resolutions, key=lambda r: r.total_pixels())

    def smallest_resolution(self) -> Resolution:
        if not self.resolutions:
            return Resolution(0, 0)
        return min(self.resolutions, key=lambda r: r.total_pixels())

    def get_closest(self, target: Resolution) -> Resolution:
        if not self.resolutions:
            return Resolution(0, 0)

        closest = self.resolutions[0]
        closest_distance = euclidean_distance(
            [closest.width, closest.height],
            [target.width, target.height]
        )

        for res in self.resolutions[1:]:
            distance = euclidean_distance(
                [res.width, res.height],
                [target.width, target.height]
            )
            if distance < closest_distance:
                closest = res
                closest_distance = distance

        return closest

    def get_closest_equal_or_larger(self, target: Resolution) -> Resolution:
        if not self.resolutions:
            return None

        closest_equal_or_larger = self.resolutions[0]
        closest_distance = euclidean_distance(
            [float(closest_equal_or_larger.width),
             float(closest_equal_or_larger.height)],
            [float(target.width), float(target.height)]
        )

        for resolution in self.resolutions:
            distance = euclidean_distance(
                [float(resolution.width), float(resolution.height)],
                [float(target.width), float(target.height)]
            )
            if distance < closest_distance or not closest_equal_or_larger.can_contains(target):
                closest_equal_or_larger = resolution
                closest_distance = distance

        return closest_equal_or_larger

    def get_closest_by_ratio(self, target: Resolution) -> Resolution:
        if not self.resolutions:
            return Resolution(0, 0)

        reference_ratio = target.aspect_ratio()

        # Sort by ratio distance to target ratio
        ratio_sorted = sorted(self.resolutions, key=lambda r: euclidean_distance(
            [r.aspect_ratio().numerator, r.aspect_ratio().denominator],
            [reference_ratio.numerator, reference_ratio.denominator]
        ))

        # Find all candidates with the same ratio distance
        closest_candidates = [ratio_sorted[0]]
        ref_distance = euclidean_distance(
            [ratio_sorted[0].aspect_ratio().numerator,
             ratio_sorted[0].aspect_ratio().denominator],
            [reference_ratio.numerator, reference_ratio.denominator]
        )

        for res in ratio_sorted[1:]:
            distance = euclidean_distance(
                [res.aspect_ratio().numerator, res.aspect_ratio().denominator],
                [reference_ratio.numerator, reference_ratio.denominator]
            )
            if abs(distance - ref_distance) < 1e-9:  # Using approximate equality
                closest_candidates.append(res)
            else:
                break

        # Return the resolution closest in size from the closest ratios
        return ResolutionsList(closest_candidates).get_closest(target)


def get_closest_valid_patch_resolution(res: Resolution, patch: int) -> Resolution:
    if res.width % patch == 0 and res.height % patch == 0:
        return res

    truncated_width_ratio = res.width // patch
    truncated_height_ratio = res.height // patch

    candidates = [
        Resolution(truncated_width_ratio * patch,
                   truncated_height_ratio * patch),  # SW
        Resolution(truncated_width_ratio * patch,
                   (truncated_height_ratio + 1) * patch),  # NW
        Resolution((truncated_width_ratio + 1) * patch,
                   truncated_height_ratio * patch),  # SE
        Resolution((truncated_width_ratio + 1) * patch,
                   (truncated_height_ratio + 1) * patch)  # NE
    ]

    return ResolutionsList(candidates).get_closest(res)
