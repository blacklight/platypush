from dataclasses import dataclass
import math
from typing import Tuple

from flask import Blueprint, make_response, request


logo = Blueprint('logo', __name__)

# Declare routes list
__routes__ = [
    logo,
]


@dataclass
class Gear:
    """
    A utility class used to model the gears in the application's logo.
    """

    center: Tuple[float, float]
    outer_radius: float
    inner_radius: float
    color: str = "currentColor"
    background: str = ""
    num_spikes: int = 0
    spike_max_base: float = 0
    spike_min_base: float = 0
    spike_height: float = 0
    alpha_offset: float = 0

    def to_svg(self) -> str:
        """
        Returns the SVG representation of a gear.
        """

        # Generate the basic circle
        svg = f"""
        <circle
            cx="{self.center[0]}" cy="{self.center[1]}"
            r="{self.outer_radius - (self.inner_radius / math.pi)}"
            stroke-width="{self.inner_radius}"
            stroke="{self.color}"
            fill="none" />
        """

        # Generate the spikes
        for i in range(self.num_spikes):
            # Iterate for alpha -> [0, 2*pi]
            alpha = (2 * math.pi * i) / self.num_spikes
            # Calculate the base angle for the major base of the gear polygon
            maj_delta_alpha = math.asin(self.spike_max_base / (2 * self.outer_radius))
            # Calculate the points of the gear polygon's major base
            maj_base = (
                (
                    self.center[0]
                    + self.outer_radius
                    * math.cos(alpha + maj_delta_alpha + self.alpha_offset),
                    self.center[1]
                    + self.outer_radius
                    * math.sin(alpha + maj_delta_alpha + self.alpha_offset),
                ),
                (
                    self.center[0]
                    + self.outer_radius
                    * math.cos(alpha - maj_delta_alpha + self.alpha_offset),
                    self.center[1]
                    + self.outer_radius
                    * math.sin(alpha - maj_delta_alpha + self.alpha_offset),
                ),
            )

            # Height of the gear relative to the circle's center
            h = self.outer_radius * math.cos(maj_delta_alpha) + self.spike_height
            # Calculate the base angle for the minor base of the gear polygon
            min_delta_alpha = math.asin(self.spike_min_base / (2 * h))
            # Calculate the points of the gear polygon's minor base
            min_base = (
                (
                    self.center[0]
                    + h * math.cos(alpha - min_delta_alpha + self.alpha_offset),
                    self.center[1]
                    + h * math.sin(alpha - min_delta_alpha + self.alpha_offset),
                ),
                (
                    self.center[0]
                    + h * math.cos(alpha + min_delta_alpha + self.alpha_offset),
                    self.center[1]
                    + h * math.sin(alpha + min_delta_alpha + self.alpha_offset),
                ),
            )

            # Flatten the polygon's points
            svg_points = " ".join(
                [f"{point[0]},{point[1]}" for point in [*maj_base, *min_base]]
            )

            # Serialize the gear polygon to SVG
            svg += f"""
        <polygon points="{svg_points}" stroke="{self.color}" fill="{self.color}" />"""

        return svg


# Properties of the two gears on the logo
gears = [
    Gear(
        center=(32.9, 34.5),
        outer_radius=22.6,
        inner_radius=12.4,
        num_spikes=12,
        spike_max_base=9,
        spike_min_base=4.3,
        spike_height=10.16,
    ),
    Gear(
        center=(65.5, 70.5),
        outer_radius=14.4,
        inner_radius=8.5,
        num_spikes=7,
        spike_max_base=9,
        spike_min_base=4.3,
        spike_height=7.5,
        alpha_offset=math.pi / 6.6,
    ),
]


template_start = """
<svg version="1.1"
     width="{width}" height="{height}"
     viewBox="0 0 100 100"
     preserveAspectRatio="none"
     xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="triangleGradient">
        <stop offset="0%" stop-color="#8acb45" />
        <stop offset="50%" stop-color="#6bbb4c" />
        <stop offset="100%" stop-color="#5cb450" />
    </linearGradient>
  </defs>

  <rect width="100%" height="100%" fill="{bg_color}" />
"""

template_end = "\n</svg>"


@logo.route('/logo.svg', methods=['GET'])
def logo_path():
    """
    This path dynamically generates the logo image as a parametrizable vector SVG.

    Parameters:

        - ``size``: Size of the image in pixels (default: 256)
        - ``bg``: Background color (default: "none")
        - ``fg``: Foreground color (default: "currentColor")

    """
    size = request.args.get("size", 256)
    bg = request.args.get("bg", "none")
    fg = request.args.get("fg", "currentColor")
    svg = template_start.format(
        width=size,
        height=size,
        bg_color=bg,
    )

    for gear in gears:
        gear.color = fg
        gear.background = bg
        svg += gear.to_svg()

    # "Play" triangle on the logo
    svg += """\n\t\t<polygon points="67,47 67,3 99,25.3" fill="url(#triangleGradient)" />"""
    svg += template_end

    rs = make_response(svg)
    rs.headers.update({"Content-Type": "image/svg+xml"})
    return rs


# vim:sw=4:ts=4:et:
