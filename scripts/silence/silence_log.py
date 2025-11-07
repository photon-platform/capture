# Re-importing necessary library and redefining the functions as the code execution state was reset
import re
from rich import print

import subprocess

def detect_silence_ffmpeg(input_file, threshold=2.0, silence_log='silence.log'):
    try:
        cmd = [
            'ffmpeg',
            '-hide_banner',
            '-i', input_file,
            '-af', f'silencedetect=noise=-30dB:d={threshold}',
            '-f', 'null',
            '-'
        ]

        silence_log = input_file + ".silence.log"
        with open(silence_log, 'w') as log_file:
            subprocess.run(cmd, stderr=log_file)

        return silence_log
    except Exception as e:
        return f"Error running FFmpeg: {e}"

# Function to parse silence log and retrieve each pair of silence_start and silence_end values
def parse_silence_log_pairs(log_content):
    """
    Parse the silence log to extract pairs of silence_start and silence_end times.
    """
    pattern = r'silence_(start|end): ([0-9.]+)'
    matches = re.findall(pattern, log_content)

    silence_pairs = []
    for i in range(0, len(matches), 2):
        start = float(matches[i][1])
        end = float(matches[i + 1][1]) if i + 1 < len(matches) else None
        silence_pairs.append((start, end))

    return silence_pairs

# Function to read the silence.log file and parse it
def parse_silence_log_file(file_path):
    """
    Read a silence log file and parse it to extract pairs of silence_start and silence_end times.
    """
    try:
        with open(file_path, 'r') as file:
            log_content = file.read()
        return parse_silence_log_pairs(log_content)
    except Exception as e:
        return f"Error reading file: {e}"

def get_non_silent_segments(silence_pairs, total_duration=None):
    non_silent_segments = []
    last_silence_end = 0.0

    for start, end in silence_pairs:
        if start > last_silence_end:
            non_silent_segments.append((last_silence_end, start))
        last_silence_end = end

    if total_duration is None or last_silence_end < total_duration:
        non_silent_segments.append((last_silence_end, total_duration))

    return non_silent_segments


# Path to the silence log file
media_file = './23.354.042722.check.mp4'

# Parsing the silence log file
silence_log = detect_silence_ffmpeg(media_file)
silence_pairs = parse_silence_log_file(silence_log)
clips = get_non_silent_segments(silence_pairs)
print(clips)


