import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
from pathlib import Path
import threading
import os
import re
from datetime import datetime
import sys

if hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

FFMPEG_EXE = os.path.join(base_path, "ffmpeg.exe")
FFPROBE_EXE = os.path.join(base_path, "ffprobe.exe")

if not os.path.exists(FFMPEG_EXE):
    FFMPEG_EXE = "ffmpeg"
if not os.path.exists(FFPROBE_EXE):
    FFPROBE_EXE = "ffprobe"

# ==============================
# SETTINGS & GLOBALS
# ==============================

# CRF / CQ level around 30 gives excellent compression for H265
QUALITY = 30 
VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v", ".flv", ".wmv"}

cancel_flag = False
current_process = None

# ==============================
# HELPERS
# ==============================

def get_desktop():
    return Path(os.path.join(os.path.expanduser("~"), "Desktop"))

def get_output_dir():
    desktop = get_desktop()
    today_str = datetime.today().strftime("%Y-%m-%d")
    out_dir = desktop / today_str
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir

def get_duration(input_file):
    command = [
        FFPROBE_EXE,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(input_file)
    ]
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
            encoding='utf-8',
            errors='replace'
        )
        return float(result.stdout.strip())
    except Exception:
        return 0.0

def format_time(seconds):
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:02}"

def cancel_action():
    global cancel_flag, current_process
    if messagebox.askyesno("Bekor qilish", "Siqish jarayonini haqiqatan ham bekor qilmoqchimisiz?"):
        cancel_flag = True
        if current_process:
            try:
                current_process.terminate()
            except:
                pass

def update_ui(func, *args, **kwargs):
    root.after(0, lambda: func(*args, **kwargs))
    
def get_encoder_args(encoder_choice, quality):
    if "NVIDIA" in encoder_choice:
        # NVIDIA NVENC
        return ["-c:v", "hevc_nvenc", "-preset", "slow", "-rc", "vbr", "-cq", str(quality), "-b:v", "0"]
    elif "AMD" in encoder_choice:
        # AMD AMF
        return ["-c:v", "hevc_amf", "-quality", "quality", "-rc", "cqp", "-qp_i", str(quality), "-qp_p", str(quality)]
    elif "Intel" in encoder_choice:
        # Intel QSV
        return ["-c:v", "hevc_qsv", "-preset", "slow", "-global_quality", str(quality)]
    else:
        # CPU
        return ["-c:v", "libx265", "-preset", "fast", "-crf", str(quality)]

# ==============================
# COMPRESSION LOGIC
# ==============================

def process_video_file(video, out_dir, index, total_videos, encoder_choice):
    global cancel_flag, current_process
    
    output_path = out_dir / f"{video.stem}_compressed.mp4"
    counter = 1
    while output_path.exists():
        output_path = out_dir / f"{video.stem}_compressed_{counter}.mp4"
        counter += 1
        
    duration = get_duration(video)
    if duration == 0:
        duration = 1.0 # fallback

    enc_args = get_encoder_args(encoder_choice, QUALITY)

    command = [
        FFMPEG_EXE, "-y",
        "-i", str(video),
        *enc_args,
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        str(output_path)
    ]
    
    process = subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        universal_newlines=True,
        bufsize=1,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
        encoding='utf-8',
        errors='replace'
    )
    current_process = process
    
    time_pattern = re.compile(r"time=(\d+):(\d+):(\d+(?:\.\d+)?)")
    
    try:
        while True:
            if cancel_flag:
                process.terminate()
                process.wait()
                if output_path.exists():
                    try: output_path.unlink()
                    except: pass
                raise Exception("CANCELLED")

            line = process.stderr.readline()
            if not line:
                if process.poll() is not None:
                    break
                continue
                
            match = time_pattern.search(line)
            if match:
                h = int(match.group(1))
                m = int(match.group(2))
                s = float(match.group(3))
                current_time = h * 3600 + m * 60 + s
                percent = min(100, (current_time / duration) * 100)
                
                def ui_update(p=percent, ct=current_time, d=duration):
                    progress["value"] = p
                    percent_label.config(text=f"{p:.1f}%")
                    remaining = max(0, d - ct)
                    prefix = f"⏳ Siqilmoqda ({index}/{total_videos})...\n" if total_videos > 1 else "⏳ Siqilmoqda...\n"
                    status.config(text=f"{prefix}{video.name}\n{format_time(ct)} / {format_time(d)}\nQolgan: {format_time(remaining)}")
                update_ui(ui_update)
                
        return_code = process.wait()
        if return_code != 0 and not cancel_flag:
            if output_path.exists():
                try: output_path.unlink()
                except: pass
            raise Exception(f"FFmpeg xatosi: {video.name} (Tanlangan qurilma qo'llab quvvatlanmasligi mumkin)")
            
        orig_mb = video.stat().st_size / (1024 * 1024)
        comp_mb = output_path.stat().st_size / (1024 * 1024)
        return orig_mb, comp_mb, output_path
    
    except Exception as e:
        # Biron xatolik bo'lsa yoki bekor qilinsa chala qolgan faylni o'chirish
        if output_path.exists():
            try: output_path.unlink()
            except: pass
        raise e

