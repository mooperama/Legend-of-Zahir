import pygame
import os

class SoundManager:
    """
    A class to manage all sound-related functionality for the game.
    
    This class centralizes sound loading, playing, and stopping,
    making it easier to manage audio across the entire game.
    It now uses a more organized folder structure for sound assets.
    """

    def __init__(self):
        """
        Initialize the SoundManager.
        
        Sets up the pygame mixer and initializes dictionaries for sounds and music.
        """
        pygame.mixer.init()
        self.sounds = {}
        self.music = None
        self.sound_path = os.path.join('assets', 'sounds',)

    def get_sound_path(self, folder, filename):
        """
        Construct the full path for a sound file.

        Args:
            folder (str): The subfolder ('sfx' or 'bgm').
            filename (str): The name of the sound file.

        Returns:
            str: The full path to the sound file.
        """
        return os.path.join(self.sound_path, folder, filename)

    def load_sound(self, name, filename):
        """
        Load a sound effect and store it in the sounds dictionary.

        Args:
            name (str): The name to associate with the sound.
            filename (str): The filename of the sound file (without path).

        This method allows for easier sound management and error handling.
        """
        try:
            file_path = self.get_sound_path('sfx', filename)
            sound = pygame.mixer.Sound(file_path)
            self.sounds[name] = sound
        except pygame.error as e:
            print(f"Error loading sound {filename}: {e}")

    def play_sound(self, name):
        """
        Play a loaded sound effect.

        Args:
            name (str): The name of the sound to play.

        This method centralizes sound playing and includes error handling.
        """
        if name in self.sounds:
            self.sounds[name].play()
        else:
            print(f"Sound '{name}' not found")

    def stop_sound(self, name):
        """
        Stop a currently playing sound effect.

        Args:
            name (str): The name of the sound to stop.

        This method allows for more control over sound playback.
        """
        if name in self.sounds:
            self.sounds[name].stop()
        else:
            print(f"Sound '{name}' not found")

    def load_music(self, filename):
        """
        Load background music.

        Args:
            filename (str): The filename of the music file (without path).

        This method separates music loading from sound effect loading.
        """
        try:
            file_path = self.get_sound_path('bgm', filename)
            pygame.mixer.music.load(file_path)
            self.music = file_path
        except pygame.error as e:
            print(f"Error loading music {filename}: {e}")

    def play_music(self, loops=-1):
        """
        Play the loaded background music.

        Args:
            loops (int): Number of times to loop the music. -1 for infinite loop.

        This method centralizes music playback control.
        """
        if self.music:
            pygame.mixer.music.play(loops)
        else:
            print("No music loaded")

    def stop_music(self):
        """
        Stop the currently playing background music.

        This method provides a way to stop background music when needed.
        """
        pygame.mixer.music.stop()

# Create a global instance of SoundManager
sound_manager = SoundManager()

# Load all game sounds
sound_manager.load_sound('bullet', 'ineedmorebullets.wav')


# Load background music
sound_manager.load_music('background_music.wav')
