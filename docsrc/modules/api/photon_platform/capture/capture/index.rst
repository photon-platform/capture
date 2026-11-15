photon_platform.capture.capture
===============================

.. py:module:: photon_platform.capture.capture


Attributes
----------

.. autoapisummary::

   photon_platform.capture.capture.DEFAULT_MIC
   photon_platform.capture.capture.DEFAULT_MIC
   photon_platform.capture.capture.DEFAULT_SYSTEM_AUDIO


Functions
---------

.. autoapisummary::

   photon_platform.capture.capture.display_elapsed_time
   photon_platform.capture.capture.slugify
   photon_platform.capture.capture.configure_mic_pipeline
   photon_platform.capture.capture.configure_screen_pipeline
   photon_platform.capture.capture.configure_system_audio_pipeline
   photon_platform.capture.capture.configure_system_screen_audio_pipeline
   photon_platform.capture.capture.clean_mic_audio
   photon_platform.capture.capture.combine_video_system_audio
   photon_platform.capture.capture.invert_video_colors
   photon_platform.capture.capture.combine_all
   photon_platform.capture.capture.generate_waveform
   photon_platform.capture.capture.combine_screen_waves_2
   photon_platform.capture.capture.combine_screen_waves


Module Contents
---------------

.. py:data:: DEFAULT_MIC
   :value: 'alsa_input.usb-BLUE_MICROPHONE_Blue_Snowball_201305-00.analog-stereo'


.. py:data:: DEFAULT_MIC
   :value: 'alsa_output.usb-Focusrite_Scarlett_2i2_4th_Gen_S2NYNAU3C96D20-00.analog-surround-40'


.. py:data:: DEFAULT_SYSTEM_AUDIO
   :value: 'alsa_output.pci-0000_0a_00.6.analog-stereo.monitor'


.. py:function:: display_elapsed_time(start_time, stop_event)

.. py:function:: slugify(value)

   Converts to lowercase, removes non-word characters (alphanumerics and underscores)
   and converts spaces to hyphens. Also strips leading and trailing whitespace.


.. py:function:: configure_mic_pipeline(output_file: pathlib.Path, device=DEFAULT_MIC)

.. py:function:: configure_screen_pipeline(output_file: pathlib.Path)

.. py:function:: configure_system_audio_pipeline(output_file: pathlib.Path, device=DEFAULT_SYSTEM_AUDIO)

.. py:function:: configure_system_screen_audio_pipeline(output_file: pathlib.Path, audio_device=DEFAULT_SYSTEM_AUDIO)

.. py:function:: clean_mic_audio(input_audio: pathlib.Path) -> pathlib.Path

.. py:function:: combine_video_system_audio(video_file: pathlib.Path, audio_file: pathlib.Path, output_file: pathlib.Path)

.. py:function:: invert_video_colors(input_file: pathlib.Path) -> pathlib.Path

.. py:function:: combine_all(folder_name: pathlib.Path, screen_system_file: pathlib.Path, mic_file: pathlib.Path) -> pathlib.Path

.. py:function:: generate_waveform(input_audio: pathlib.Path, color='Blue') -> pathlib.Path

.. py:function:: combine_screen_waves_2(output_file: pathlib.Path, screen_file: pathlib.Path, mic_waves: pathlib.Path, system_waves: pathlib.Path) -> pathlib.Path

.. py:function:: combine_screen_waves(output_file: pathlib.Path, screen_file: pathlib.Path, mic_waves: pathlib.Path, system_waves: pathlib.Path) -> pathlib.Path

