# 🦡 DL Mongoose

> Fast • Clean • Unstoppable — YouTube Downloader

---

## Features

- 🎬 Download YouTube videos (Best / 1080p / 720p / 480p / 360p)
- 🎵 Download YouTube Music as MP3 (320 / 256 / 192 / 128 kbps)
- 📋 Queue system — add multiple links, cancel/remove anytime
- ⚡ Real-time download speed + percentage
- 📁 Download history with file management
- 🔴 Auto internet connection detection
- ⊟ Minimize to system tray
- 🌌 Glassmorphism dark aurora UI
- 💛 Support creator button

---

## Setup & Build (Windows)

### Prerequisites

1. **Python 3.11+** — https://python.org
2. **FFmpeg** — https://ffmpeg.org/download.html
   - Download, extract, add `bin` folder to your PATH
   - Required for MP3 conversion and video merging
3. **Inno Setup** — https://jrsoftware.org/isinfo.php
   - Only needed to create the installer

### Build Steps

```bash
# 1. Clone this repo
git clone https://github.com/yourusername/dl-mongoose
cd dl-mongoose

# 2. Run the build script
build.bat

# 3. Open installer.iss in Inno Setup Compiler
# 4. Click Build > Compile
# 5. Find DLMongoose_Setup_v1.0.0.exe in installer_output/
```

### Manual Build

```bash
pip install -r requirements.txt
pip install pyinstaller
pyinstaller dl_mongoose.spec --clean
```

---

## File Structure

```
dlmongoose/
├── main.py              # Main application
├── requirements.txt     # Python dependencies
├── dl_mongoose.spec     # PyInstaller config
├── installer.iss        # Inno Setup installer script
├── build.bat            # One-click build script
├── assets/
│   ├── mongoose.ico     # App icon (you add this)
│   ├── installer_banner.bmp
│   └── installer_icon.bmp
└── README.md
```

---

## Adding Your Icon

1. Create or commission a mongoose vs snake logo
2. Convert to `.ico` format (256x256, 128x128, 64x64, 32x32, 16x16 sizes)
3. Save as `assets/mongoose.ico`
4. Rebuild

Free icon converter: https://convertio.co/png-ico/

---

## Distribution via GitHub

1. Build the installer EXE
2. Go to your GitHub repo → Releases → New Release
3. Tag: `v1.0.0`
4. Upload `DLMongoose_Setup_v1.0.0.exe`
5. Users download and double-click — done

---

## Support

Buy Me a Coffee: https://buymeacoffee.com/dlmongoose

---

## Tech Stack

- Python 3.11
- CustomTkinter (UI)
- yt-dlp (downloading)
- PyInstaller (EXE packaging)
- Inno Setup (installer)
- pystray (system tray)
