# pylint: disable=missing-module-docstring,disable=missing-class-docstring,missing-function-docstring,line-too-long
import math
from typing import List

HIRES_RATIO = 2


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

    def __str__(self) -> str:
        return f"{self.numerator}:{self.denominator}"

    def __eq__(self, other) -> bool:
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

    def valid(self, patch_len: int, min_len: int, max_size: int) -> bool:
        return (self.width >= min_len and self.width % patch_len == 0 and
                self.height >= min_len and self.height % patch_len == 0 and
                self.width * self.height <= max_size)

    def can_contains(self, target: "Resolution") -> bool:
        return self.width >= target.width and self.height >= target.height

    def total_pixels(self) -> int:
        return self.width * self.height

    def mega_pixels(self) -> float:
        return round(self.total_pixels() / 1000000, 2)

    def __str__(self) -> str:
        return f"{self.width}×{self.height} ({self.aspect_ratio()} @ {self.mega_pixels()}MP)"


def ratio_distance(ref: AspectRatio, candidate: AspectRatio) -> float:
    return abs(ref.value() - candidate.value())


class ResolutionsList:
    def __init__(self, resolutions: List[Resolution] = []):
        self.resolutions = resolutions

    def get_closest(self, target: Resolution) -> Resolution:
        if not self.resolutions:
            return Resolution(0, 0)
        # First candidate
        closest = self.resolutions[0]
        closest_distance = euclidean_distance(
            [closest.width, closest.height],
            [target.width, target.height]
        )
        # Iterate over the rest of the candidates to find the closest one
        for res in self.resolutions[1:]:
            distance = euclidean_distance(
                [res.width, res.height],
                [target.width, target.height]
            )
            if distance < closest_distance:
                closest = res
                closest_distance = distance
            elif distance == closest_distance and res.can_contains(closest):
                # same distance but res is bigger
                closest = res
        return closest

    def get_closest_equal_or_larger(self, target: Resolution) -> Resolution:
        if not self.resolutions:
            return Resolution(0, 0)
        # Find all resolutions larger than or equal to the target
        larger_or_equal_resolutions = ResolutionsList(
            [res for res in self.resolutions if res.can_contains(target)])
        # We prefere a more distant but bigger or equal resolution than a closer but smaller one
        if larger_or_equal_resolutions.resolutions:
            return larger_or_equal_resolutions.get_closest(target)
        # No bigger or equal resolutions in the list, taking all the resolutions into account
        return self.get_closest(target)

    def get_best_candidate(self, target: Resolution) -> Resolution:
        if not self.resolutions:
            return Resolution(0, 0)
        # Sort all possibles resolutions given their ratio aspect distance from target's aspect ratio
        # A candidates with the same ratio will have a distance of 0 and therefor will be at the beginning of the list
        target_aspect_ratio = target.aspect_ratio()
        ratio_sorted = sorted(self.resolutions, key=lambda res: ratio_distance(
            target_aspect_ratio, res.aspect_ratio()))
        # i = 0
        # samples = []
        # for res in ratio_sorted:
        #     if i > 10:
        #         break
        #     samples.append(
        #         f"{res} = {ratio_distance(target_aspect_ratio, res.aspect_ratio())}")
        #     i += 1
        # print(f"Ratio distance sorted: {samples}")
        # Find all candidates with the same ratio distance (multiples could have the same aspect ratio/distance)
        closest_candidates = [ratio_sorted[0]]
        best_candidates_ratio = ratio_sorted[0].aspect_ratio()
        for res in ratio_sorted[1:]:
            if res.aspect_ratio() == best_candidates_ratio:
                closest_candidates.append(res)
            else:
                break
        # print(f"Closest candidates: {ResolutionsList(closest_candidates)}")

        # Return the resolution closest in size from the closest ratio candidates
        return ResolutionsList(closest_candidates).get_closest_equal_or_larger(target)

    def __bool__(self):
        return bool(self.resolutions)

    def __str__(self):
        return str([str(res) for res in self.resolutions])


def generate_all_valid_resolutions(patch_len: int, min_len: int, max_size: int) -> ResolutionsList:
    valid_resolutions = []

    # Start with one less than the minimum to generate the first candidate below min_size
    width_multiplier = (min_len // patch_len) - 1
    while True:
        width_multiplier += 1
        width = patch_len * width_multiplier
        if width * min_len > max_size:
            break

        # For each width, iterate through height multipliers
        height_multiplier = (min_len // patch_len) - 1
        while True:
            height_multiplier += 1
            height = patch_len * height_multiplier
            if width * height > max_size:
                break
            valid_resolutions.append(Resolution(width, height))

    return ResolutionsList(valid_resolutions)
