# -*- coding: utf-8 -*-
import arcpy
import math
import os

# ------------------------------------------------------------------
# Drubo & Team - GIS Geometry Experiment
# Purpose: Create a TRUE mathematical offset for polygons
# (because the standard buffer tool was giving us messy results on concave corners)
# ------------------------------------------------------------------

print("Starting custom geometric offset...")

# paths - adjust these if running on a different machine
gdb = r"D:\Drubo_IWM\Georeferencing\Buffer Practice\New File Geodatabase.gdb"
input_fc = os.path.join(gdb, "Plot")
output_fc = os.path.join(gdb, "Plot_true_math_offset_5m")

# The magic number: how far to offset (meters)
offset_dist = 5.0
arcpy.env.overwriteOutput = True


# --------------------------------------------------
# GEOMETRY LOGIC
# We are doing this manually with vectors to control the exact output.
# --------------------------------------------------

def unit_normal(p1, p2):
    """
    Calculates the perpendicular unit vector for an edge.
    We need this to know which direction to 'push' the line.
    """
    dx = p2.X - p1.X
    dy = p2.Y - p1.Y
    L = math.sqrt(dx*dx + dy*dy)

    if L == 0:
        return 0.0, 0.0

    # Rotate 90 degrees counter-clockwise and normalize
    nx = -dy / L
    ny = dx / L
    return nx, ny


def offset_line(p1, p2, dist):
    """
    Shifts a line segment by 'dist' units along its normal vector.
    This creates the parallel edge we need.
    """
    nx, ny = unit_normal(p1, p2)
    p1o = arcpy.Point(p1.X + nx * dist, p1.Y + ny * dist)
    p2o = arcpy.Point(p2.X + nx * dist, p2.Y + ny * dist)
    return p1o, p2o


def line_intersection(a1, a2, b1, b2):
    """
    Standard linear algebra to find where two infinite lines cross.
    Essential for finding the new 'corner' vertex.
    """
    x1, y1 = a1.X, a1.Y
    x2, y2 = a2.X, a2.Y
    x3, y3 = b1.X, b1.Y
    x4, y4 = b2.X, b2.Y

    denom = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)

    # Parallel lines don't intersect (denominator is approx 0)
    if abs(denom) < 1e-9:
        return None

    px = ((x1*y2 - y1*x2)*(x3-x4) - (x1-x2)*(x3*y4 - y3*x4)) / denom
    py = ((x1*y2 - y1*x2)*(y3-y4) - (y1-y2)*(x3*y4 - y3*x4)) / denom

    return arcpy.Point(px, py)


# --------------------------------------------------
# MAIN EXECUTION
# --------------------------------------------------

print("Reading input geometry...")
geom = None

# Using a standard search cursor to grab the shape
with arcpy.da.SearchCursor(input_fc, ["SHAPE@"]) as cur:
    for row in cur:
        geom = row[0]
        break 

if geom is None:
    raise Exception("Error: Input is empty? No polygon found.")


# Step 1: Extract vertices
# We need them in order to traverse the boundary
vertices = []

for part in geom:
    for p in part:
        if p:
            vertices.append(p)

# Formatting check: remove the duplicate closing point if it exists
if len(vertices) > 1 and vertices[0].equals(vertices[-1]):
    vertices.pop()

n = len(vertices)
print("Found {0} vertices.".format(n))

if n < 3:
    raise Exception("Not enough vertices to form a polygon!")


# Step 2: Calculate the new offset vertices
# We iterate through every corner, find the two adjacent edges, 
# offset them, and find where they meet.
offset_pts = []

for i in range(n):
    # Grab the triplet: Previous, Current, Next
    p_prev = vertices[i - 1]
    p_curr = vertices[i]
    p_next = vertices[(i + 1) % n]

    # Create the two parallel lines
    l1_p1, l1_p2 = offset_line(p_prev, p_curr, offset_dist)
    l2_p1, l2_p2 = offset_line(p_curr, p_next, offset_dist)

    # Find the new corner
    inter = line_intersection(l1_p1, l1_p2, l2_p1, l2_p2)

    if inter:
        offset_pts.append(inter)

print("Calculated {0} new vertices for the offset polygon.".format(len(offset_pts)))

if len(offset_pts) < 3:
    raise Exception("Failed to generate enough points for the new polygon.")


# Step 3: Rebuild and Save
# Stitch the points back into an ArcPy Geometry object
print("Reconstructing polygon...")

arr = arcpy.Array(offset_pts)
arr.add(offset_pts[0])  # Close the ring manually

offset_polygon = arcpy.Polygon(arr, geom.spatialReference)

# Save to file
if arcpy.Exists(output_fc):
    arcpy.Delete_management(output_fc)

arcpy.CopyFeatures_management(offset_polygon, output_fc)

print("--------------------------------------------------")
print("SUCCESS: Offset polygon created.")
print("Output saved at: " + output_fc)
print("--------------------------------------------------")
