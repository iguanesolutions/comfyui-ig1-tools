# pylint: disable=missing-module-docstring,disable=missing-class-docstring,missing-function-docstring,line-too-long
import math
from typing import List, Tuple

# Constants
STEP = 16    # Should be 32 but it's too limiting; 16 allows for more resolutions and seems to work fine with Flux anyway
MIN_SIZE = 320
MAX_SIZE = 1440


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

    def flux_valid(self) -> bool:
        return (self.width >= MIN_SIZE and self.width % STEP == 0 and self.width <= MAX_SIZE and
                self.height >= MIN_SIZE and self.height % STEP == 0 and self.height <= MAX_SIZE)

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


def compute_all_flux_valid_resolutions() -> ResolutionsList:
    valid_resolutions = []

    # Start with one less than the minimum to generate the first candidate below min_size
    width_multiplier = (MIN_SIZE // STEP) - 1
    while True:
        width_multiplier += 1
        width = STEP * width_multiplier
        if width > MAX_SIZE:
            break

        # For each width, iterate through height multipliers
        height_multiplier = (MIN_SIZE // STEP) - 1
        while True:
            height_multiplier += 1
            height = STEP * height_multiplier
            if height > MAX_SIZE:
                break

            valid_resolutions.append(Resolution(width, height))

    return ResolutionsList(valid_resolutions)


# Precompute all valid resolutions
all_valid_resolutions = compute_all_flux_valid_resolutions()


def get_flux_resolutions_by_ratio(ratio: AspectRatio) -> ResolutionsList:
    valid_resolutions = []
    for res in all_valid_resolutions.resolutions:
        if res.aspect_ratio() == ratio:
            valid_resolutions.append(res)
    return ResolutionsList(valid_resolutions)


def get_closest_valid_step_resolution(res: Resolution) -> Resolution:
    if res.width % STEP == 0 and res.height % STEP == 0:
        return res

    truncated_width_ratio = res.width // STEP
    truncated_height_ratio = res.height // STEP

    candidates = [
        Resolution(truncated_width_ratio * STEP,
                   truncated_height_ratio * STEP),  # SW
        Resolution(truncated_width_ratio * STEP,
                   (truncated_height_ratio + 1) * STEP),  # NW
        Resolution((truncated_width_ratio + 1) * STEP,
                   truncated_height_ratio * STEP),  # SE
        Resolution((truncated_width_ratio + 1) * STEP,
                   (truncated_height_ratio + 1) * STEP)  # NE
    ]

    return ResolutionsList(candidates).get_closest(res)


def get_flux_closest_valid_resolution(res: Resolution) -> Tuple[Resolution, Resolution]:
    """
    Returns the closest FLUX-compatible resolution and the adjusted reference.
    """
    # Is the resolution already valid?
    if res.flux_valid():
        return res, res
    # Try to find a valid resolution with the same aspect ratio
    candidates = get_flux_resolutions_by_ratio(res.aspect_ratio())
    if candidates.resolutions:
        flux_valid = candidates.get_closest_equal_or_larger(res)
        return flux_valid, res
    # Try with a slight adjustment of the resolution to fit step increments
    adjusted_reference = get_closest_valid_step_resolution(res)
    if adjusted_reference.flux_valid():
        return adjusted_reference, adjusted_reference
    # As last resort, find the closest valid resolution by aspect ratio
    flux_valid = all_valid_resolutions.get_closest_by_ratio(
        adjusted_reference)
    return flux_valid, adjusted_reference
