info = georasterinfo('C:\gitRepo\ImagesOrtho\68c01a6e11d12c7707b61834.tif');

%{

Image size (rows × cols)
[10029 13209]

[39048 81720]

Coordinate system (if available)

Spatial extent (bounding box in map coordinates)
%}
disp(info);



%% read geo
[A, R] = readgeoraster('C:\gitRepo\ImagesOrtho\68c01a6e11d12c7707b61834.tif');

% Downsample for fast display
factor = 100; 
A_small = A(1:factor:end, 1:factor:end, :);

figure;
imshow(A_small);
title('Downsampled orthophoto');



%%  read roi
[A, R] = readgeoraster('68bfba20589c103ce6106132.tif');

% Example crop: rows 1000–2000, cols 1500–2500
rowWin = 1000:2000;
colWin = 1500:2500;
A_crop = A(rowWin, colWin, :);

figure;
imshow(A_crop);
title('Cropped window from orthophoto');



%% inspect pixel
info = georasterinfo('68bfba20589c103ce6106132.tif');
R = info.RasterReference;

row = 4000;
col = 7000;

[xWorld, yWorld] = intrinsicToWorld(R, col, row);
fprintf('Pixel (%d,%d) = Map coords (%.2f, %.2f)\n', row, col, xWorld, yWorld);

%% interactive

[A, R] = readgeoraster('68bfba20589c103ce6106132.tif');

% Coarse preview
previewFactor = 20; % every 20th pixel
A_preview = A(1:previewFactor:end, 1:previewFactor:end, :);

figure;
imshow(A_preview);
title('Preview of orthophoto');

figure;
imshow(A_preview);
title('Click to explore pixels');

dcm = datacursormode(gcf);
set(dcm, 'Enable', 'on');


