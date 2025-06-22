import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import simpleaudio as sa
import numpy as np

# --- Configuration ---
# Set the directory you want to monitor.
# IMPORTANT: Replace "YOUR_DIRECTORY_TO_MONITOR" with the actual path.
# For example: r"C:\Users\YourUser\Documents" on Windows
# or "/home/youruser/Documents" on Linux/macOS
DIRECTORY_TO_MONITOR = "YOUR_DIRECTORY_TO_MONITOR"

SOUND_DURATION = 0.2  # Duration of the sound in seconds
SAMPLE_RATE = 44100   # Samples per second for audio
ALERT_FREQUENCY = 660 # Frequency for the alert sound (e.g., a high-pitched beep)
VOLUME = 0.8          # Volume of the alert sound (0.0 to 1.0)

# --- Audio Functions (reused from previous example, slightly modified) ---
def generate_sine_wave(frequency, duration, sample_rate, amplitude=0.5):
    """
    Generates a sine wave audio array.

    Args:
        frequency (float): The frequency of the sine wave in Hz.
        duration (float): The duration of the sine wave in seconds.
        sample_rate (int): The number of samples per second.
        amplitude (float): The peak amplitude of the wave (0.0 to 1.0).

    Returns:
        numpy.ndarray: A 16-bit PCM mono audio array.
    """
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    amplitude_scaled = amplitude * 32767  # Max value for 16-bit signed integer
    audio = amplitude_scaled * np.sin(frequency * t * 2 * np.pi)
    return audio.astype(np.int16)

def play_alert_sound():
    """
    Plays a short alert sound.
    """
    print(f"Playing alert sound: Frequency={ALERT_FREQUENCY}Hz, Volume={VOLUME}")
    wave = generate_sine_wave(ALERT_FREQUENCY, SOUND_DURATION, SAMPLE_RATE, amplitude=VOLUME)
    play_obj = sa.play_buffer(wave, 1, 2, SAMPLE_RATE)
    # If you want the script to wait for the sound to finish before continuing, uncomment:
    # play_obj.wait_done()

# --- Watchdog Event Handler ---
class MyEventHandler(FileSystemEventHandler):
    """
    Custom event handler for Watchdog to react to file system events.
    """
    def on_created(self, event):
        """
        Called when a file or directory is created.
        """
        if not event.is_directory:
            print(f"File created: {event.src_path}")
            play_alert_sound()
        else:
            print(f"Directory created: {event.src_path}")

    def on_deleted(self, event):
        """
        Called when a file or directory is deleted.
        """
        if not event.is_directory:
            print(f"File deleted: {event.src_path}")
        else:
            print(f"Directory deleted: {event.src_path}")

    def on_modified(self, event):
        """
        Called when a file or directory is modified.
        """
        if not event.is_directory:
            # You can uncomment this if you want alerts for modifications too
            # print(f"File modified: {event.src_path}")
            # play_alert_sound()
            pass
        else:
            # print(f"Directory modified: {event.src_path}")
            pass

    def on_moved(self, event):
        """
        Called when a file or directory is moved/renamed.
        """
        if not event.is_directory:
            print(f"File moved/renamed: From {event.src_path} to {event.dest_path}")
            play_alert_sound()
        else:
            print(f"Directory moved/renamed: From {event.src_path} to {event.dest_path}")


# --- Main Program ---
def run_vigilant_machine():
    """
    Starts the file system monitoring and alert system.
    """
    if DIRECTORY_TO_MONITOR == "YOUR_DIRECTORY_TO_MONITOR":
        print("ERROR: Please update 'DIRECTORY_TO_MONITOR' in the script with the actual path you want to monitor.")
        return

    if not os.path.isdir(DIRECTORY_TO_MONITOR):
        print(f"ERROR: The specified directory '{DIRECTORY_TO_MONITOR}' does not exist or is not a directory.")
        return

    event_handler = MyEventHandler()
    observer = Observer()
    observer.schedule(event_handler, DIRECTORY_TO_MONITOR, recursive=True) # Monitor subdirectories too

    print(f"Vigilant Machine started! Monitoring directory: {DIRECTORY_TO_MONITOR}")
    print("Press Ctrl+C to stop monitoring.")

    try:
        observer.start()
        while True:
            time.sleep(1) # Keep the main thread alive
    except KeyboardInterrupt:
        observer.stop()
        print("\nVigilant Machine stopped.")
    observer.join()

if __name__ == "__main__":
    # Instructions for installing libraries:
    print("Please ensure you have the following Python libraries installed:")
    print("pip install watchdog numpy simpleaudio")
    print("\nStarting the Vigilant Computing Machine...")
    run_vigilant_machine()
