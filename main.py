from Whisper_Live import Whisper_Live
from transcript_post_processing import PostProcessing
from rest import Rest_API


def main():

    #wl = Whisper_Live("small")
    #wl.list_devices() 
    #device_id = int(input("Enter the input device ID (microphone): ")) # Here the user selects the device to use from the list
    #wl.select_device_id(device_id)

    #print("------- Hold spacebar to start recording -------")
    #while True:

    #    wl.get_transcription()
    #    print("------- Hold spacebar to start recording -------")

    #pp = PostProcessing()
    #pp.analyze_phrase("MoVe to the position A", "go")

    ra = Rest_API()
    ra.select_robot("mir200")
    print(ra.get_positions())
    print(ra.get_missions())
    ra.execute_mission("footprint")
    ra.go_to("POS1")
if __name__ == "__main__":

    main()