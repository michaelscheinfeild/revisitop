# --------------------------------------------------------------
#  geo_tiff_info_and_show.py
# --------------------------------------------------------------
#  Requirements:
#      pip install rasterio matplotlib numpy
# --------------------------------------------------------------

import rasterio
from rasterio.enums import ColorInterp
from rasterio.warp import transform_bounds

#from osgeo import osr

import matplotlib.pyplot as plt
import numpy as np
import sys
from pathlib import Path

def dms(coord: float) -> str:
    """Convert decimal degrees to DMS string (e.g. 34d54'56.48"E)"""
    sign = "E" if coord >= 0 else "W"
    coord = abs(coord)
    d = int(coord)
    m = int((coord - d) * 60)
    s = (coord - d - m/60) * 3600
    return f"{d}d{m}'{s:.2f}\"{sign}"

def print_wkt_formatted(wkt_string):
    """Parse and print WKT string in a readable format without special packages."""
    # Remove extra spaces and split by commas, but be careful with nested brackets
    level = 0
    current_field = ""
    fields = []
    
    for char in wkt_string:
        if char == '[':
            level += 1
            current_field += char
        elif char == ']':
            level -= 1
            current_field += char
        elif char == ',' and level == 1:  # Only split at top level commas
            fields.append(current_field.strip())
            current_field = ""
        else:
            current_field += char
    
    # Add the last field
    if current_field.strip():
        fields.append(current_field.strip())
    
    # Print each field
    for field in fields:
        field = field.strip()
        if field.startswith('GEOGCS'):
            print(f"Geographic Coordinate System: {field}")
        elif field.startswith('DATUM'):
            print(f"Datum: {field}")
        elif field.startswith('SPHEROID'):
            print(f"Spheroid: {field}")
        elif field.startswith('PRIMEM'):
            print(f"Prime Meridian: {field}")
        elif field.startswith('UNIT'):
            print(f"Unit: {field}")
        elif field.startswith('AXIS'):
            print(f"Axis: {field}")
        elif field.startswith('AUTHORITY'):
            print(f"Authority: {field}")
        else:
            print(f"Other: {field}")