def compress_videos_task(videos, encoder_choice):
    global cancel_flag, current_process
    cancel_flag = False
    current_process = None

    out_dir = get_output_dir()
    total_videos = len(videos)
    orig_mb_total = 0
    saved_mb_total = 0

    try:
        for i, video in enumerate(videos, 1):
            if cancel_flag:
                break
                
            update_ui(status.config, text=f"⏳ Siqilmoqda ({i}/{total_videos})...\n{video.name}")
            orig_mb, comp_mb, out_path = process_video_file(video, out_dir, i, total_videos, encoder_choice)
            orig_mb_total += orig_mb
            saved_mb_total += comp_mb
            
        if cancel_flag:
            update_ui(status.config, text="🚫 Jarayon bekor qilindi")
        else:
            update_ui(progress.config, value=100)
            update_ui(percent_label.config, text="100%")
            if orig_mb_total > 0:
                saved_percent = (1 - saved_mb_total / orig_mb_total) * 100
                update_ui(status.config, text=f"✅ Barchasi tayyor!\n{orig_mb_total:.1f} MB → {saved_mb_total:.1f} MB\nTejaldi: {saved_percent:.1f}%")
                msg = f"Barcha videolar siqildi! 🎬\n\nOriginal: {orig_mb_total:.1f} MB\nSiqilgan: {saved_mb_total:.1f} MB\nTejaldi: {saved_percent:.1f}%\n\nJoylashuv: {out_dir.name}"
                update_ui(messagebox.showinfo, "Tayyor", msg)
            else:
                update_ui(status.config, text="❌ Muammo yuz berdi")

    except Exception as e:
        if str(e) == "CANCELLED" or cancel_flag:
            update_ui(status.config, text="🚫 Jarayon bekor qilindi")
        else:
            update_ui(status.config, text="❌ Xatolik yuz berdi")
            update_ui(messagebox.showerror, "Xatolik", str(e))
    finally:
        current_process = None
        update_ui(btn_file.config, state="normal")
        update_ui(btn_folder.config, state="normal")
        update_ui(combo_encoder.config, state="readonly")
        update_ui(btn_cancel.config, state="disabled")


# ==============================
# ACTIONS
# ==============================

def start_compression(videos):
    btn_file.config(state="disabled")
    btn_folder.config(state="disabled")
    combo_encoder.config(state="disabled")
    btn_cancel.config(state="normal")
    progress["value"] = 0
    percent_label.config(text="0%")
    
    selected_encoder = combo_encoder.get()
    
    thread = threading.Thread(target=compress_videos_task, args=(videos, selected_encoder), daemon=True)
    thread.start()

def action_choose_file():
    file_path = filedialog.askopenfilename(
        title="Faylni tanlang",
        filetypes=[("Video files", "*.mp4 *.mkv *.avi *.mov *.webm *.m4v *.flv *.wmv")]
    )
    if not file_path:
        return

    path_obj = Path(file_path)
    if path_obj.suffix.lower() not in VIDEO_EXTS:
        messagebox.showwarning("Ogohlantirish", "Faqat video fayllarni tanlang!")
        return

    status.config(text=f"📄 Tanlandi: {path_obj.name}")
    start_compression([path_obj])

def action_choose_folder():
    folder_path = filedialog.askdirectory(title="Jildni tanlang")
    if not folder_path:
        return

    path_obj = Path(folder_path)
    videos = [f for f in path_obj.rglob('*') if f.is_file() and f.suffix.lower() in VIDEO_EXTS]
    
    if not videos:
        status.config(text="❌ Jildda video topilmadi")
        messagebox.showwarning("Ogohlantirish", "Tanlangan jild ichida hech qanday video fayl topilmadi.")
        return
        
    status.config(text=f"📁 Tanlandi: {path_obj.name} ({len(videos)} ta video)")
    start_compression(videos)

