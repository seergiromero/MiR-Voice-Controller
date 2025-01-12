import sounddevice as sd
from scipy.io.wavfile import write
import os
from faster_whisper import WhisperModel 
import pyaudio
import numpy as np
from pynput import keyboard
import tempfile

class Whisper_Live:
    """
    Class to manage all the transcript process
    The idea of the transcript process is the following:
       - The user will press the space bar on its keyboard to start recording.
       - A temporary file will be created recording everything the user says.
       - When it presses the space bar again, the code will stop recording and it will save the temporary file.
       - This temporary file will be transcripted with the AI faster whisper model.
       - Once transcripted, the temporary file will be deleted.
    """

    def __init__(self, model_size="small", device_id=15) -> None:
        """
        Init function, select the type of model and the device to be used as a microphone
        """
        # Fast Whisper Model AI
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")

        # Calculate automatically the sample rate and channels from the device information
        self.audio = pyaudio.PyAudio()
        device_info = self.audio.get_device_info_by_index(device_id)
        self.rate = int(device_info['defaultSampleRate'])
        self.channels = int(device_info['maxInputChannels'])

        self.is_recording = False

    def list_devices(self) -> None:
        """
        Function to list all the devices and check the available microphones
        """
        print("Available audio devices:")
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            print(f"ID {i}: {info['name']} - Input channels: {info['maxInputChannels']}")

    def select_device_id(self, device_id) -> None:
        """
        Function to select the device to use
        """
        device_info = self.audio.get_device_info_by_index(device_id)
        self.rate = int(device_info['defaultSampleRate'])
        self.channels = int(device_info['maxInputChannels'])
    
    def record(self): 
        """
        Function to record audio when the user presses the space bar
        """

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
    def start_recording(self, key) -> None:
        if key == keyboard.Key.space:
            if not self.is_recording:
                self.is_recording = True
                print('Recording')


    def stop_recording(self, key) -> None:
        if key == keyboard.Key.space:
            if self.is_recording:
                self.is_recording = False
                print("Stop recording")

    def temporary_file(self, recording) -> str:
        """
        Function to generate the temporary file
        """
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        write(temp_file.name, self.rate, recording)
        return temp_file.name
    
    
    def transcript_temporary_file(self, file_path) -> str:
        """
        Function to transcript the temporary file using the AI
        """
        segments, info = self.model.transcribe(file_path, beam_size=5)
        print("Language detected: '%s', Probability: '%f'" % (info.language, info.language_probability))
        transcription = ""
        for segment in segments:
            print(segment.text)
            transcription += segment.text + " "
        os.remove(file_path)
        return transcription
        
    def get_transcription(self) -> str:
        """
        Function where the transcription will be obtained
        """

        recording = self.record()
        file_path = self.temporary_file(recording)
        transcription = self.transcript_temporary_file(file_path)
        return transcription
        

