# Written (with love) by Lex Whalen

# This class is used to convert audio to wav. I was originally going to use SpeechRecognition,
# ...which needed .wav, but since I did not it is possible to get away with non-wav files I believe.

import os
from pydub import AudioSegment

class AudioConverter:
    """Converts audio to wav."""
    def __init__(self, FLDR_NAME):
        self.CWD = os.getcwd()
        self.FLDR_DIR = os.path.join(self.CWD,FLDR_NAME)
        self.CONVERT_FLDR = os.path.join(self.CWD,"wav_refs")

    def mass_convert(self):
        """Converts all audio found to wav if not already wav."""
        for f in os.listdir(self.FLDR_DIR):
            ext = os.path.splitext(f)[-1]
            if(ext != ".wav"):
                file_path = os.path.join(self.FLDR_DIR,f)
                new_file_name = f.split('.')[0] + ".wav"
                new_file_path = os.path.join(self.CONVERT_FLDR,new_file_name)
                self.convert_to_wav(file_path,new_file_path)


    def convert_to_wav(self,in_path,out_path):
        """Converts an audio file from mp3 to .wav."""
        sound = AudioSegment.from_mp3(in_path)
        sound.export(out_path,format = "wav")


# Examples
#test = AudioConverter("mixed_refs")
#test.mass_convert()
#test.mass_convert()
