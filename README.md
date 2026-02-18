# True Mathematical Polygon Offset

**A pure geometric approach to handling convex & concave polygon offsets.**

## Why we built this
We were working on a standard GIS task involving polygon buffers, but we kept running into issues with standard tools:
*   **Messy topology** on concave corners.
*   **Self-intersections** that ruined the geometry.
*   **Inconsistent distances** in some edge cases.

We realized we needed a solution that respected the **mathematical vectors** of the geometry, rather than just a raster-style buffer or a standard tool approximation. This script is the result of that experiment—a vector-based offset engine built from scratch.

---

## How it works (The Math)

Instead of relying on a "black box" tool, we broke it down into vector logic:

1.  **Extract Vertices**: We grab the ordered points of the polygon.
2.  **Calculate Normals**: For every edge, we compute the perpendicular unit vector.
3.  **Shift Edges**: We generate "virtual" infinite lines parallel to the original edges at the set offset distance.
4.  **Find Intersections**: We calculate exactly where these new lines intersect to form the new corners.
5.  **Rebuild**: We stitch the new intersection points into a clean, topological valid polygon.

### The Logic Chain
`Input Polygon` -> `Vectors` -> `Normals` -> `Offset Intersection` -> `Clean Output`

---

## Results
This approach gives us a **clean, mathematically perfect offset** that handles both convex and concave shapes without the usual artifacts.

*   No self-intersections.
*   Uniform distance on all sides.
*   Works purely on coordinate geometry.

---

## Tech Stack
*   Python
*   ArcPy (for reliable I/O)
*   Linear Algebra (the core logic)

---

## Authors
Developed by **Drubo** and the team during a deep-dive into computational geometry.
Repositories: [GitHub](https://github.com/DruboPaul/true-polygon-offset)

> "Real engineering begins where ready-made tools stop working."