def print_gdalinfo_like(dataset: rasterio.io.DatasetReader):
    """Print information in the style of gdalinfo."""
    print(f"Driver: {dataset.driver}/{dataset.meta.get('driver', 'Unknown')}")
    print(f"Files: {dataset.name}")
    for aux in dataset.files[1:]:
        print(f"       {aux}")

    print(f"Size is {dataset.width}, {dataset.height}")

    # ---- Coordinate system ------------------------------------------------
    if dataset.crs:
        print("Coordinate System is:")
        print(dataset.crs.to_string())          # EPSG:4326 etc.
        #print(dataset.crs.to_wkt(pretty=True))  # full WKT (matches gdalinfo)
        wkt = dataset.crs.to_wkt()
        print(wkt)
        print("\nWKT Components:")
        print_wkt_formatted(wkt)
    else:
        print("Coordinate System is: (none)")

    # ---- Transform ---------------------------------------------------------
    print(f"Origin = ({dataset.transform.c}, {dataset.transform.f})")
    print(f"Pixel Size = ({dataset.transform.a:.12f},{dataset.transform.e:.12f})")

    # ---- Metadata -----------------------------------------------------------
    meta = dataset.meta.copy()
    meta.update(dataset.tags())
    if meta:
        print("Metadata:")
        for k, v in sorted(meta.items()):
            if k not in ("driver", "dtype", "nodata", "width", "height", "count", "crs", "transform"):
                print(f"  {k}={v}")

    # ---- Image structure ----------------------------------------------------
    interleave = dataset.meta.get("interleave", "pixel").upper()
    print(f"Image Structure Metadata:")
    print(f"  INTERLEAVE={interleave}")

    # ---- Corner coordinates -------------------------------------------------
    left, bottom, right, top = dataset.bounds
    print("Corner Coordinates:")
    print(f"Upper Left  ({left: .10f}, {top: .10f}) ({dms(left)}, {dms(top)})")
    print(f"Lower Left  ({left: .10f}, {bottom: .10f}) ({dms(left)}, {dms(bottom)})")
    print(f"Upper Right ({right: .10f}, {top: .10f}) ({dms(right)}, {dms(top)})")
    print(f"Lower Right ({right: .10f}, {bottom: .10f}) ({dms(right)}, {dms(bottom)})")
    cx = (left + right) / 2
    cy = (top + bottom) / 2
    print(f"Center      ({cx: .10f}, {cy: .10f}) ({dms(cx)}, {dms(cy)})")

    # ---- Bands ---------------------------------------------------------------
    for i in range(1, dataset.count + 1):
        band = dataset.read(i, masked=True)
        ci = dataset.colorinterp[i-1] if i <= len(dataset.colorinterp) else None
        print(f"Band {i} Block={dataset.block_shapes[i-1][0]}x{dataset.block_shapes[i-1][1]} "
              f"Type={band.dtype}, ColorInterp={ci.name if ci else 'Undefined'}")
        if dataset.tags(i):
            print("  Metadata:")
            for k, v in dataset.tags(i).items():
                print(f"    {k}={v}")

        # statistics (use rasterio's built-in if available, otherwise compute)
        stats = dataset.tags(i).get("STATISTICS_MINIMUM")
        if stats:
            print(f"  Min={float(dataset.tags(i)['STATISTICS_MINIMUM']):.3f} "
                  f"Max={float(dataset.tags(i)['STATISTICS_MAXIMUM']):.3f}")
            print(f"  Mean={float(dataset.tags(i)['STATISTICS_MEAN']):.3f} "
                  f"StdDev={float(dataset.tags(i)['STATISTICS_STDDEV']):.3f}")
            vp = dataset.tags(i).get("STATISTICS_VALID_PERCENT")
            if vp:
                print(f"  Valid Percent={vp}")
        else:
            # compute on-the-fly (slow for huge files, but works)
            if band.size:
                print(f"  Min={float(band.min()):.3f} Max={float(band.max()):.3f}")
                print(f"  Mean={float(band.mean()):.3f} StdDev={float(band.std()):.3f}")

        # mask / alpha
        if dataset.mask_flag_enums[i-1]:
            print(f"  Mask Flags: {' '.join([e.name for e in dataset.mask_flag_enums[i-1]])}")

def show_image(dataset: rasterio.io.DatasetReader):
    """Display the image (RGB or RGBA) using matplotlib."""
    count = dataset.count
    if count < 3:
        print("Warning: less than 3 bands -> showing first band as grayscale")
        img = dataset.read(1)
        plt.imshow(img, cmap="gray")
    else:
        # read RGB(A)
        img = dataset.read([1, 2, 3] + ([4] if count >= 4 else []))
        img = np.moveaxis(img, 0, -1)                # (C,H,W) -> (H,W,C)

        # handle alpha (if present)
        if count >= 4:
            alpha = img[..., 3]
            rgb = img[..., :3]
            # apply alpha to RGB (pre-multiplied is not needed for display)
            rgb = rgb.astype(np.float32) / 255.0
            rgb = np.where(alpha[..., None] > 0, rgb, np.nan)
            plt.imshow(rgb)
        else:
            plt.imshow(img.astype(np.uint8))

    plt.title(Path(dataset.name).name)
    plt.axis("off")
    plt.show()

# ----------------------------------------------------------------------
def main(tiff_path: str):
    if not Path(tiff_path).exists():
        print(f"File not found: {tiff_path}")
        sys.exit(1)

    with rasterio.open(tiff_path) as ds:
        print_gdalinfo_like(ds)
        print("\n" + "="*60 + "\n")
        show_image(ds)

# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Change this to your file name or pass as argument
    default_file = "C:\\Users\\OPER\\OneDrive - Israel Aerospace Industries\\OrthoPhoto\\GeoIsr\\ex1\\sec.tif"
    file_to_use = sys.argv[1] if len(sys.argv) > 1 else default_file
    main(file_to_use)

