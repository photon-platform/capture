import subprocess
import re

def get_source_identifier(partial_match_string):
    """
    Finds the full name or index of an input source matching a partial string
    in its Name, Description, or certain device properties.
    Prefers returning the full name if found, as it's more stable.

    Args:
        partial_match_string (str): A substring to match (case-insensitive)
                                    in the source's name or description.
                                    e.g., "Scarlett", "Focusrite", "Analog Input - Scarlett"

    Returns:
        str or None: The full name (preferred) or index of the matching source,
                     or None if not found.
    """
    try:
        result = subprocess.run(['pactl', 'list', 'sources'], capture_output=True, text=True, check=True)
        sources_output = result.stdout
        
        source_blocks = sources_output.split("Source #")
        
        for block_content in source_blocks:
            if not block_content.strip():
                continue

            current_block = "Source #" + block_content # For easier parsing of individual source details
            
            source_index_match = re.search(r"^Source #(\d+)", current_block, re.MULTILINE)
            source_name_match = re.search(r"^\s*Name: (.+)", current_block, re.MULTILINE)
            source_description_match = re.search(r"^\s*Description: (.+)", current_block, re.MULTILINE)
            properties_dev_desc_match = re.search(r"device.description = \"([^\"]+)\"", current_block)
            properties_prod_name_match = re.search(r"device.product.name = \"([^\"]+)\"", current_block)

            current_source_index = source_index_match.group(1) if source_index_match else None
            current_source_name = source_name_match.group(1).strip() if source_name_match else None
            current_source_description = source_description_match.group(1).strip() if source_description_match else None
            prop_dev_desc = properties_dev_desc_match.group(1).strip() if properties_dev_desc_match else ""
            prop_prod_name = properties_prod_name_match.group(1).strip() if properties_prod_name_match else ""
            
            identifier_to_return = None

            # Check for match in Name (often like alsa_input.usb-Focusrite_Scarlett...)
            if current_source_name and partial_match_string.lower() in current_source_name.lower():
                identifier_to_return = current_source_name

            # Check for match in Description (often more user-friendly like "Scarlett 2i2 Analog Stereo")
            elif current_source_description and partial_match_string.lower() in current_source_description.lower():
                identifier_to_return = current_source_name if current_source_name else current_source_index
            
            # Check for match in device.description property
            elif prop_dev_desc and partial_match_string.lower() in prop_dev_desc.lower():
                identifier_to_return = current_source_name if current_source_name else current_source_index

            # Check for match in device.product.name property
            elif prop_prod_name and partial_match_string.lower() in prop_prod_name.lower():
                identifier_to_return = current_source_name if current_source_name else current_source_index

            if identifier_to_return:
                # print(f"Debug: Matched Source #{current_source_index}, Name: {current_source_name}, Desc: {current_source_description}, Identifier: {identifier_to_return}")
                return identifier_to_return
                
    except FileNotFoundError:
        print("Error: pactl command not found. Is PulseAudio or pipewire-pulse installed and in your PATH?")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error executing 'pactl list sources': {e.stderr}")
        return None
    return None

def set_input_volume(source_identifier, volume_percent_str):
    """
    Sets the input volume for a given PulseAudio source.

    Args:
        source_identifier (str): The name or index of the input source.
        volume_percent_str (str): The desired volume level as a percentage string (e.g., "100%", "150%").
                                  PulseAudio uses an internal value of 65536 for 100% (0dB).
                                  Using percentages with pactl handles this conversion.
    """
    try:
        command = ['pactl', 'set-source-volume', source_identifier, volume_percent_str]
        
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Successfully set volume for source '{source_identifier}' to {volume_percent_str}.")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
            
    except FileNotFoundError:
        print("Error: pactl command not found. Is PulseAudio (or pipewire-pulse) installed and in your PATH?")
    except subprocess.CalledProcessError as e:
        print(f"Error setting volume for source '{source_identifier}':")
        print(f"Command: {' '.join(e.cmd)}")
        print(f"Return code: {e.returncode}")
        print(f"Stderr: {e.stderr.strip() if e.stderr else 'N/A'}")
        print(f"Stdout: {e.stdout.strip() if e.stdout else 'N/A'}")
        print("Please ensure the source identifier is correct and PulseAudio/PipeWire is running.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # --- Configuration ---

    # 1. Identify your Input Device Keyword:
    #    Open a terminal and run: `pactl list sources`
    #    Look for your microphone (e.g., "Scarlett 2i2 4th Gen").
    #    Note its "Name:" (e.g., alsa_input.usb-Focusrite_Scarlett_2i2_4th_Gen...)
    #    or "Description:" (e.g., Scarlett 2i2 4th Gen Analog Stereo).
    #    The text from your screenshot "Analog Input - Scarlett 2i2 4th Gen" is likely the Description.
    #    Choose a unique part of the Name or Description for TARGET_SOURCE_KEYWORD.
    #
    #    Example: Based on your screenshot, good keywords could be:
    #             "Scarlett 2i2 4th Gen" (more specific)
    #             "Scarlett 2i2" (if unique enough)
    #             "Analog Input - Scarlett"
    TARGET_SOURCE_KEYWORD = "Scarlett 2i2 4th Gen" # <--- IMPORTANT: SET THIS TO MATCH YOUR DEVICE
                                                  # This search is case-insensitive.

    # 2. Set Desired Volume:
    #    "100%" is the standard maximum volume (0dB).
    #    If you want to enable "Over-Amplification" or go beyond 100% (if your system/driver supports it),
    #    you can use values like "120%", "150%", etc.
    #    Too high a value might cause clipping or distortion, so you might need to experiment.
    DESIRED_VOLUME_PERCENT = "150%" # <--- SET YOUR DESIRED MAX VOLUME HERE (e.g., "100%", "120%", "150%")


    # --- Script Logic ---
    print(f"Attempting to find input source containing: '{TARGET_SOURCE_KEYWORD}'")
    source_identifier = get_source_identifier(TARGET_SOURCE_KEYWORD)

    if source_identifier:
        print(f"Found source identifier: '{source_identifier}'")
        print(f"Setting volume to {DESIRED_VOLUME_PERCENT} for '{source_identifier}'.")
        set_input_volume(source_identifier, DESIRED_VOLUME_PERCENT)
    else:
        print(f"\nCould not automatically find an input source matching '{TARGET_SOURCE_KEYWORD}'.")
        print("Troubleshooting steps:")
        print("1. Double-check the `TARGET_SOURCE_KEYWORD` in the script against your device's details.")
        print("2. Ensure your microphone is connected and recognized by the system.")
        print("3. Run 'pactl list sources' in your terminal to see all available sources and their exact names/descriptions.")
        print("   You might need a more specific or different keyword.")
        print("\nAs a fallback, you can try setting the volume for the default input source,")
        print("although specifying your Scarlett device is more reliable:")
        # print("\nAttempting to set volume for @DEFAULT_SOURCE@ as a fallback...")
        # set_input_volume("@DEFAULT_SOURCE@", DESIRED_VOLUME_PERCENT)
