import argparse
import datetime
from pathlib import Path
import threading
import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib
import time

# Use relative imports within the package
from .capture import (
    configure_mic_pipeline,
    configure_screen_pipeline,
    configure_system_audio_pipeline,
    display_elapsed_time,
    clean_mic_audio,
    combine_video_system_audio,
    slugify,
)
from .mlt_generator import generate_mlt_file, launch_shotcut

#  DEFAULT_SESSIONS_DIR = Path.home() / 'Sessions'
DEFAULT_SESSIONS_DIR = Path('.')

def run(output_dir: Path, title: str):
    """
    Main function to run the recording process.
    """
    slug = slugify(title)
    ts = datetime.datetime.now().strftime("%y.%j.%H%M%S")

    folder_path = output_dir / f"{ts}_{slug}"
    folder_path.mkdir(parents=True, exist_ok=True) # Ensure parent dirs exist

    mic_file = folder_path / "mic.ogg"
    screen_file = folder_path / "screen.mkv"
    system_file = folder_path / "system.ogg"

    Gst.init(None) # Initialize GStreamer
    mic_pipeline = configure_mic_pipeline(mic_file)
    screen_pipeline = configure_screen_pipeline(screen_file)
    system_audio_pipeline = configure_system_audio_pipeline(system_file)

    loop = GLib.MainLoop()
    stop_event = threading.Event()

    start_time = time.time()
    elapsed_thread = threading.Thread(
        target=display_elapsed_time, args=(start_time, stop_event)
    )
    elapsed_thread.start()

    print(f"Starting recording for '{title}'...")
    print(f"Output folder: {folder_path}")
    print("Press Ctrl+C to stop recording.")

    try:
        # Start the pipelines
        mic_pipeline.set_state(Gst.State.PLAYING)
        screen_pipeline.set_state(Gst.State.PLAYING)
        system_audio_pipeline.set_state(Gst.State.PLAYING)
        loop.run()
    except KeyboardInterrupt:
        print("\nStopping recording...")
        # Send EOS to each pipeline
        mic_pipeline.send_event(Gst.Event.new_eos())
        screen_pipeline.send_event(Gst.Event.new_eos())
        system_audio_pipeline.send_event(Gst.Event.new_eos())

        # Allow some time for EOS to propagate and files to finalize
        time.sleep(1) # Adjust sleep time if needed

        # Stop the pipelines
        mic_pipeline.set_state(Gst.State.NULL)
        screen_pipeline.set_state(Gst.State.NULL)
        system_audio_pipeline.set_state(Gst.State.NULL)
        loop.quit()

        stop_event.set()
        elapsed_thread.join()
        print("Recording stopped.")

    print("Processing audio...")
    mic_clean_file = clean_mic_audio(mic_file)
    print(f"Cleaned mic audio saved as: {mic_clean_file}")

    print("Combining screen video and system audio...")
    system_video_audio_file = folder_path / "system_video_audio.mkv"
    combine_video_system_audio(screen_file, system_file, system_video_audio_file)
    print(f"Combined video/system audio saved as: {system_video_audio_file}")

    print("Generating MLT file...")
    mlt_file = generate_mlt_file(mic_clean_file, folder_path / f"{slug}.mlt")
    print(f"MLT file generated: {mlt_file}")

    # Launch Shotcut with the generated MLT file
    print("Launching Shotcut...")
    launch_shotcut(mlt_file.resolve())
    print("Process complete.")


def main():
    """
    Entry point function with argument parsing for the 'capture' script.
    """
    parser = argparse.ArgumentParser(description="Record screen, microphone, and system audio.")
    parser.add_argument("title", help="Title for the recording session.")
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=DEFAULT_SESSIONS_DIR,
        help=f"Directory to save the session folder (default: {DEFAULT_SESSIONS_DIR})"
    )
    args = parser.parse_args()

    run(args.output_dir, args.title)

if __name__ == "__main__":
    # Allows running this module directly, e.g., python -m photon_platform.capture.main "My Test Recording"
    main()
