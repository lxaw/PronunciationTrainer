# Written (with love) by Lex Whalen

# This class serves as a database of audio-image pairings.
# Used to reference a pair of audio and images, so you can grab either file type.

import os
from pair import Pair


class AudImgDataBase():
    """Stores all audio-img pairs"""
    def __init__(self,wav_fldr,img_fldr):

        # file referencing
        self.CWD = os.getcwd()

        # req folders
        self.WAV_FLDR = wav_fldr
        self.IMG_FLDR = img_fldr

        # pairings is a list of pairs
        self.PAIRINGS = []

        # initialized the pairings
        self.init_pair_list()

    def get_file_title(self,f):
        return os.path.basename(f).split(".")[0]

    def get_working_path(self,f,fldr):
        return os.path.join(fldr,f)

    def init_pair_list(self):
        """Loops through the wav and img folders, if files have same name pairs them"""
        for aud_f in os.listdir(self.WAV_FLDR):
            # need title to check, and need to get the path of the file
            aud_title = self.get_file_title(aud_f)

            working_aud_path = self.get_working_path(aud_f,self.WAV_FLDR)

            for img_f in os.listdir(self.IMG_FLDR):
                img_title = self.get_file_title(img_f)
                working_img_path = self.get_working_path(img_f,self.IMG_FLDR)
                if(aud_title == img_title):
                    # get a match, make a pairing
                    self.PAIRINGS.append(Pair(aud_title,working_aud_path,working_img_path))
    
    def print_pairings(self):
        for pair in self.PAIRINGS:
            print("Name: {} -- First: {} -- Second: {}".format(pair.NAME,pair.FIRST,pair.SECOND))

# Examples
#test = AudImgDataBase("wav_refs","wav_img_refs")
#test.print_pairings()
