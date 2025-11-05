import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch

# Function to compute the union area of a list of rectangles using sweep line algorithm
def compute_union_area(rectangles):
    if not rectangles:
        return 0.0
    
    events = []
    for x1, y1, x2, y2 in rectangles:
        events.append((x1, y1, y2, 0))  # 0 for start
        events.append((x2, y1, y2, 1))  # 1 for end
    
    events.sort(key=lambda e: (e[0], e[3]))  # sort by x, then starts before ends
    
    ans = 0.0
    prevX = events[0][0]
    yPairs = []
    
    def getHeight():
        height = 0.0
        prevY = float('-inf')
        for y1, y2 in sorted(yPairs):
            prevY = max(prevY, y1)
            if y2 > prevY:
                height += y2 - prevY
                prevY = y2
        return height
    
    for currX, y1, y2, typ in events:
        if currX > prevX:
            width = currX - prevX
            ans += width * getHeight()
            prevX = currX
        if typ == 0:  # start
            yPairs.append((y1, y2))
        else:  # end
            yPairs.remove((y1, y2))
    
    return ans

# Define the file paths (update these to your actual file locations)
file1 = r'C:\Users\micha\OneDrive - Israel Aerospace Industries\OrthoPhoto\GeoIsr\ex4\Tiles\geographical_info.txt'
file2 = r'C:\Users\micha\OneDrive - Israel Aerospace Industries\OrthoPhoto\Jerusalem\Tiles\geographical_info.txt'


# Read the tables, skipping comment lines starting with '#'
df1 = pd.read_csv(file1, delimiter=',', comment='#', header=None, usecols=[3,4,7,8], names=['tl_x', 'tl_y', 'w', 'h'])
df2 = pd.read_csv(file2, delimiter=',', comment='#', header=None, usecols=[3,4,7,8], names=['tl_x', 'tl_y', 'w', 'h'])

# Create lists of rectangles (minx, miny, maxx, maxy)
rects1 = [[row.tl_x, row.tl_y - row.h, row.tl_x + row.w, row.tl_y] for row in df1.itertuples(index=False)]
rects2 = [[row.tl_x, row.tl_y - row.h, row.tl_x + row.w, row.tl_y] for row in df2.itertuples(index=False)]

# Compute union areas for efficient overlap calculation (avoids pairwise for area)
area1 = compute_union_area(rects1)
area2 = compute_union_area(rects2)
area_union = compute_union_area(rects1 + rects2)
overlap_area = area1 + area2 - area_union
print(f'Overlap area: {overlap_area} square meters')

# Still need pairwise for plotting overlaps (if too slow, comment out the overlap plotting loop)
overlap_rects = []
for r1 in rects1:
    for r2 in rects2:
        ix1 = max(r1[0], r2[0])
        iy1 = max(r1[1], r2[1])
        ix2 = min(r1[2], r2[2])
        iy2 = min(r1[3], r2[3])
        if ix1 < ix2 and iy1 < iy2:
            overlap_rects.append([ix1, iy1, ix2, iy2])

# Plot the regions and overlap
fig, ax = plt.subplots()
# Plot region 1
for r in rects1:
    ax.add_patch(Rectangle((r[0], r[1]), r[2] - r[0], r[3] - r[1], facecolor='red', alpha=0.5, edgecolor='k'))
# Plot region 2
for r in rects2:
    ax.add_patch(Rectangle((r[0], r[1]), r[2] - r[0], r[3] - r[1], facecolor='blue', alpha=0.5, edgecolor='k'))
# Plot overlaps with hatch for visibility (vertical lines; change to '.' for dots)
for r in overlap_rects:
    ax.add_patch(Rectangle((r[0], r[1]), r[2] - r[0], r[3] - r[1], facecolor='green', alpha=0.3, hatch='|', edgecolor='k'))

# Set axis limits based on all rectangles
all_rects = rects1 + rects2
if all_rects:
    min_x = min(r[0] for r in all_rects)
    max_x = max(r[2] for r in all_rects)
    min_y = min(r[1] for r in all_rects)
    max_y = max(r[3] for r in all_rects)
    
    print(f"X range: {min_x} to {max_x}")
    print(f"Y range: {min_y} to {max_y}")
    
    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)

ax.set_aspect('equal')
ax.set_xlabel('UTM X (meters)')
ax.set_ylabel('UTM Y (meters)')
legend_elements = [
    Patch(facecolor='red', alpha=0.5, edgecolor='k', label='Region 1 (File 1)'),
    Patch(facecolor='blue', alpha=0.5, edgecolor='k', label='Region 2 (File 2)'),
    Patch(facecolor='green', alpha=0.3, hatch='|', edgecolor='k', label='Overlap')
]
ax.legend(handles=legend_elements)
ax.set_title('Geographical Regions and Overlap')
ax.grid(True)

plt.savefig('overlap_analysis_fast.png', dpi=300, bbox_inches='tight')
plt.show()