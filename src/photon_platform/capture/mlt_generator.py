from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
import datetime
import hashlib
import subprocess
import os


def launch_shotcut(mlt_file_path):
    """
    Launch Shotcut with the specified MLT file.
    """
    shotcut = "/home/phi/AppImages/shotcut-linux-x86_64-250329.AppImage"
    try:
        subprocess.Popen([shotcut, str(mlt_file_path)])
        print(f"Launching Shotcut with MLT file: {mlt_file_path}")
    except FileNotFoundError:
        print("Shotcut not found. Please make sure it's installed and in your PATH.")
    except Exception as e:
        print(f"An error occurred while trying to launch Shotcut: {e}")


def get_audio_duration(file_path):
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(file_path),
        ],
        capture_output=True,
        text=True,
    )
    duration = float(result.stdout)
    return duration


def get_template_path():
    return os.path.join(os.path.dirname(__file__), "templates", "mlt_template.xml")


def generate_mlt_file(mic_clean_file: Path, output_file: Path):
    template_path = get_template_path()
    template_dir = os.path.dirname(template_path)

    env = Environment(
        loader=FileSystemLoader(template_dir), autoescape=select_autoescape(["xml"])
    )
    template = env.get_template(os.path.basename(template_path))

    duration_seconds = get_audio_duration(mic_clean_file)
    duration = f"{int(duration_seconds // 3600):02d}:{int((duration_seconds % 3600) // 60):02d}:{duration_seconds % 60:06.3f}"
    length = f"{duration}.{int((duration_seconds % 1) * 1000):03d}"

    with open(mic_clean_file, "rb") as f:
        file_hash = hashlib.md5(f.read()).hexdigest()

    # Use relative path for mic_clean_file
    relative_mic_clean_file = os.path.relpath(mic_clean_file, start=output_file.parent)

    context = {
        "mic_clean_file": relative_mic_clean_file,
        "mic_clean_filename": mic_clean_file.name,
        "duration": duration,
        "length": length,
        "creation_time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "hash": file_hash,
    }

    output = template.render(context)

    with open(output_file, "w") as f:
        f.write(output)

    print(f"MLT file generated: {output_file}")

    return output_file
