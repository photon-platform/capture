#!/usr/bin/env bash

file="./23.354.044952.start.mp4"
threshold="2.0"  # threshold duration for silence in seconds

# Step 1: Detect silence
ffmpeg -i "$file" -af silencedetect=noise=-30dB:d=$threshold -f null - 2> silence.log

# Step 2: Parse the silence durations and trim the audio
# This part would involve more complex scripting to parse and act on the log file.

