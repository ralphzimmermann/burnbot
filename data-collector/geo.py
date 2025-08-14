#!/usr/bin/env python3
"""
Geospatial utilities to translate Burning Man ring/clock locations to latitude/longitude.

Definitions
- Center ("the Man"): 40.786959, -119.202991
- Rings: Esplanade, then A..K increasing radius outward
- Clock times: 2:00 through 10:00 in 15-minute increments

Approach
1) Derive ring radii (in meters) from center using provided 9:00 coordinates for each ring
2) Convert a given clock time to a bearing (degrees from north, clockwise)
3) Convert polar offset (radius, bearing) to (lat, lon) using a small-area approximation

Note
The mapping uses a standard clock-to-bearing mapping: 12:00=0°, 3:00=90°, 6:00=180°, 9:00=270°.
"""

from dataclasses import dataclass
from math import radians, degrees, cos, sin, atan2, sqrt
from typing import Dict, Tuple


# Center of Black Rock City (The Man)
MAN_LAT = 40.786959
MAN_LON = -119.202991


@dataclass(frozen=True)
class LatLon:
    lat: float
    lon: float


# Reference coordinates at 9:00 for each ring (approximate)
RING_COORDS_9: Dict[str, LatLon] = {
    "Esplanade": LatLon(40.791876, -119.209625),
    "A": LatLon(40.792724, -119.210704),
    "B": LatLon(40.793335, -119.211465),
    "C": LatLon(40.793891, -119.212184),
    "D": LatLon(40.794464, -119.212946),
    "E": LatLon(40.795038, -119.213724),
    "F": LatLon(40.795960, -119.214976),
    "G": LatLon(40.796545, -119.215717),
    "H": LatLon(40.797089, -119.216433),
    "I": LatLon(40.797599, -119.217095),
    "J": LatLon(40.797985, -119.217600),
    "K": LatLon(40.798362, -119.218090),
}


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance between two lat/lon points in meters."""
    R = 6371000.0
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2.0) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2.0) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def _meters_per_degree(lat: float) -> Tuple[float, float]:
    """Return meters per degree latitude and longitude at given latitude."""
    # Approximation sufficient for BRC-scale distances
    m_per_deg_lat = 111_320.0
    m_per_deg_lon = 111_320.0 * cos(radians(lat))
    return m_per_deg_lat, m_per_deg_lon


def _bearing_from_clock(clock_hhmm: str) -> float:
    """
    Convert a clock time (e.g., "9:00", "4:30", "2:15") to a bearing in degrees
    from north, clockwise. 12:00 = 0°, 3:00 = 90°, 6:00 = 180°, 9:00 = 270°.
    """
    hh, mm = clock_hhmm.split(":")
    hours = int(hh) % 12
    minutes = int(mm)
    frac_hours = hours + minutes / 60.0
    return (frac_hours / 12.0) * 360.0


def _precompute_radii_m() -> Dict[str, float]:
    radii: Dict[str, float] = {}
    for ring, coord in RING_COORDS_9.items():
        radii[ring] = _haversine_m(MAN_LAT, MAN_LON, coord.lat, coord.lon)
    return radii


RING_RADII_M: Dict[str, float] = _precompute_radii_m()


def ring_clock_to_latlon(ring: str, clock_hhmm: str) -> Tuple[float, float]:
    """
    Compute approximate (lat, lon) for a given ring and clock position.

    Args:
        ring: "Esplanade" or one of "A".."K" (case-insensitive)
        clock_hhmm: string like "7:25", "9:00" (2:00–10:00 at 15-min increments)

    Returns:
        (lat, lon) tuple
    """
    rkey = ring.strip().title() if ring.strip().lower() == 'esplanade' else ring.strip().upper()
    if rkey not in RING_RADII_M:
        raise ValueError(f"Unknown ring '{ring}'. Expected 'Esplanade' or A..K.")

    radius_m = RING_RADII_M[rkey]
    bearing_deg = _bearing_from_clock(clock_hhmm)
    bearing_rad = radians(bearing_deg)

    # Convert polar (radius, bearing) to local ENU offsets (meters)
    north_m = radius_m * cos(bearing_rad)
    east_m = radius_m * sin(bearing_rad)

    m_per_deg_lat, m_per_deg_lon = _meters_per_degree(MAN_LAT)
    dlat = north_m / m_per_deg_lat
    dlon = east_m / m_per_deg_lon

    return (MAN_LAT + dlat, MAN_LON + dlon)


def clock_and_distance_to_latlon(clock_hhmm: str, distance_feet: float) -> Tuple[float, float]:
    """
    Compute approximate (lat, lon) for a given clock angle and radial distance from the Man.

    Args:
        clock_hhmm: clock position like "1:21", "10:51", "12:00"
        distance_feet: radial distance from the Man in feet

    Returns:
        (lat, lon) tuple
    """
    radius_m = float(distance_feet) * 0.3048
    bearing_deg = _bearing_from_clock(clock_hhmm)
    bearing_rad = radians(bearing_deg)

    north_m = radius_m * cos(bearing_rad)
    east_m = radius_m * sin(bearing_rad)

    m_per_deg_lat, m_per_deg_lon = _meters_per_degree(MAN_LAT)
    dlat = north_m / m_per_deg_lat
    dlon = east_m / m_per_deg_lon

    return (MAN_LAT + dlat, MAN_LON + dlon)


def normalized_location_to_latlon(normalized_location: str) -> Tuple[float, float]:
    """
    Parse a normalized location like "G & 7:25" or "Esplanade & 7:45" and
    return (lat, lon).
    """
    parts = [p.strip() for p in normalized_location.split('&')]
    if len(parts) != 2:
        raise ValueError(f"Invalid normalized location '{normalized_location}'. Expected '<Ring> & <Clock>'.")
    ring, clock = parts[0], parts[1]
    return ring_clock_to_latlon(ring, clock)


__all__ = [
    "ring_clock_to_latlon",
    "normalized_location_to_latlon",
    "clock_and_distance_to_latlon",
]


