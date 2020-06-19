import pygame
import os
from time import sleep


pygame.mixer.init()
pygame.mixer.fadeout(1000)
BASE_SOUND_FOLDER = "./sounds/"

class sound_folder():
    def __init__(self, folder, name):
        self.sounds = []
        self.folder = folder
        self.get_files()
        self.load_sounds()
        self.sound_sequence = (sound for sound in self.sounds)

    def __call__(self, *args, **kwargs):
        self.play()

    def get_files(self):
        self.files = os.listdir(self.folder)

    def load_sounds(self):
        for file in self.files:
            self.sounds.append(pygame.mixer.Sound(os.path.join(self.folder, file)))

    def play(self):
        try:
            sound = next(self.sound_sequence)
        except StopIteration:
            self.sound_sequence = (sound for sound in self.sounds)
            sound = next(self.sound_sequence)
        sound.play()

cannon_sound    = sound_folder(BASE_SOUND_FOLDER + "cannon/"   , "cannon"   )
explosion_sound = sound_folder(BASE_SOUND_FOLDER + "explosion/", "explosion")
# missed_sound    = sound_folder(BASE_SOUND_FOLDER + "missed/"   , "missed"   )
sunk_sound      = sound_folder(BASE_SOUND_FOLDER + "sunk/"     , "sunk"     )


if __name__ == "__main__":
    all_sounds = [cannon_sound, explosion_sound, sunk_sound]

    for sound in all_sounds:
        for _ in range(5):
            sound()
            sleep(0.5)
    sleep(5)
