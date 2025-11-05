function create_geographical_dataset(inputTiff, outputDir, blockWidth, blockHeight)
% Create tiles from a large orthophoto and export geographical info
%
% Format of output file:
% filename,center_utm_x,center_utm_y,top_left_utm_x,top_left_utm_y,center_lat,center_lon,width_meters,height_meters

    % Read geospatial metadata
    info = georasterinfo(inputTiff);
    R = info.RasterReference;
    proj = R.ProjectedCRS; % UTM zone 36N (EPSG:32636)

    % Create output folder
    if ~exist(outputDir, 'dir')
        mkdir(outputDir);
    end

    % Output text file
    geoFile = fullfile(outputDir, 'geographical_info.txt');
    fid = fopen(geoFile, 'w');
    fprintf(fid, '# Geographical Information for Orthophoto Tiles\n');
    fprintf(fid, '# Format: filename,center_utm_x,center_utm_y,top_left_utm_x,top_left_utm_y,center_lat,center_lon,width_meters,height_meters\n');

    % Read total raster size
    rasterSize = R.RasterSize;
    totalRows = rasterSize(1);
    totalCols = rasterSize(2);

    % Overlap (50%)
    stepX = blockWidth / 2;
    stepY = blockHeight / 2;

    % Define grid positions
    xPositions = 1:stepX:(totalCols - blockWidth);
    yPositions = 1:stepY:(totalRows - blockHeight);

    % Open large image (use memory-mapped read)
    [~, name, ext] = fileparts(inputTiff);
    fprintf('📷 Processing %s%s\n', name, ext);

    for yi = 1:length(yPositions)
        for xi = 1:length(xPositions)
            % Pixel positions in raster
            x0 = xPositions(xi);
            y0 = yPositions(yi);

            % Compute tile coordinates (in world meters)
            [xTopLeft, yTopLeft] = intrinsicToWorld(R, x0, y0);
            [xCenter, yCenter] = intrinsicToWorld(R, x0 + blockWidth/2, y0 + blockHeight/2);

            % Convert to geographic coordinates (lat/lon)
            [centerLat, centerLon] = projinv(proj, xCenter, yCenter);

            % Create filename
            filename = sprintf('imgdb_%d_%d.tif', round(xCenter), round(yCenter));

            if 0
                filepath = fullfile(outputDir, filename);

                % Read and save tile (optional for testing)
                tile = readgeoraster(inputTiff, 'OutputType', 'uint8', ...
                    'PixelRegion', {[y0 y0+blockHeight-1], [x0 x0+blockWidth-1]});
                imwrite(tile, filepath);
            end

            % Write line to text file
            fprintf(fid, '%s,%.2f,%.2f,%.2f,%.2f,%.6f,%.6f,%.1f,%.1f\n', ...
                filename, xCenter, yCenter, xTopLeft, yTopLeft, ...
                centerLat, centerLon, blockWidth*R.CellExtentInWorldX, blockHeight*R.CellExtentInWorldY);
        end
    end

    fclose(fid);
    fprintf('✅ Done! File saved: %s\n', geoFile);
end
