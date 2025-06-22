import cv2
import numpy as np
import simpleaudio as sa
import time

# --- Configuration ---
CAMERA_INDEX = 0  # Typically 0 for the default webcam
MIN_CONTOUR_AREA = 500  # Minimum area of motion to trigger sound (adjust as needed)
SOUND_DURATION = 0.1  # Duration of the sound in seconds
SAMPLE_RATE = 44100  # Samples per second for audio
BASE_FREQUENCY = 440  # Base frequency for the sound (A4 note)
FREQUENCY_MULTIPLIER = 0.5 # Adjusts how much motion impacts frequency
VOLUME_MULTIPLIER = 0.5 # Adjusts the volume of the sound (0.0 to 1.0)
SOUND_DELAY = 0.05 # Minimum delay between sounds to prevent rapid playback

# --- Global variables for sound control ---
last_sound_time = 0

# --- Audio Functions ---
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
    # Generate sine wave: 2 * pi * frequency * time
    amplitude_scaled = amplitude * 32767  # Max value for 16-bit signed integer
    audio = amplitude_scaled * np.sin(frequency * t * 2 * np.pi)
    # Convert to 16-bit integers
    audio = audio.astype(np.int16)
    return audio

def play_sound(frequency, volume=1.0):
    """
    Plays a short sine wave sound.

    Args:
        frequency (float): The frequency of the sound to play.
        volume (float): The volume level (0.0 to 1.0).
    """
    global last_sound_time
    current_time = time.time()

    if current_time - last_sound_time < SOUND_DELAY:
        return # Too soon to play another sound

    # Ensure frequency is positive and within a reasonable range
    frequency = max(100, min(2000, frequency))
    volume = max(0.0, min(1.0, volume))

    wave = generate_sine_wave(frequency, SOUND_DURATION, SAMPLE_RATE, amplitude=volume)
    play_obj = sa.play_buffer(wave, 1, 2, SAMPLE_RATE)
    # You can uncomment play_obj.wait_done() if you want the script to wait for sound to finish
    # before processing next frame, but it might cause lag.
    last_sound_time = current_time

# --- Main Program ---
def run_motion_sound_detector():
    """
    Initializes the webcam, detects motion, and plays sound based on movement.
    """
    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        print(f"Error: Could not open video stream from camera index {CAMERA_INDEX}.")
        print("Please check if the camera is connected and not in use by another application.")
        return

    print("Camera opened successfully. Press 'q' to quit.")

    # Read the first frame and convert to grayscale for background
    ret, frame1 = cap.read()
    if not ret:
        print("Error: Could not read first frame. Exiting.")
        return
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray1 = cv2.GaussianBlur(gray1, (21, 21), 0) # Apply Gaussian blur for smoothing

    while True:
        ret, frame2 = cap.read()
        if not ret:
            print("Reached end of stream or camera disconnected. Exiting.")
            break

        # Convert current frame to grayscale and blur
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)

        # Compute the absolute difference between the current frame and the previous frame
        frame_delta = cv2.absdiff(gray1, gray2)
        # Threshold the delta image to get areas of significant change
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        # Dilate the thresholded image to fill in holes
        thresh = cv2.dilate(thresh, None, iterations=2)

        # Find contours of the detected motion
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        motion_detected = False
        largest_area = 0
        center_x = 0
        center_y = 0
        contour_count = 0

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < MIN_CONTOUR_AREA:
                continue

            motion_detected = True
            contour_count += 1
            if area > largest_area:
                largest_area = area

            # Get bounding box for the contour and draw it on the original frame
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame2, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Calculate center of the largest motion for sound modulation
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                # We can use this center_x, center_y to modulate sound based on position
                # For simplicity, we'll use the largest contour's center.
                if area == largest_area:
                    center_x = cx
                    center_y = cy

        if motion_detected:
            # Modulate frequency based on the largest detected motion area and/or its position
            # Example: Larger area -> Higher frequency
            # Adjust the multiplier and offset to get desired sound behavior
            modulated_frequency = BASE_FREQUENCY + (largest_area * FREQUENCY_MULTIPLIER / 100)
            # You could also use center_x or center_y for additional modulation
            # e.g., modulated_frequency += (center_x / frame2.shape[1]) * 500

            # Modulate volume based on the number of contours or largest area
            # Example: More contours/larger area -> Higher volume
            modulated_volume = VOLUME_MULTIPLIER + (min(largest_area, 5000) / 5000.0) * (1.0 - VOLUME_MULTIPLIER)
            modulated_volume = min(1.0, modulated_volume) # Cap volume at 1.0

            play_sound(modulated_frequency, modulated_volume)

        # Display the resulting frame
        cv2.imshow("Motion Detector", frame2)
        cv2.imshow("Thresholded Motion", thresh) # Show the motion mask for debugging

        # Update the previous frame
        gray1 = gray2

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the capture and destroy all windows
    cap.release()
    cv2.destroyAllWindows()
    print("Application closed.")

if __name__ == "__main__":
    # Instructions for installing libraries:
    print("Please ensure you have the following Python libraries installed:")
    print("pip install opencv-python numpy simpleaudio")
    print("\nStarting motion sound detector...")
    run_motion_sound_detector()
