# CAPTURE Project: Strategy and Vision

## 1. Introduction

This document outlines the strategic vision for the `CAPTURE` project, a unified and enhanced media production workflow for the PHOTON platform. The project's goal is to consolidate the strengths of existing tools (`voce`, `.photon/tools`, `melt`), integrate modern capabilities, and create a flexible, powerful, and efficient system for capturing, processing, and producing high-quality audio and video content.

## 2. Analysis of Existing Assets

Our current ecosystem consists of several key components, each with its own strengths and weaknesses:

-   **`.photon/tools` (legacy scripts):**
    -   **Strengths:** Powerful, battle-tested `melt`-based workflow (`video_melt.sh`) for automated editing from LosslessCut EDL files. Sophisticated overlay and text-to-speech generation.
    -   **Weaknesses:** Brittle, shell-based implementation. Tightly coupled with a now-outdated `melt` installation.

-   **`voce` project:**
    -   **Strengths:** Modern Python-based implementation. Robust GStreamer-based capture for screen, microphone, and system audio. Good foundation for modular design.
    -   **Weaknesses:** Created as a workaround for the broken `melt` dependency, so it lacks the powerful post-production automation of the original scripts.

-   **`melt` framework:**
    -   **Strengths:** A powerful and scriptable multimedia framework, ideal for automated, non-linear editing. The cornerstone of our original, efficient workflow.
    -   **Weaknesses:** Historically, it has been difficult to install and maintain, leading to the creation of `voce`.

## 3. The Vision for `CAPTURE`

The `CAPTURE` project will be a modular, Python-based toolkit that provides a complete, end-to-end solution for media production. It will be designed as a library of workflows, allowing for flexible and extensible production pipelines.

The core principles of the `CAPTURE` project are:

-   **Integration:** Seamlessly combine the best features of `voce` (GStreamer capture), the legacy scripts (`melt` automation), and new tools (Glaxnimate, Frei0r).
-   **Modularity:** Structure the project as a collection of independent but interoperable modules (e.g., capture, audio, editing, effects).
-   **Flexibility:** Use a configuration-driven approach (e.g., YAML files) to define and manage different production workflows.
-   **Efficiency:** Automate as much of the production process as possible, from capture to final render.

## 4. Core Capabilities

The `CAPTURE` project will be organized around the following core capabilities:

### 4.1. Capture

-   **Multi-source Recording:** Leverage GStreamer for simultaneous capture of:
    -   Screen (full screen, specific window, or region).
    -   Microphone audio.
    -   System audio.
    -   Browser-based sources (e.g., using WebRTC or other browser automation tools).
-   **Device Management:** A robust system for detecting and selecting audio and video devices.
-   **Real-time Monitoring:** Provide real-time feedback on audio levels and capture status.

### 4.2. Pre-production & Editing

-   **Automated Rough Cuts:**
    -   **Silence Detection:** Integrate the silence detection scripts from `voce/silence` to automatically remove dead air.
    -   **EDL-based Assembly:** Fully reintegrate and enhance the `video_melt.sh` workflow, using EDLs from LosslessCut to drive `melt` for automated assembly.
-   **Transcription:** Integrate speech-to-text capabilities to generate transcripts and subtitles.
-   **Asset Management:** A system for organizing and managing captured media, generated assets, and project files.

### 4.3. Post-production & Effects

-   **`melt` Integration:** Re-establish `melt` as the core engine for automated editing, transitions, and effects.
-   **Glaxnimate & Frei0r:**
    -   **Glaxnimate:** Integrate Shotcut's new Glaxnimate support for programmatic creation of complex 2D animations and overlays.
    -   **Frei0r:** Leverage the Frei0r effects library for a wide range of filters and transitions that can be scripted with `melt`.
-   **Text-to-Speech & Audio Processing:** Enhance the existing `speak_wav` functionality and provide a library of audio processing workflows (e.g., noise reduction, equalization, compression).
-   **Overlay Engine:** Rebuild the PHP-based overlay system in Python, providing a more robust and flexible solution for generating titles, captions, and other graphics.

### 4.4. Workflow Management

-   **Workflow Library:** Create a library of pre-defined production workflows (e.g., "screencast," "presentation," "interview").
-   **YAML Configuration:** Allow users to define and customize workflows using simple YAML files.
-   **CLI Interface:** A powerful and intuitive command-line interface for executing workflows and managing the production pipeline.

## 5. Technical Strategy & Architecture

-   **Language:** Python will be the primary language for the project, providing a robust and flexible foundation.
-   **Core Libraries:**
    -   **GStreamer:** For all capture-related tasks.
    -   **`melt`:** As a subprocess for all automated editing and rendering.
    -   **FFmpeg:** For transcoding, audio processing, and other media manipulation tasks.
-   **Project Structure:**
    -   `src/capture/`: The main Python source code.
        -   `capture/`: GStreamer-based capture modules.
        -   `audio/`: Audio processing and TTS modules.
        -   `editing/`: `melt` and EDL processing modules.
        -   `effects/`: Glaxnimate, Frei0r, and overlay modules.
        -   `workflows/`: The workflow management system.
    -   `workflows/`: A directory of YAML files defining different production workflows.
    -   `templates/`: Templates for MLT XML, subtitles, and other generated files.

## 6. Migration & Integration Plan

1.  **Establish the Foundation:** Create the new `capture` project with the proposed modular structure.
2.  **Migrate `voce`:** Port the GStreamer capture and audio processing capabilities from `voce` into the new `capture` project.
3.  **Reintegrate `melt`:** Re-implement the `video_melt.sh` logic in Python, creating a robust and flexible EDL-driven editing engine.
4.  **Integrate New Capabilities:** Begin integrating Glaxnimate, Frei0r, and other new tools into the workflow.
5.  **Deprecate Old Tools:** Once the `capture` project is feature-complete, `voce` and the legacy `.photon/tools` scripts can be archived.

## 7. Future Enhancements

-   **Web UI:** A web-based interface for managing workflows and monitoring the production process.
-   **AI Integration:** Explore AI-powered tools for automated video editing, content analysis, and other advanced capabilities.
-   **Cloud Integration:** Support for cloud-based storage and rendering.
