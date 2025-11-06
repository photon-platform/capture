import gi
import subprocess
from pathlib import Path
import time
import re

gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib

Gst.init(None)

DEFAULT_MIC = "alsa_input.usb-BLUE_MICROPHONE_Blue_Snowball_201305-00.analog-stereo"
DEFAULT_MIC = "alsa_output.usb-Focusrite_Scarlett_2i2_4th_Gen_S2NYNAU3C96D20-00.analog-surround-40"
DEFAULT_SYSTEM_AUDIO = "alsa_output.pci-0000_0a_00.6.analog-stereo.monitor"


def display_elapsed_time(start_time, stop_event):
    while not stop_event.is_set():
        elapsed_time = time.time() - start_time
        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        print(f"\rElapsed Time: {elapsed_str}", end="")
        time.sleep(1)
    print()


def slugify(value):
    """
    Converts to lowercase, removes non-word characters (alphanumerics and underscores)
    and converts spaces to hyphens. Also strips leading and trailing whitespace.
    """
    value = str(value)
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    value = re.sub(r'[-\s]+', '-', value)
    return value


#  pulsesrc device=alsa_input.usb-Focusrite_Scarlett_2i2_4th_Gen_S2NYNAU3C96D20-00.analog-surround-40 ! audioconvert ! audioresample ! wavenc ! filesink location=output.wav
def configure_mic_pipeline(output_file: Path, device=DEFAULT_MIC):
    pipeline_cmd = (
        f"pulsesrc device={device} ! "
        f"volume volume=1.5 ! "
        f"audioconvert ! opusenc ! oggmux ! "
        f"filesink location={str(output_file)}"
    )
    return Gst.parse_launch(pipeline_cmd)

def configure_screen_pipeline(output_file: Path):
    pipeline_cmd = (
        f"ximagesrc use-damage=0 startx=0 starty=768 endx=1919 endy=1847 ! "
        f"videoconvert ! vp8enc cpu-used=4 target-bitrate=2000000 ! matroskamux ! "
        f"filesink location={str(output_file)}"
    )
    return Gst.parse_launch(pipeline_cmd)

def configure_system_audio_pipeline(output_file: Path, device=DEFAULT_SYSTEM_AUDIO):
    pipeline_cmd = (
        f"pulsesrc device={device} ! "
        f"volume volume=0.7 ! "
        f"audioconvert ! opusenc ! oggmux ! "
        f"filesink location={str(output_file)}"
    )
    return Gst.parse_launch(pipeline_cmd)

def configure_system_screen_audio_pipeline(output_file: Path, audio_device=DEFAULT_SYSTEM_AUDIO):
    pipeline_cmd = (
        f"ximagesrc use-damage=0 startx=0 starty=768 endx=1919 endy=1847 ! "
        f"videoconvert ! vp8enc cpu-used=4 target-bitrate=2000000 ! queue ! mux. "
        f"pulsesrc device={audio_device} ! audioconvert ! opusenc ! queue ! mux. "
        f"matroskamux name=mux ! filesink location={str(output_file)}"
    )
    return Gst.parse_launch(pipeline_cmd)

def clean_mic_audio(input_audio: Path) -> Path:
    #  output_audio = input_audio.with_suffix("_clean.ogg")
    output_audio = input_audio.with_name(input_audio.stem + "_clean" + input_audio.suffix)

    command = [
        'ffmpeg', '-y', '-i', str(input_audio),
        '-af', 'afftdn=nr=40:nt=w,equalizer=f=300:width=100:gain=3:f=5000:width=200:gain=3,acompressor=threshold=-21dB:ratio=9:attack=200:release=1000',
        str(output_audio)
    ]
    subprocess.run(command)
    return output_audio

def combine_video_system_audio(video_file: Path, audio_file: Path, output_file: Path):
    command = [
        "ffmpeg",
        "-i",
        str(video_file),
        "-i",
        str(audio_file),
        "-c:v",
        "libx264",
        "-crf",
        "23",
        "-preset",
        "veryfast",
        "-c:a",
        "copy",
        "-shortest",
        str(output_file),
    ]
    subprocess.run(command)
    return output_file

def invert_video_colors(input_file: Path) -> Path:
    #  output_file = input_file.with_suffix("_inv.mkv")
    output_file = input_file.with_name(input_file.stem + "_inv" + input_file.suffix)
    command = [
        'ffmpeg',
        '-i', str(input_file),
        '-vf', 'negate',
        str(output_file)
    ]
    subprocess.run(command)
    return output_file

def combine_all(folder_name: Path, screen_system_file: Path, mic_file: Path) -> Path:
    output_file = folder_name / "all.mp4"
    command = [
        'ffmpeg',
        "-i",
        str(screen_system_file),
        "-i",
        str(mic_file),
        "-filter_complex",
        "[0:a][1:a]amix=inputs=2:duration=shortest,volume=2.0[a]",
        "-map",
        "0:v",
        '-map', '0:v',                  # Map video from first input
        '-map', '[a]',                  # Map mixed audio
        '-c:v', 'copy',                 # Copy the video stream as is
        '-c:a', 'aac',                  # Re-encode audio to AAC
        '-b:a', '128k',                 # Bitrate for the audio
        str(output_file)                # Output file
    ]
    subprocess.run(command)
    return output_file

