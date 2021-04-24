# Written (with love) by Lex Whalen

# The main app.
# PLEASE let me know if there is any redundancy / stupidity when you see it. There surely is.
# I do not have time to refine the program at the moment, so just message me and point where you see the mistake.
# Thank you!

from basic_colors import *
from sprites import LineSprite
from audio_manager import AudioManager
from aud_img_database import AudImgDataBase

import pygame as pg
import threading
import os
import random
from PIL import Image
import time
import send2trash

class App():

    def __init__(self):
        # init pygame
        pg.init()
        pg.font.init()
        pg.mixer.init()
        pg.mixer.set_num_channels(8)

        # channels
        self.REF_AUD_CHAN = pg.mixer.Channel(5)
        self.YOUR_AUD_CHAN = pg.mixer.Channel(3)

        # clock
        self.CLOCK = pg.time.Clock()
        self.FPS = 30

        # file referencing
        self.CWD = os.getcwd()
        self.WAV_REFS = os.path.join(self.CWD,"wav_refs")
        self.WAV_IMG_REFS = os.path.join(self.CWD,"wav_img_refs")
        self.YOUR_RECS_FLDR = os.path.join(self.CWD,"your_recordings")

        # basic window attributes
        DISPLAY_W, DISPLAY_Y = pg.display.Info().current_w, pg.display.Info().current_h
        self.WIN_X = int(DISPLAY_W)
        self.WIN_Y = int(DISPLAY_Y)
        self.WIN = pg.display.set_mode((self.WIN_X,self.WIN_Y))
        pg.display.set_caption("Pronunciation Trainer")

        # basic font stuff
        self.FONT = pg.font.SysFont('Comic Sans MS',30)

        # for managing
        self.AUD_MAN = AudioManager()
        self.AUD_IMG_DATABASE = AudImgDataBase("wav_refs","wav_img_refs")
        self.PAIRINGS = self.AUD_IMG_DATABASE.PAIRINGS

        # for the png of the audio
        self.AUD_IMG_CENTER = (int(self.WIN_X//2),int(self.WIN_Y * 0.75))

        # the moving line
        self.LINE = None

        # for the audio / img changes
        self.REF_NAME = None
        self.REF_AUD = None
        self.REF_IMG= None
        self.REF_AUD_SND = None


        # for timing the audio
        self.AUD_FINISHED = False
        self.PLAYING_AUD = False
        self.CURRENT_AUD = None
        self.AUD_FIN_EVENT = pg.USEREVENT + 1

        # for when you record on your mic
        self.OUT_AUD_PATH = None
        self.OUT_AUD_IMG = None
        self.OUT_AUD_IMG_RECT = None

        # for indexing the audio
        self.AUD_INDEX = 0
        self.IS_RECORDING = False
        self.REC_AUD_PRESENT = False

        self.RUNNING = True

    def get_pg_img(self,f_path):
        return pg.image.load(f_path)

    def get_img_size(self,f_path):
        img = Image.open(f_path)
        # im.size is (w,h)
        return img.size
    
    def get_pg_snd(self,snd_path):
        return pg.mixer.Sound(snd_path)

    def get_random_pair(self):
        # PAIRINGS database uses paths relative to "Trainer" folder

        if self.AUD_INDEX == len(self.PAIRINGS) -1:
            # need to reset
            self.AUD_INDEX =0
        else:
            self.AUD_INDEX +=1

        selected_aud = self.PAIRINGS[self.AUD_INDEX].FIRST
        selected_img = self.PAIRINGS[self.AUD_INDEX].SECOND
        self.REF_NAME = self.PAIRINGS[self.AUD_INDEX].NAME

        return selected_aud,selected_img
    
    def reset_line_dx(self):
        aud_time_ms = int(self.AUD_MAN.get_aud_length(self.REF_AUD,milleseconds=True))
        ref_img_w = self.get_img_size(self.REF_IMG)[0]
        moves_per_loop = (aud_time_ms/1000) * self.FPS
        LINE_DX = ref_img_w /moves_per_loop

        return LINE_DX
    
    def create_your_aud_img(self,found_aud_path,f_name):
        # must wait for audio to finish, or get error
        time.sleep(0.5)
        self.AUD_MAN.create_wav_img(found_aud_path,f_name,color="red")

        self.OUT_AUD_IMG = self.get_pg_img(f_name)
        self.OUT_AUD_IMG_RECT = self.OUT_AUD_IMG.get_rect(center=(int(self.WIN_X//2),int(self.WIN_Y * 0.3)))

    def playing_audio_effects(self,aud_time_ms):
        # reset the audio
        self.AUD_FINISHED = False
        self.PLAYING_AUD = True


        pg.time.set_timer(self.AUD_FIN_EVENT,aud_time_ms)
        # play the self.REF_AUD
        self.REF_AUD_CHAN.play(self.REF_AUD_SND)

    def delete_recordings(self,your_rec_dir):
        if(len(your_rec_dir) !=0):
            for f in your_rec_dir:
                working_path = os.path.join(self.YOUR_RECS_FLDR,f)
                send2trash.send2trash(working_path)

    def run(self):

        # delete any prior recordings
        your_rec_dir = os.listdir(self.YOUR_RECS_FLDR)
        self.delete_recordings(your_rec_dir)
        

        controls_text_surf = self.FONT.render("R to record. P to play. S to switch audio file.",False,(0,0,0))
        aud_finished_text_surf = self.FONT.render("Audio Finished.",False,(255,0,0))

        # gets random img and aud
        self.REF_AUD,self.REF_IMG= self.get_random_pair()

        self.REF_AUD_SND = self.get_pg_snd(self.REF_AUD)

        # now we calculate the speed of line (d = vt, v = d/t)
        # 30 FPS -> "x" seconds * 30 FPS -> dx = distance/60
        aud_time_ms = int(self.AUD_MAN.get_aud_length(self.REF_AUD,milleseconds=True))
        ref_img_w = self.get_img_size(self.REF_IMG)[0]
        moves_per_loop = (aud_time_ms/1000) * self.FPS

        LINE_DX = ref_img_w /moves_per_loop
        
        ref_wave_img = self.get_pg_img(self.REF_IMG)
        ref_wave_rect = ref_wave_img.get_rect(center=self.AUD_IMG_CENTER)

        # update where the line is posistioned
        LINE_START_X = ref_wave_rect.left + 140
        LINE_START_Y = ref_wave_rect.top + 75
        LINE_H = 300
        LINE_W = 10

        self.LINE = LineSprite(self.WIN,LINE_START_X,LINE_START_Y,LINE_W,LINE_H,LINE_DX,color="red")

        while self.RUNNING:
            # constantly checks if you have updated your recordings
            your_rec_dir = os.listdir(self.YOUR_RECS_FLDR)

            # start with filling screen
            self.WIN.fill(WHITE)

            # blit referece audio wave images
            self.WIN.blit(ref_wave_img,ref_wave_rect)

            self.WIN.blit(controls_text_surf,(10,0))

            # blit moving line
            self.LINE.draw()

            # create img

            if len(your_rec_dir)!=0 and self.REC_AUD_PRESENT != True:
                for f in your_rec_dir:
                    if os.path.splitext(f)[-1] == ".wav":
                        self.REC_AUD_PRESENT = True
                        rec_aud_path = os.path.join(self.YOUR_RECS_FLDR,f)
                        f_name = "mic-{}.png".format(self.REF_NAME)
                        f_path = os.path.join(self.YOUR_RECS_FLDR,f_name)

                        threading.Thread(target=self.create_your_aud_img,args=[rec_aud_path,f_path]).start()

            if self.OUT_AUD_IMG != None and self.IS_RECORDING != True:
                self.WIN.blit(self.OUT_AUD_IMG,self.OUT_AUD_IMG_RECT)


            if(self.AUD_FINISHED):
                self.WIN.blit(aud_finished_text_surf,(1000,0))

            if self.PLAYING_AUD and self.LINE.RECT.x < ref_img_w + 80:
                self.LINE.update()
            
            
            # check events
            for event in pg.event.get():

                if event.type == self.AUD_FIN_EVENT:
                    self.AUD_FINISHED = True

                # check key presses
                elif event.type == pg.KEYDOWN:

                    # if key == "s", switch the audio
                    if event.key == pg.K_s and self.REF_AUD_CHAN.get_busy() != True:
                        # reset audio and image
                        self.OUT_AUD_IMG = None
                        self.OUT_AUD_PATH = None
                        self.delete_recordings(your_rec_dir)

                        # make sure we are not playing audio
                        self.PLAYING_AUD = False

                        self.REF_AUD,self.REF_IMG= self.get_random_pair()
                        self.REF_AUD_SND = self.get_pg_snd(self.REF_AUD)

                        # reset the line x
                        self.LINE.reset_line()
                        new_dx = self.reset_line_dx()
                        self.LINE.set_dx(new_dx)

                        # reset the audio length:
                        aud_time_ms = int(self.AUD_MAN.get_aud_length(self.REF_AUD,milleseconds=True))

                        ref_wave_img = self.get_pg_img(self.REF_IMG)
                        ref_wave_rect = ref_wave_img.get_rect(center=self.AUD_IMG_CENTER)


                    # check if key pressed == "r", then we record
                    if event.key == pg.K_r:
                        self.REC_AUD_PRESENT = False
                        
                        # reset the line x
                        self.LINE.reset_line()
                        new_dx = self.reset_line_dx()
                        self.LINE.set_dx(new_dx)
                        # reset the audio
                        self.AUD_FINISHED = False
                        self.PLAYING_AUD = True

                        # need to delete the recordings / imgs generated prior
                        self.delete_recordings(your_rec_dir)

                        # record your audio, need to thread baby!
                        duration = aud_time_ms / 1000
                        name = "mic-{}.wav".format(self.REF_NAME)
                        self.OUT_AUD_PATH = os.path.join(self.YOUR_RECS_FLDR,name)

                        threading.Thread(target=self.AUD_MAN.record_mic,args=[duration,self.OUT_AUD_PATH]).start()
                        threading.Thread(target=self.playing_audio_effects,args=[aud_time_ms]).start()
                        pg.time.set_timer(self.AUD_FIN_EVENT,aud_time_ms)

                        # play the self.REF_AUD
                        self.REF_AUD_CHAN.play(self.REF_AUD_SND)


                        
                    
                    # check if key press == "p", then we play the audio
                    elif event.key == pg.K_p:
                        # reset the line x
                        self.LINE.reset_line()
                        new_dx = self.reset_line_dx()
                        self.LINE.set_dx(new_dx)
                        # reset the audio
                        self.AUD_FINISHED = False
                        self.PLAYING_AUD = True

                        pg.time.set_timer(self.AUD_FIN_EVENT,aud_time_ms)

                        if self.OUT_AUD_PATH is not None:
                            your_snd = self.get_pg_snd(self.OUT_AUD_PATH)
                            self.YOUR_AUD_CHAN.play(your_snd)

                        self.REF_AUD_CHAN.play(self.REF_AUD_SND)

                    elif event.key == pg.K_q:
                        self.delete_recordings(your_rec_dir)
                        # quit prog
                        self.RUNNING = False

                
                # if event is quit, quit
                if event.type == pg.QUIT:
                    self.RUNNING = False


            # update the surf
            pg.display.update()
            self.CLOCK.tick(self.FPS)
        
        pg.quit()

if __name__ == "__main__":
    app = App()

    app.run()


    