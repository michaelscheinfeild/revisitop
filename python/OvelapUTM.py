import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Function to compute the union area of a list of rectangles using sweep line algorithm
def compute_union_area(rectangles):
    if not rectangles:
        return 0.0
    
    events = []
    for x1, y1, x2, y2 in rectangles:
        events.append((x1, y1, y2, 's'))
        events.append((x2, y1, y2, 'e'))
    
    events.sort(key=lambda x: x[0])
    
    ans = 0.0
    prevX = events[0][0]
    yPairs = []
    
    def getHeight(yPairs):
        height = 0.0
        prevY = float('-inf')
        
        for y1, y2 in yPairs:
            prevY = max(prevY, y1)
            if y2 > prevY:
                height += y2 - prevY
                prevY = y2
        
        return height
    
    for currX, y1, y2, typ in events:
        if currX > prevX:
            width = currX - prevX
            ans += width * getHeight(yPairs)
            prevX = currX
        if typ == 's':
            yPairs.append((y1, y2))
            yPairs.sort()
        else:  # typ == 'e'
            yPairs.remove((y1, y2))
    
    return ans

# Define the file paths (update these to your actual file locations)


file1 = r'C:\Users\micha\OneDrive - Israel Aerospace Industries\OrthoPhoto\GeoIsr\ex4\Tiles\geographical_info.txt'
file2 = r'C:\Users\micha\OneDrive - Israel Aerospace Industries\OrthoPhoto\Jerusalem\Tiles\geographical_info.txt'


# Read the tables, skipping comment lines starting with '#'
df1 = pd.read_csv(file1, delimiter=',', comment='#', header=None, usecols=[3,4,7,8], names=['tl_x', 'tl_y', 'w', 'h'])
df2 = pd.read_csv(file2, delimiter=',', comment='#', header=None, usecols=[3,4,7,8], names=['tl_x', 'tl_y', 'w', 'h'])

# Create lists of rectangles (minx, miny, maxx, maxy)
rects1 = []
for row in df1.itertuples():
    x1 = row.tl_x
    y2 = row.tl_y
    x2 = row.tl_x + row.w
    y1 = row.tl_y - row.h
    rects1.append([x1, y1, x2, y2])

rects2 = []
for row in df2.itertuples():
    x1 = row.tl_x
    y2 = row.tl_y
    x2 = row.tl_x + row.w
    y1 = row.tl_y - row.h
    rects2.append([x1, y1, x2, y2])

# Compute pairwise intersection rectangles
overlap_rects = []
for r1 in rects1:
    for r2 in rects2:
        ix1 = max(r1[0], r2[0])
        iy1 = max(r1[1], r2[1])
        ix2 = min(r1[2], r2[2])
        iy2 = min(r1[3], r2[3])
        if ix1 < ix2 and iy1 < iy2:
            overlap_rects.append([ix1, iy1, ix2, iy2])

# Compute the overlap area as the union area of the intersection rectangles
overlap_area = compute_union_area(overlap_rects)
print(f'Overlap area: {overlap_area} square meters')
overlap_area_hectares = overlap_area / 10000
print(f'Overlap area: {overlap_area_hectares:.2f} hectares')

# Plot the regions and overlap
fig, ax = plt.subplots()
# Plot region 1
for r in rects1:
    x1, y1, x2, y2 = r
    ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, facecolor='red', alpha=0.5, edgecolor='k'))
# Plot region 2
for r in rects2:
    x1, y1, x2, y2 = r
    ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, facecolor='blue', alpha=0.5, edgecolor='k'))
# Plot overlaps with hatch for visibility (vertical lines; change to '.' for dots)
for r in overlap_rects:
    x1, y1, x2, y2 = r
    ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, facecolor='green', alpha=0.3, hatch='|', edgecolor='k'))

ax.set_aspect('equal')
ax.set_xlabel('UTM X (meters)')
ax.set_ylabel('UTM Y (meters)')
ax.legend(['Region 1 (File 1)', 'Region 2 (File 2)', 'Overlap'])
ax.set_title('Geographical Regions and Overlap')
ax.grid(True)
plt.show()