# 🎮 LILA BLACK — Player Journey Visualization Tool

A web-based tool for Level Designers to visually explore player behavior across LILA BLACK's three maps.

## 🔗 Live Demo
**https://lila-games-map.streamlit.app**

> ⚠️ **App is hosted on Streamlit Cloud free tier.**
> If you see an **"Oh no"** error screen — click **"Manage app"** (bottom right) → **"Reboot app"**. Back up in 30 seconds.
>
> ![Streamlit Error Screen](docs/error.png)

---

## Tech Stack

| Layer | Tool | Why |
|-------|------|-----|
| Frontend + Server | Streamlit | Zero build step, fast prototyping, perfect for internal tools |
| Data Parsing | Pandas + PyArrow | Native parquet support, fast enough for 89K rows |
| Map Rendering | Matplotlib + SciPy | Full layer control; gaussian_filter for smooth heatmaps |
| Image Handling | Pillow | Minimap PNG/JPG loading |
| Hosting | Streamlit Cloud | Free, one-click GitHub deploy |

---

## Setup

### 1. Install dependencies
```bash
pip install streamlit pandas pyarrow matplotlib scipy pillow numpy
```

### 2. Folder structure
```
LILA GAMES/
├── app.py
├── requirements.txt
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

### 3. Run locally
```bash
streamlit run app.py
```

---

## Features

| Feature | Description |
|---------|-------------|
| **Map → Date → Match filter** | Drill down from map to specific match |
| **Traffic Heatmap** | Smooth gaussian heatmap of all player movement |
| **Kill Zone Heatmap** | Red overlay where kills are concentrated |
| **Death Zone Heatmap** | Blue overlay where deaths are concentrated |
| **Player Paths** | Green = human, Cyan = bot |
| **Event Markers** | Kill (×), Death (▽), Loot (★), Storm Kill (◆) |
| **Timeline Slider** | Scrub through match progression by timestamp |
| **Metrics Bar** | Players, Humans, Bots, Kills, Deaths, Loots per match |

---

## ⚠️ If App Shows "Oh no" Error

![Error Screen](docs/error.png)

**Steps to fix in 30 seconds:**
1. Go to **https://lila-games-map.streamlit.app**
2. Click **"Manage app"** button — bottom right corner
3. Click **"Reboot app"**
4. Wait 30 seconds ✅
