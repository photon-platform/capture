# Re-importing necessary library and redefining the functions as the code execution state was reset
import re
from rich import print

import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET


def read_videoframerate(video_path) -> float:
    """TODO: Docstring for read_videoframerate.
    :video_path: str or Path
    :returns: TODO

    """
    video_path = Path(video_path)
    if video_path.is_file():
        try:
            cmd = ["exiftool", "-VideoFrameRate", str(video_path)]
            response = subprocess.check_output(cmd)
        except:
            print("ERROR: exiftool ")
            print(response)
            return 0

        response = response.decode("utf-8")
        vfr = str(response).split(": ")[1]
        vfr = float(vfr)
        return vfr
    else:
        print(video_path, "is not a file.")
        return 0


def combine_to_xml(clips, source_video, output_mlt=None):
    video_path = Path(source_video)
    root = ET.Element("mlt")

    vfr = read_videoframerate(source_video)  # Reading the video frame rate

    if not output_mlt:
        output_mlt = video_path.with_suffix(".mlt")

    producer = ET.SubElement(root, "producer", id="main")
    ET.SubElement(producer, "property", name="resource").text = str(video_path)

    playlist = ET.SubElement(root, "playlist", id=f"playlist0")

    for i, (start, end) in enumerate(clips):
        start_frame = int(start * vfr)  
        end_frame = (
            int(end * vfr) if end is not None else None
        ) 
        entry = ET.SubElement(playlist, "entry", producer=f"main")
        entry.attrib["in"] = str(start_frame)
        if end_frame is not None:
            entry.attrib["out"] = str(end_frame)

    # Create a tractor to combine the playlists
    tractor = ET.SubElement(root, "tractor", id="tractor0")
    multitrack = ET.SubElement(tractor, "multitrack")

    ET.SubElement(multitrack, "track", producer=f"playlist0")

    # Write to XML file
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write(output_mlt)

    return f"MLT XML created and saved to {output_mlt}"



#  def detect_silence_ffmpeg(input_file, threshold=2.0, silence_log="silence.log"):
    #  try:
        #  cmd = [
            #  "ffmpeg",
            #  "-hide_banner",
            #  "-i",
            #  input_file,
            #  "-af",
            #  f"silencedetect=noise=-30dB:d={threshold}",
            #  "-f",
            #  "null",
            #  "-",
        #  ]

        #  silence_log = input_file + ".silence.log"
        #  with open(silence_log, "w") as log_file:
            #  subprocess.run(cmd, stderr=log_file)

        #  return silence_log
    #  except Exception as e:
        #  return f"Error running FFmpeg: {e}"

def detect_silence_ffmpeg(input_file, threshold=2.0):
    try:
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-i",
            input_file,
            "-af",
            f"silencedetect=noise=-30dB:d={threshold}",
            "-f",
            "null",
            "-"
        ]

        # Run FFmpeg and capture the stderr
        result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)

        # Parse the stderr output to get silence periods
        silence_pairs = parse_silence_log_pairs(result.stderr)
        return silence_pairs
    except Exception as e:
        return f"Error running FFmpeg: {e}"


def parse_silence_log_pairs(log_content):
    """
    Parse the silence log to extract pairs of silence_start and silence_end times.
    """
    pattern = r"silence_(start|end): ([0-9.]+)"
    matches = re.findall(pattern, log_content)

    silence_pairs = []
    for i in range(0, len(matches), 2):
        start = float(matches[i][1])
        end = float(matches[i + 1][1]) if i + 1 < len(matches) else None
        silence_pairs.append((start, end))

    return silence_pairs


def parse_silence_log_file(file_path):
    """
    Read a silence log file and parse it to extract pairs of silence_start and
    silence_end times.
    """
    try:
        with open(file_path, "r") as file:
            log_content = file.read()
        return parse_silence_log_pairs(log_content)
    except Exception as e:
        return f"Error reading file: {e}"


def get_clips(silence_pairs, total_duration=None):
    clips = []
    last_silence_end = 0.0

    for start, end in silence_pairs:
        if start > last_silence_end:
            clips.append((last_silence_end, start))
        last_silence_end = end

    if total_duration is None or last_silence_end < total_duration:
        clips.append((last_silence_end, total_duration))

    return clips

if __name__ == "__main__":

    # Path to the silence log file
    media_file = "./23.358.111536.test2.mp4"

    # Ensure the media file is a valid file
    if not Path(media_file).exists():
        print(f"File not found: {media_file}")
    else:
        # Parsing the silence log file
        silence_pairs = detect_silence_ffmpeg(media_file)
        clips = get_clips(silence_pairs)
        print(clips)
        combine_to_xml(clips, media_file)

