% MATLAB script to read two geographical_info.txt files, compute the overlapping area using UTM coordinates,
% and plot the regions along with the overlap.

% Define the file paths (update these to your actual file locations)
file1 = 'C:\Users\micha\OneDrive - Israel Aerospace Industries\OrthoPhoto\GeoIsr\ex4\Tiles\geographical_info.txt';  % e.g., 'C:\data\geographical_info.txt'
file2 = 'C:\Users\micha\OneDrive - Israel Aerospace Industries\OrthoPhoto\Jerusalem\Tiles\geographical_info.txt'; % e.g., 'D:\other\geographical_info.txt'

% Read the tables, skipping comment lines starting with '#'
T1 = readtable(file1, 'Delimiter', ',', 'CommentStyle', '#', 'ReadVariableNames', false);
T2 = readtable(file2, 'Delimiter', ',', 'CommentStyle', '#', 'ReadVariableNames', false);

% Function to create a union polyshape from the tiles in a table
function ps = tiles_to_polyshape(T)
    ps = polyshape();  % Start with an empty polyshape
    for i = 1:height(T)
        tl_x = T.Var4(i);      % top_left_utm_x
        tl_y = T.Var5(i);      % top_left_utm_y
        w = T.Var8(i);         % width_meters
        h = T.Var9(i);         % height_meters
        
        % Define the rectangle coordinates (closing the polygon)
        x = [tl_x, tl_x + w, tl_x + w, tl_x, tl_x];
        y = [tl_y, tl_y, tl_y - h, tl_y - h, tl_y];
        
        ps_tile = polyshape(x, y);
        ps = union(ps, ps_tile);  % Union with the accumulating polyshape
    end
end

% Create union polyshapes for each file
ps1 = tiles_to_polyshape(T1);
ps2 = tiles_to_polyshape(T2);

% Compute the intersection (overlap)
ps_overlap = intersect(ps1, ps2);

% Compute and display the overlap area in square meters
overlap_area = area(ps_overlap);
disp(['Overlap area: ', num2str(overlap_area), ' square meters']);

% Plot the regions and overlap
figure;
plot(ps1, 'FaceColor', 'red', 'FaceAlpha', 0.5, 'EdgeColor', 'k');
hold on;
plot(ps2, 'FaceColor', 'blue', 'FaceAlpha', 0.2, 'EdgeColor', 'b','LineWidth',3);
plot(ps_overlap, 'FaceColor', 'green', 'FaceAlpha', 0.8, 'EdgeColor', 'k');
axis equal;
legend('Region 1 (File 1)', 'Region 2 (File 2)', 'Overlap');
title('Geographical Regions and Overlap');
xlabel('UTM X (meters)');
ylabel('UTM Y (meters)');
grid on;