'''
Driver: GTiff/GTiff
Files: C:\Users\OPER\OneDrive - Israel Aerospace Industries\OrthoPhoto\GeoIsr\ex1\sec.tif
       C:\Users\OPER\OneDrive - Israel Aerospace Industries\OrthoPhoto\GeoIsr\ex1\sec.tif.aux.xml
Size is 23585, 22386
Coordinate System is:
EPSG:4326
GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AXIS["Latitude",NORTH],AXIS["Longitude",EAST],AUTHORITY["EPSG","4326"]]

WKT Components:
Geographic Coordinate System: GEOGCS["WGS 84"
Datum: DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]]
Prime Meridian: PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]]
Unit: UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]]
Axis: AXIS["Latitude",NORTH]
Axis: AXIS["Longitude",EAST]
Authority: AUTHORITY["EPSG","4326"]]
Origin = (34.915688037872314, 32.13128149509433)
Pixel Size = (0.000005364418,-0.000005364418)
Metadata:
  AREA_OR_POINT=Area
  IDENTIFIER=O_united_w84geo_Jun25_gpkg_17
  ZOOM_LEVEL=17
Image Structure Metadata:
  INTERLEAVE=PIXEL
Corner Coordinates:
Upper Left  ( 34.9156880379,  32.1312814951) (34d54'56.48"E, 32d7'52.61"E)
Lower Left  ( 34.9156880379,  32.0111936331) (34d54'56.48"E, 32d0'40.30"E)
Upper Right ( 35.0422078371,  32.1312814951) (35d2'31.95"E, 32d7'52.61"E)
Lower Right ( 35.0422078371,  32.0111936331) (35d2'31.95"E, 32d0'40.30"E)
Center      ( 34.9789479375,  32.0712375641) (34d58'44.21"E, 32d4'16.46"E)
Band 1 Block=1x23585 Type=uint8, ColorInterp=red
  Metadata:
    STATISTICS_APPROXIMATE=YES
    STATISTICS_MAXIMUM=255
    STATISTICS_MEAN=134.57677058523
    STATISTICS_MINIMUM=0
    STATISTICS_STDDEV=42.511971533867
    STATISTICS_VALID_PERCENT=46.72
  Min=0.000 Max=255.000
  Mean=134.577 StdDev=42.512
  Valid Percent=46.72
  Mask Flags: per_dataset alpha
Band 2 Block=1x23585 Type=uint8, ColorInterp=green
  Metadata:
    STATISTICS_APPROXIMATE=YES
    STATISTICS_MAXIMUM=255
    STATISTICS_MEAN=133.00831721155
    STATISTICS_MINIMUM=0
    STATISTICS_STDDEV=36.133773526256
    STATISTICS_VALID_PERCENT=46.72
  Min=0.000 Max=255.000
  Mean=133.008 StdDev=36.134
  Valid Percent=46.72
  Mask Flags: per_dataset alpha
Band 3 Block=1x23585 Type=uint8, ColorInterp=blue
  Metadata:
    STATISTICS_APPROXIMATE=YES
    STATISTICS_MAXIMUM=255
    STATISTICS_MEAN=127.75630251595
    STATISTICS_MINIMUM=0
    STATISTICS_STDDEV=34.489728397704
    STATISTICS_VALID_PERCENT=46.72
  Min=0.000 Max=255.000
  Mean=127.756 StdDev=34.490
  Valid Percent=46.72
  Mask Flags: per_dataset alpha
Band 4 Block=1x23585 Type=uint8, ColorInterp=alpha
  Min=0.000 Max=255.000
  Mean=119.787 StdDev=127.267
  Mask Flags: all_valid


  =======================================================
  ✅ Convert to meters
At latitude ~32° (your image center), 1° ≈ 111,320 m horizontally and ≈ 92,000 m vertically.
So:
Pixel size in meters ≈ 0.000005364418030 × 111,320 ≈ 0.597 m (longitude)
Pixel size in meters ≈ 0.000005364418030 × 92,000 ≈ 0.494 m (latitude)

Approximate ground resolution:
~0.5–0.6 meters per pixel (sub-meter resolution, typical for high-quality aerial imagery).

✅ How to compute generally:

Take Pixel Size from gdalinfo.
If CRS is geographic (EPSG:4326), multiply by:

111,320 m for longitude
111,320 × cos(latitude) for latitude


If CRS is projected (e.g., UTM), pixel size is already in meters.

'''    