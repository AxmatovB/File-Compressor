# 🎬 Max Video Compressor

Max Video Compressor is a lightweight, fast, and highly efficient desktop utility built with Python and Tkinter. It is designed to significantly reduce the size of video files utilizing Hardware (GPU) Acceleration for maximum speed and efficiency.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-orange.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-lightgrey.svg)

## 🌟 Key Features

- **Hardware-Accelerated Compression**: Fast encoding using modern GPU architectures:
  - 🟩 NVIDIA NVENC
  - 🟥 AMD AMF
  - 🟦 Intel QSV
  - ⬜ CPU (libx265 for fallback)
- **High Efficiency (H.265 / HEVC)**: Uses the modern H.265 codec to reduce video file sizes with minimal quality loss.
- **Batch Folder Processing**: Select an entire directory, and the tool will automatically scan and compress all supported video files.
- **Smart Output Management**: Automatically creates an output folder on your Desktop named with today's date (e.g., `Desktop/YYYY-MM-DD/`) and saves all compressed files there.
- **Safe Cancellation**: A built-in cancel button (❌) allows you to stop the compression at any time. It safely cleans up and deletes partially processed files.
- **Clean UI**: A minimalistic, modern, and responsive graphical interface with real-time progress tracking.

## 🛠 Prerequisites

Before running the **source code**, ensure you have the following installed on your system:

1. **Python 3.7+**
2. **FFmpeg**: You must have `ffmpeg.exe` and `ffprobe.exe` placed in the root directory of the project, or installed on your system and added to your `PATH`.
   - Download FFmpeg: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

*(Note: If you are using the compiled `.exe` version, FFmpeg is already bundled inside and you do not need to install anything!)*

## 🚀 Installation & Usage

### Running from Source

1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/max-compressor.git
   cd max-compressor
   ```
2. Run the application:
   ```bash
   python main.py
   ```

### Building a Standalone Executable (.exe)

You can compile this tool into a standalone Windows executable. The following command bundles `ffmpeg.exe` and `ffprobe.exe` directly into the `.exe` so it works out-of-the-box on any PC!

**Using PyInstaller:**
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=compress_setting_repair_tools_zipper_icon_265700.ico --add-binary "ffmpeg.exe;." --add-binary "ffprobe.exe;." --name="Max_Video_Compressor" main.py
```

## 🖥 How to Use

1. Launch the application.
2. **Select your Encoder**: Choose your GPU (NVIDIA, AMD, Intel) or fallback to CPU from the dropdown menu.
3. Click **🎬 Video yuklash (Upload File)**: 
   - Choose a single video file to compress.
4. Or click **📁 Jild yuklash (Upload Folder)**:
   - Select a folder. The application will find all supported videos inside and compress them one by one.
5. The processed files will automatically appear on your Desktop in a folder named with the current date.

## ⚙️ Advanced Settings (For Developers)

You can tweak the compression settings inside `main.py` if you prefer different FFmpeg arguments:
- `QUALITY = 30`: Controls the video quality and file size (CRF/CQ value).

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
