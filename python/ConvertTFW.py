import os
from pyproj import Proj, transform
import logging
from math import radians, cos

'''
This script reads a .tfw file (world file for a raster image),
converts coordinates from lat/lon to UTM if necessary,
and writes a new .tfw file with correct UTM coordinates and pixel sizes in meters.

Out
A  → pixel width in meters (X-scale)
B  → rotation (usually 0)
C  → rotation (usually 0)
D  → pixel height in meters (negative Y-scale)
E  → UTM Easting of top-left corner (X origin)
F  → UTM Northing of top-left corner (Y origin)


General TFW format:
LineMeaning (input) 
1A – pixel width in the input coordinate units (meters if UTM, degrees if lat/lon)
2B – X-rotation (usually 0)
3C – Y-rotation (usually 0)
4D – pixel height in the input coordinate units (negative)
5E – X origin of the top-left pixel (UTM easting or longitude)
6F – Y origin of the top-left pixel (UTM northing or latitude)

'''

def create_correct_tfw(input_tfw_path, output_tfw_path=None, utm_zone=36, north=True):
    """
    Reads a .tfw file (possibly with lat/lon instead of UTM),
    converts to proper UTM (Zone 36N by default),
    and writes a new _new.tfw with correct meters and UTM coordinates.

    Parameters:
        input_tfw_path (str): Path to input .tfw file
        output_tfw_path (str, optional): Output path. If None, uses input_new.tfw
        utm_zone (int): UTM zone (36 for Israel)
        north (bool): True for Northern hemisphere

    Example inputs:
        "0.0000053644\n0.0\n0.0\n-0.0000053644\n34.9204704165\n31.9817295671"
        → lat/lon, pixel size in degrees

        "0.5\n0\n0\n-0.5\n685800.25\n3534964.75"
        → already UTM, pixel size in meters
    """
    if output_tfw_path is None:
        base, ext = os.path.splitext(input_tfw_path)
        output_tfw_path = f"{base}_new{ext}"

    # Read TFW lines
    with open(input_tfw_path, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    if len(lines) != 6:
        raise ValueError(f"Invalid TFW file: expected 6 lines, got {len(lines)}")

    try:
        A = float(lines[0])  # pixel width
        B = float(lines[1])  # rotation
        C = float(lines[2])  # rotation
        D = float(lines[3])  # pixel height (negative)
        E = float(lines[4])  # X origin (top-left)
        F = float(lines[5])  # Y origin (top-left)
    except ValueError as e:
        raise ValueError(f"Failed to parse TFW values: {e}")

    logging.info(f"Original TFW: A={A}, D={D}, E={E}, F={F}")

    # Step 1: Detect if (E, F) is lat/lon or UTM
    def is_likely_latlon(x, y):
        return (-180 <= x <= 180) and (-90 <= y <= 90)

    is_geo = is_likely_latlon(E, F)

    # Step 2: Define projections
    p_ll = Proj(proj='latlong', datum='WGS84')  # EPSG:4326
    p_utm = Proj(proj='utm', zone=utm_zone, ellps='WGS84', south=not north)

    # Step 3: Convert top-left corner to UTM if needed
    if is_geo:
        logging.info("Detected lat/lon in TFW → converting to UTM")
        utm_easting, utm_northing = transform(p_ll, p_utm, F, E)  # (lon, lat) → (E, N)
        # Convert pixel size from degrees → meters
        # Approximate: 1 degree ≈ 111320 m at equator, but better to use local scale
        # Use average latitude for scaling
        avg_lat = E
        meters_per_deg_lat = 111320  # constant
        meters_per_deg_lon = 111320 * abs(cos(radians(avg_lat)))
        
        new_A = A * meters_per_deg_lon   # pixel width in meters
        new_D = D * meters_per_deg_lat   # pixel height in meters (D is negative)
    else:
        logging.info("Detected UTM in TFW → using as-is")
        utm_easting, utm_northing = E, F
        new_A, new_D = A, D  # already in meters

    # Ensure B and C are zero (standard)
    new_B = 0.0
    new_C = 0.0

    # Step 4: Write new TFW
    with open(output_tfw_path, 'w') as f:
        f.write(f"{new_A:.10f}\n")
        f.write(f"{new_B:.10f}\n")
        f.write(f"{new_C:.10f}\n")
        f.write(f"{new_D:.10f}\n")
        f.write(f"{utm_easting:.10f}\n")
        f.write(f"{utm_northing:.10f}\n")

    logging.info(f"New TFW saved: {output_tfw_path}")
    logging.info(f"   Pixel size: {new_A:.6f} m (X), {new_D:.6f} m (Y)")
    logging.info(f"   Top-left UTM: {utm_easting:.2f} E, {utm_northing:.2f} N")

    return output_tfw_path


if __name__ == "__main__":
        # Configure logging
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
        
        # Example 1: Your lat/lon TFW
        create_correct_tfw("C:\\Users\\OPER\\OneDrive - Israel Aerospace Industries\\OrthoPhoto\\GeoIsr\\ex3\\aIlan.tfw")
        # → creates aIlan_new.tfw with UTM + meters