# ==============================
# UI
# ==============================

root = tk.Tk()
root.title("Max Video Compressor")
root.geometry("500x560")
root.resizable(False, False)
root.configure(bg="#FDFDFD")

try:
    import sys
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
        
    icon_path = os.path.join(base_path, 'compress_setting_repair_tools_zipper_icon_265700.ico')
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
except Exception:
    pass

style = ttk.Style()
style.theme_use('clam')
style.configure("TProgressbar", 
                thickness=16, 
                troughcolor='#EAEAEA', 
                background='#0078D7', 
                bordercolor='#FDFDFD', 
                lightcolor='#0078D7', 
                darkcolor='#0078D7')
style.configure("TCombobox", padding=5, font=("Segoe UI", 10))

title = tk.Label(root, text="Max Video Compressor", font=("Segoe UI", 24, "bold"), bg="#FDFDFD", fg="#202124")
title.pack(pady=(25, 5))

subtitle = tk.Label(root, text="Videolarni GPU orqali tez va maksimal siqish", font=("Segoe UI", 11), bg="#FDFDFD", fg="#5F6368")
subtitle.pack(pady=(0, 15))

# Encoder Selection
encoder_frame = tk.Frame(root, bg="#FDFDFD")
encoder_frame.pack(fill="x", padx=40, pady=(0, 15))

lbl_enc = tk.Label(encoder_frame, text="Videokarta (GPU) turini tanlang:", font=("Segoe UI", 10), bg="#FDFDFD", fg="#5F6368")
lbl_enc.pack(anchor="w", pady=(0, 5))

encoders = [
    "🟩 NVIDIA GPU (Juda tez)",
    "🟥 AMD GPU (Juda tez)",
    "🟦 Intel GPU (Juda tez)",
    "⬜ CPU Processor (Sekin)"
]
combo_encoder = ttk.Combobox(encoder_frame, values=encoders, state="readonly", font=("Segoe UI", 10))
combo_encoder.current(0) # Default to NVIDIA
combo_encoder.pack(fill="x")

progress_frame = tk.Frame(root, bg="#FDFDFD")
progress_frame.pack(fill="x", padx=40, pady=5)

percent_label = tk.Label(progress_frame, text="0%", font=("Segoe UI", 16, "bold"), bg="#FDFDFD", fg="#202124")
percent_label.pack(pady=(0, 5))

bar_container = tk.Frame(progress_frame, bg="#FDFDFD")
bar_container.pack(fill="x")

progress = ttk.Progressbar(bar_container, orient="horizontal", mode="determinate", maximum=100)
progress.pack(side="left", fill="x", expand=True)

btn_cancel = tk.Button(
    bar_container, text="❌", font=("Segoe UI", 10, "bold"), 
    bg="#D32F2F", fg="white", activebackground="#B71C1C", activeforeground="white", 
    relief="flat", bd=0, padx=10, pady=2, cursor="hand2", command=cancel_action, state="disabled"
)
btn_cancel.pack(side="right", padx=(10, 0))

status_frame = tk.Frame(root, bg="#FDFDFD", height=90)
status_frame.pack(fill="x", pady=15)
status_frame.pack_propagate(False)

status = tk.Label(status_frame, text="Boshlash uchun video yoki jild tanlang", font=("Segoe UI", 10), bg="#FDFDFD", fg="#5F6368", justify="center")
status.pack(expand=True, fill="both")

btn_frame = tk.Frame(root, bg="#FDFDFD")
btn_frame.pack(pady=10)

btn_file = tk.Button(
    btn_frame, text="🎬 Video yuklash", font=("Segoe UI", 11, "bold"), 
    bg="#0078D7", fg="white", activebackground="#005A9E", activeforeground="white", 
    relief="flat", bd=0, padx=20, pady=10, cursor="hand2", command=action_choose_file
)
btn_file.pack(side="left", padx=10)

btn_folder = tk.Button(
    btn_frame, text="📁 Jild yuklash", font=("Segoe UI", 11, "bold"), 
    bg="#3C4043", fg="white", activebackground="#202124", activeforeground="white", 
    relief="flat", bd=0, padx=20, pady=10, cursor="hand2", command=action_choose_folder
)
btn_folder.pack(side="left", padx=10)

info = tk.Label(root, text="Faqat videolar qabul qilinadi. (H.265 bilan maksimal siqish)", font=("Segoe UI", 9), bg="#FDFDFD", fg="#9AA0A6")
info.pack(side="bottom", pady=20)

root.mainloop()