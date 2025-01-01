import sounddevice as sd
from faster_whisper import WhisperModel 
import pyaudio
import numpy as np
from pynput import keyboard

# Function to list all the devices and check the available microphones
def list_devices():
    audio = pyaudio.PyAudio()
    print("Available audio devices:")
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        print(f"ID {i}: {info['name']} - Input channels: {info['maxInputChannels']}")
    audio.terminate()


# Class to manage all the transcript process
# The idea of the transcript process is the following:
#   - The user will press the space bar on its keyboard to start recording.
#   - A temporary file will be created recording everything the user says.
#   - When it presses the space bar again, the code will stop recording and it will save the temporary file.
#   - This temporary file will be transcripted with the AI faster whisper model.
#   - Once transcripted, the temporary file will be deleted.
class Whisper_Live:

    # Init function, select the type of model and the device to be used as a microphone
    def __init__(self, model_size="small", device_id=15):
        # Fast Whisper Model AI
        self.model = WhisperModel(model_size, device="cpu")

        # Calculate automatically the sample rate and channels from the device information
        audio = pyaudio.PyAudio()
        device_info = audio.get_device_info_by_index(device_id)
        self.rate = int(device_info['defaultSampleRate'])
        self.channels = int(device_info['maxInputChannels'])

        self.is_recording = False

    # Function to record audio when the user presses the space bar    
    # (NOT TESTED)
    def record(self): 

        # Creates an empty array with the channels shape to store the recorded audio
        recording = np.array([], dtype='float64').reshape(0,self.channels)

        # Calculate the number of frames to be recorded on each chunk
        frames_per_buffer = int(self.rate*0.1)

        # Listen to keyboard events to detect when the space bar is pressed to start recording
        with keyboard.Listener(on_press=self.start_recording, on_release=self.stop_recording) as listener:
            while True:
                # Once the space bar is pressed, it starts recording
                if self.is_recording:
                    chunk = sd.rec(frames_per_buffer, samplerate=self.rate, channels=self.channels, dtype="float64") # Recording chunks of audio
                    sd.wait() # Wait until chunk recording is finished
                    recording = np.vstack([recording, chunk]) # Stacked in the recording array

                # When the space bar is pressed again, then it breaks and returns the recording
                if not self.is_recording and len(recording) > 0:
                    break

        return recording

    # Functions to change is_recording value when space bar is pressed
    def start_recording(self, key):
        if key == keyboard.Key.space:
            if not self.is_recording:
                self.is_recording = True
                print('Recording')


    def stop_recording(self, key):
        if key == keyboard.Key.space:
            if self.is_recording:
                self.is_recording = False
                print("Stop recording")

    # Function to generate the temporary file
    def temporary_file(self):
        pass
    
    # Function to transcript the temporary file using the AI
    def transcript_temporary_file(self):
        pass

    # Main function where everything will be executed
    def main(self):
        pass

if __name__ == "__main__":
    list_devices() 
    device_id = int(input("Enter the input device ID (microphone): ")) # Here the user selects the device to use from the list

    # The above process has only to be executed once, then you can just put the device id directly as 
    # it will always be the same
    voice_to_text = Whisper_Live("small", device_id)
    voice_to_text.main()