def generate_waveform(input_audio: Path, color="Blue") -> Path:
    #  output = input_audio.with_suffix("_waves.mp4")
    output = input_audio.with_name(input_audio.stem + "_waves.mp4")  # Updated line

    subprocess.run([
        'ffmpeg', '-y', '-i', str(input_audio),
        '-filter_complex', f'showwaves=s=200x400:mode=cline:colors={color},crop=200:200',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        str(output)
    ])
    return output

def combine_screen_waves_2(output_file: Path, screen_file: Path, mic_waves: Path, system_waves: Path) -> Path:
    margin = 30
    wave_size = 100

    # Use Path(__file__).parent to locate circle_mask.png relative to this script
    circle_mask_path = Path(__file__).parent / "circle_mask.png" # Ensure this path is correct

    # Calculate new height for the screen video
    output_resolution = (1920, 1080)
    new_height = output_resolution[1] - 3 * margin - wave_size
    # Calculate new width while maintaining the aspect ratio
    aspect_ratio = 16 / 9
    new_width = int(new_height * aspect_ratio)

    # NOTE: the system and mic waves have been switched so the filter names are opposite
    subprocess.run([
        'ffmpeg', '-y',
        '-i', str(screen_file),
        '-i', str(system_waves),
        '-i', str(mic_waves),
        '-i', str(circle_mask_path),
        '-filter_complex',
        f'[1:v]scale={wave_size}x{wave_size},format=yuva420p[mic_waves];' + 
        f'[2:v]scale={wave_size}x{wave_size},format=yuva420p[sys_waves];' + 
        '[mic_waves][3:v]alphamerge[mic_masked];' + 
        '[sys_waves][3:v]alphamerge[sys_masked];' + 
        f'[0:v]scale={new_width}x{new_height}[scaled_screen];' + 
        f'color=c=black:s={output_resolution[0]}x{output_resolution[1]}[bg];' + 
        f'[bg][scaled_screen]overlay=(W-w)/2:{margin}[screen_on_bg];' + 
        f'[screen_on_bg][mic_masked]overlay=shortest=1:x={margin}:y=main_h-overlay_h-{margin}[with_mic];' + 
        f'[with_mic][sys_masked]overlay=shortest=1:x=W-w-{margin}:y=main_h-overlay_h-{margin},format=yuv420p[v];' + 
        '[0:a]volume=2.0[a]',
        '-map', '[v]', '-map', '[a]',
        '-c:v', 'libx264', '-c:a', 'aac', '-b:a', '128k',
        str(output_file)
    ])
    return output_file

def combine_screen_waves(output_file: Path, screen_file: Path, mic_waves: Path, system_waves: Path) -> Path:
    margin = 30
    wave_size = 100
    #  output_file = folder_name / "all_waves.mp4"

    # Use Path(__file__).parent to locate circle_mask.png relative to this script
    circle_mask_path = Path(__file__).parent / "circle_mask.png" # Ensure this path is correct


    # Calculate new height for the screen video
    output_resolution = (1920, 1080)
    new_height = output_resolution[1] - 3 * margin - wave_size
    # Calculate new width while maintaining the aspect ratio
    aspect_ratio = 16 / 9
    new_width = int(new_height * aspect_ratio)

    # NOTE: the system and mic waves have been switched so the filter names are opposite
    subprocess.run([
        'ffmpeg', '-y',
        '-i', str(screen_file),
        '-i', str(system_waves),
        '-i', str(mic_waves),
        '-i', str(circle_mask_path),
        '-filter_complex',
        f'[1:v]scale={wave_size}x{wave_size},format=yuva420p[mic_waves];' + 
        f'[2:v]scale={wave_size}x{wave_size},format=yuva420p[sys_waves];' + 
        '[mic_waves][3:v]alphamerge[mic_masked];' + 
        '[sys_waves][3:v]alphamerge[sys_masked];' + 
        f'[0:v]scale={new_width}x{new_height}[scaled_screen];' + 
        f'color=c=black:s={output_resolution[0]}x{output_resolution[1]}[bg];' + 
        f'[bg][scaled_screen]overlay=(W-w)/2:{margin}[screen_on_bg];' + 
        f'[screen_on_bg][mic_masked]overlay=shortest=1:x={margin}:y=main_h-overlay_h-{margin}[with_mic];' + 
        f'[with_mic][sys_masked]overlay=shortest=1:x=W-w-{margin}:y=main_h-overlay_h-{margin},format=yuv420p[v];' + 
        '[1:a][2:a]amix=inputs=2:duration=shortest:normalize=0,volume=2.0[a]',
        '-map', '[v]', '-map', '[a]',
        '-c:v', 'libx264', '-c:a', 'aac', '-b:a', '128k',
        str(output_file)
    ])
    return output_file
