# Written (with love) by Lex Whalen

# This class manages all audio operations, such as generation of wav graphs with matplotlib,
# ...and getting the length of audio.

import matplotlib.pyplot as plt
import sounddevice as sd
import soundfile as sf
import numpy as np
import wave
import sys
import os
import contextlib

class AudioManager():
    """Manages audio operations"""

    def __init__(self):
        self.CWD = os.getcwd()
        self.SAMPLE_RATE = 44100 # Hertz


    def record_mic(self,duration,out_path):
        """Records audio from mic for "duration" seconds. """
        out_aud = sd.rec(int(self.SAMPLE_RATE * duration), samplerate = self.SAMPLE_RATE, 
        channels = 1,blocking = True)

        sf.write(out_path,out_aud,self.SAMPLE_RATE)

    def mass_wav_img(self,in_path,out_path):
        """Mass generates audio pngs of waves. in_path is the 
        path of the audio folder, out_path is for the new images"""
        for f_path in os.listdir(in_path):
            work_path = os.path.join(in_path,f_path)
            f_title = os.path.basename(f_path).split('.')[0]
            new_path = os.path.join(out_path,f_title)

            self.create_wav_img(work_path,new_path)

    def create_wav_img(self,in_path,out_path,color="blue",graph_dim=(20,5)):
        """Creates a waveform image from a .wav file."""
        # takes in a file path and a tuple of x_scale and y_scale

        f_title = os.path.basename(in_path).split('.')[0]

        spf = wave.open(in_path,"r")

        fs = spf.getframerate()

        # extract the raw audio from wav
        signal = spf.readframes(-1) #-1 means read all frames
        signal = np.frombuffer(signal,"int16")
        
        # get the time length
        time_length = np.linspace(0, len(signal) / fs, num=len(signal))



        # graph formatting
        plt.figure(figsize=graph_dim)
        plt.rc('font',family = "Meiryo")

        plt.title("Audio: {}".format(f_title))
        plt.plot(time_length,signal,color)
        plt.xlabel('Time [sec]')
        
        plt.savefig(out_path,bbox_inches='tight')

    def get_aud_length(self,f_path,milleseconds = False):
        with contextlib.closing(wave.open(f_path,"r")) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            dur = frames / float(rate)
            if milleseconds:
                dur = dur * 1000
            return dur

# Examples
#test = AudioManager()
#print(test.get_aud_length("test.wav",True))
#test.mass_wav_img("wav_refs","wav_img_refs")
#test.record_mic(2,"test.wav")
#test.create_wav_img("D:\Desktop\Trainer\your_recordings\mic-雨.wav","test.png")

