# 🎵 Audio Normalizer GUI Toolkit

A complete Python toolkit for LUFS normalization and True Peak limiting of audio files. Supports both full track processing and sample normalization by instrument category.

---

## 🚀 Features
- Normalize full tracks for platforms like **YouTube, Spotify, Apple Music, DJ Live**.
- Batch normalize samples by instrument type (**kick**, **bass**, **fx**, etc.) with preset LUFS/TP targets.
- GUI built with `Tkinter`.
- Export in `.wav`, `.mp3`, `.flac`.
- Optional `.zip` export after normalization.

---

## 📦 Where to Place the Scripts
This toolkit is designed to be used inside the official **FFmpeg for Windows** package for better portability.

### 📥 Download FFmpeg
- Go to the official FFmpeg site: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
- Choose: **Windows > gpl > full/shared build**
- Extract the archive anywhere on your PC, for example:
```
C:/Users/YourName/Documents/ffmpeg-master-latest-win64-gpl-shared/
```

### 📂 Inside that folder, go to:
```
ffmpeg-master-latest-win64-gpl-shared/bin/
```
Place the following files inside `bin/`:
- `Normalise_track.py`  → to normalize full-length tracks
- `Normaliser_sample.py` → to batch normalize categorized samples

These scripts will use the `ffmpeg.exe` already included in this folder.

---

## 🧱 Final Folder Structure
```
ffmpeg-master-latest-win64-gpl-shared/
├── bin/
│   ├── ffmpeg.exe              # Already included in the FFmpeg zip
│   ├── ffprobe.exe             # Already included
│   ├── Normaliser_sample.py   # Copy here
│   ├── Normalise_track.py     # Copy here
├── README.md                  # Optional
├── requirements.txt           # For Python dependencies
└── .venv/                     # Your virtual environment (recommended)
```

---

## 🖥️ Installation (First Time Only)
### ✅ 1. Open a terminal and navigate to the `bin/` folder
```bash
cd path/to/ffmpeg-master-latest-win64-gpl-shared/bin
```

### ✅ 2. Create and activate a virtual environment (optional but recommended)
```bash
python -m venv ../.venv
../.venv/Scripts/activate        # On Windows
```

### ✅ 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

Contents of `requirements.txt`:
```
pydub
tk
ffmpeg-python
```

---

## ▶️ How to Use
### 🎧 Normalize a full track
```bash
python Normalise_track.py
```
- Choose your input/output folders
- Select target platform (Spotify, YouTube, etc.) or use manual LUFS/TP sliders
- Export in chosen format

### 🥁 Normalize samples by instrument
```bash
python Normaliser_sample.py
```
- Select one folder per instrument (e.g. `kick/`, `fx/`, `vocal/`...)
- Choose your output directory and desired format
- (Optional) Create a ZIP archive with all normalized results

---

## 🧠 Future Features (planned)
- CSV log for each file (input LUFS, gain applied, output LUFS)
- Save/load user presets
- Visual waveform preview before/after
- Auto-detection of instrument type using AI

---

## ⚠️ Disclaimer
Auto-normalization is a technical assistant—not a replacement for your ears. Always check your output files after batch processing, especially in creative or dynamic genres like **psytrance**, **darkpsy**, **ambient**, or **experimental**.

---

🎶 Happy mastering!


