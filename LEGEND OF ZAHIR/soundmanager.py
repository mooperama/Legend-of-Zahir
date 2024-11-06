import pygame
import os
class SoundManager:
    """
    A class to manage all sound-related functionality for the game.
    This class centralizes sound loading, playing, and stopping, making it easier to manage audio across the entire game.
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
        self.sound_path = os.path.join('LEGEND OF ZAHIR', 'assets', 'sounds')
        
        # Load all game sounds at initialization
        self.load_sound('bullet', 'fireball.mp3')
        self.load_sound('button_click', 'buttons.mp3')
        # Add any other game sounds here
        
        # Load background music
        self.load_music('A_Journey_Awaits.mp3')
        
        # Set default volume levels
        self.set_sound_volume(0.5)  # 50% volume for sound effects
        self.set_music_volume(0.3)  # 30% volume for background music

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
        """
        try:
            file_path = self.get_sound_path('sfx', filename)
            sound = pygame.mixer.Sound(file_path)
            self.sounds[name] = sound
            print(f"Successfully loaded sound: {name}")
        except pygame.error as e:
            print(f"Error loading sound {filename}: {e}")
        except FileNotFoundError:
            print(f"Sound file not found: {filename}")

    def play_sound(self, name):
        """
        Play a loaded sound effect.
        
        Args:
            name (str): The name of the sound to play.
        """
        if name in self.sounds:
            try:
                self.sounds[name].play()
            except pygame.error as e:
                print(f"Error playing sound {name}: {e}")
        else:
            print(f"Sound '{name}' not found")

    def stop_sound(self, name):
        """
        Stop a currently playing sound effect.
        
        Args:
            name (str): The name of the sound to stop.
        """
        if name in self.sounds:
            try:
                self.sounds[name].stop()
            except pygame.error as e:
                print(f"Error stopping sound {name}: {e}")
        else:
            print(f"Sound '{name}' not found")

    def set_sound_volume(self, volume):
        """
        Set the volume for all sound effects.
        
        Args:
            volume (float): Volume level between 0.0 and 1.0
        """
        for sound in self.sounds.values():
            sound.set_volume(volume)

    def load_music(self, filename):
        """
        Load background music.
        
        Args:
            filename (str): The filename of the music file (without path).
        """
        try:
            file_path = self.get_sound_path('bgm', filename)
            pygame.mixer.music.load(file_path)
            self.music = file_path
            print(f"Successfully loaded music: {filename}")
        except pygame.error as e:
            print(f"Error loading music {filename}: {e}")
        except FileNotFoundError:
            print(f"Music file not found: {filename}")

    def play_music(self, loops=-1):
        """
        Play the loaded background music.
        
        Args:
            loops (int): Number of times to loop the music. -1 for infinite loop.
        """
        if self.music:
            try:
                pygame.mixer.music.play(loops)
            except pygame.error as e:
                print(f"Error playing music: {e}")
        else:
            print("No music loaded")

    def stop_music(self):
        """Stop the currently playing background music."""
        pygame.mixer.music.stop()

    def set_music_volume(self, volume):
        """
        Set the volume for background music.
        
        Args:
            volume (float): Volume level between 0.0 and 1.0
        """
        pygame.mixer.music.set_volume(volume)

    def pause_music(self):
        """Pause the currently playing background music."""
        pygame.mixer.music.pause()

    def unpause_music(self):
        """Resume the paused background music."""
        pygame.mixer.music.unpause()

# Create a global instance of SoundManager
sound_manager = SoundManager()