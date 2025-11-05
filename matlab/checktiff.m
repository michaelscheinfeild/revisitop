%{
 Option 1: Export from QGIS as UTM

In QGIS:

Right-click your raster → Export → Save As...

In “CRS”, choose EPSG:32636 – WGS 84 / UTM zone 36N

Save and reopen in MATLAB.
Now R will be a MapCellsReference and R.ProjectedCRS will exist. 


------------
Option 1 — Export again from QGIS in UTM 36N

In QGIS:

Right-click raster → Export → Save As...

Under CRS, select EPSG:32636 — WGS 84 / UTM zone 36N

Save the file and reload it in MATLAB:


------------
image
Option 1 — Re-export from QGIS (the safe way)

In QGIS, open your map with the image layer (even if it’s an imported .tif).

In the Layers panel, right-click the image layer → choose
Export → Save As...
(In older QGIS it might be Raster → Conversion → Translate (Convert format).)

In the dialog:

Format: GeoTIFF (*.tif)

CRS: click the CRS selector button 🌍 → type 32636 → choose
“WGS 84 / UTM zone 36N (EPSG:32636)”

Extent: leave as “Layer extent” unless you want to crop.

Resolution: keep the same as the original.

Check only the layer you’re exporting (others can remain unchecked).

Output file: choose a new filename, e.g. image_utm36n.tif.

Click OK / Run / Export.

Back in MATLAB, run:

-----------
Re-export the layer as UTM (EPSG:32636)

Right-click the layer (your .tif) in the Layers panel.

Choose Save As…

In the dialog that appears:

Format: GeoTIFF (*.tif)

CRS:

Click the small globe 🌍 button next to CRS.

In the search bar, type 32636.

Select “WGS 84 / UTM zone 36N (EPSG:32636)”.

Extent:

Usually “Layer extent” is fine.

Resolution:

Keep “Original” or the same cell size as the input.

File name / Output file:

Choose a new file name (e.g., my_image_UTM36N.tif).

Click OK or Run.

🧠 Option 3: Export without resampling

When exporting from QGIS:

Check the box “Keep resolution of input raster”.

Leave “Target resolution” blank (QGIS will preserve the original grid).

This minimizes interpolation and color changes.

%}

infoA = georasterinfo('C:\Users\micha\OneDrive - Israel Aerospace Industries\OrthoPhoto\Jerusalem\Jer_Ortho_2018_3AY_2AY.tif');
infoB = georasterinfo('C:\Users\micha\OneDrive - Israel Aerospace Industries\OrthoPhoto\GeoIsr\ex3\aIlan.tif');

%info = georasterinfo('Jer_Ortho_2018_3AY_2AY.tif')
if 0
info.Filename(1)
info.Filename(2)

info.RasterSize

info.NumBands
info.RasterReference
info.RasterReference.ProjectedCRS
info.RasterReference.ProjectedCRS.GeographicCRS
info.RasterReference.ProjectedCRS.GeographicCRS.Spheroid
info.RasterReference.ProjectedCRS.ProjectionParameters

info.CoordinateReferenceSystem
info.CoordinateReferenceSystem.GeographicCRS
info.CoordinateReferenceSystem.GeographicCRS.Spheroid

info.Metadata
end

blockWidth = 1120;   % pixels
blockHeight = 700;   % pixels

if 0
inputTiff = 'C:\Users\micha\OneDrive - Israel Aerospace Industries\OrthoPhoto\Jerusalem\Jer_Ortho_2018_3AY_2AY.tif';
outputDir = 'C:\Users\micha\OneDrive - Israel Aerospace Industries\OrthoPhoto\Jerusalem\Tiles';



create_geographical_dataset(inputTiff, outputDir, blockWidth, blockHeight);
end

inputTiff = "C:\Users\micha\OneDrive - Israel Aerospace Industries\OrthoPhoto\GeoIsr\ex4\Roshjer.tif"
outputDir = "C:\Users\micha\OneDrive - Israel Aerospace Industries\OrthoPhoto\GeoIsr\ex4\Tiles"
create_geographical_dataset(inputTiff, outputDir, blockWidth, blockHeight);

%[A, R] = readgeoraster(inputTiff);


%{
 CoordinateSystemType: 'geographic'
GeographicCRS: WGS 84 (EPSG:4326)
AngleUnit: degree
So the raster is in latitude/longitude, not UTM (meters).
That’s why MATLAB gave you the error — there is no .ProjectedCRS field for this raster type.   

What it means

The coordinates in the raster are in degrees, not meters.

QGIS probably exported the file in the default CRS (EPSG:4326) instead of UTM zone 36N (EPSG:32636).

MATLAB sees it as a GeographicCellsReference, hence R.ProjectedCRS doesn’t exist — only R.GeographicCRS does.

%}