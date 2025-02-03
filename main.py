from Whisper_Live import Whisper_Live
from transcript_post_processing import PostProcessing
from rest import RobotAPI
import spacy

def main():

    #wl = Whisper_Live("large")
    pp = PostProcessing()

    #wl.list_devices() 
    #device_id = int(input("Enter the input device ID (microphone): ")) # Here the user selects the device to use from the list
    #wl.select_device_id(device_id)

    #print("------- Hold spacebar to start recording -------")

    while True:

        #phrase = wl.get_transcription()
        #print("------- Hold spacebar to start recording -------")
        
        phrase = str(input("Send an order: "))
        pp.run_model(phrase)

        
if __name__ == "__main__":

    main()