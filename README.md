# LILA BLACK — Player Journey Visualization Tool

A web-based tool for Level Designers to explore player behavior across LILA BLACK's maps.

## Live Demo

🔗 [[deployed URL](https://lila-black-map.streamlit.app)]

## Tech Stack

- **Python + Streamlit** — fast prototyping, no frontend build step needed
- **Pandas + PyArrow** — parquet parsing
- **Matplotlib + SciPy** — map rendering, smooth heatmaps
- **Pillow** — minimap image loading

## Setup

### 1. Install dependencies

```bash
pip install streamlit pandas pyarrow matplotlib scipy pillow
```

### 2. Folder structure

```
LILA GAMES/
├── app.py
├── minimaps/
│   ├── AmbroseValley_Minimap.png
│   ├── GrandRift_Minimap.png
│   └── Lockdown_Minimap.jpg
└── data/
    ├── February_10/
    ├── February_11/
    ├── February_12/
    ├── February_13/
    └── February_14/
```

### 3. Run

```bash
streamlit run app.py
```

## Features

- Filter by Map → Date → Match
- Traffic / Kill Zone / Death Zone heatmaps (toggle independently)
- Player paths — green = human, cyan = bot
- Event markers — kills, deaths, loots, storm kills
- Timeline slider to scrub through match progression
- Metrics bar showing players, kills, deaths, loots per match
