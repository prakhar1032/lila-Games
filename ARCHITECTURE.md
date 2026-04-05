# Architecture — LILA BLACK Player Journey Viz

## What I Built & Why

| Decision   | Choice             | Reason                                                                                     |
| ---------- | ------------------ | ------------------------------------------------------------------------------------------ |
| Framework  | Streamlit          | Zero frontend build overhead; Level Designers need a working tool fast, not a polished SPA |
| Data layer | Pandas + PyArrow   | Native parquet support; fast enough for 89K rows                                           |
| Rendering  | Matplotlib + SciPy | Fine-grained control over layering; gaussian_filter for smooth heatmaps                    |
| Hosting    | Streamlit Cloud    | Free, one-click deploy from GitHub, shareable URL                                          |

## Data Flow

```
data/February_XX/*.nakama-0
        ↓ pyarrow.read_table()
        ↓ pd.concat() across all dates
        ↓ decode event bytes → string
        ↓ detect bots (numeric user_id)
        ↓ sidebar filters (map → date → match)
        ↓ world_to_pixel(x, z, cfg)
        ↓ matplotlib layers: minimap → heatmap → paths → markers
        ↓ st.pyplot() rendered in browser
```

## Coordinate Mapping — The Tricky Part

The README provided exact values per map:

```
u = (x - origin_x) / scale
v = (z - origin_z) / scale
pixel_x = u * 1024
pixel_y = (1 - v) * 1024   ← Y-flip because image origin is top-left
```

| Map           | Scale | Origin X | Origin Z |
| ------------- | ----- | -------- | -------- |
| AmbroseValley | 900   | -370     | -473     |
| GrandRift     | 581   | -290     | -290     |
| Lockdown      | 1000  | -500     | -500     |

Key insight: `y` column is elevation (3D height), not a map axis — ignored for 2D plotting.

## Assumptions Made

| Ambiguity                                               | Assumption                                           |
| ------------------------------------------------------- | ---------------------------------------------------- |
| `ts` column stores ms since match start, not wall clock | Treated as relative time; used for timeline ordering |
| February 14 is partial                                  | Loaded as-is with a note; no special handling needed |
| Out-of-bounds coordinates exist                         | Filtered out (px/py outside 0–1024)                  |
| BotKill / BotKilled not in original event list          | Added to EVENT_STYLE with distinct orange markers    |

## Major Tradeoffs

| Option A                | Option B                    | Decision                                                                       |
| ----------------------- | --------------------------- | ------------------------------------------------------------------------------ |
| Streamlit (Python)      | React + D3                  | Streamlit — faster to ship, Level Designers don't need real-time interactivity |
| Data-driven bounds      | README hardcoded values     | README values — more accurate, validated against actual game coordinate system |
| hexbin heatmap          | gaussian smooth heatmap     | Gaussian — cleaner visual, no grid artifacts                                   |
| Load one date at a time | Load all data once + filter | Load all once + cache — better UX, Streamlit cache handles memory              |
