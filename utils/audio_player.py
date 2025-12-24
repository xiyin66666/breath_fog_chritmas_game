"""
Audio player module
Using Pygame to play background music with fallback options
"""
import os
import sys

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Warning: pygame not installed, audio playback will use fallback methods")

class AudioPlayer:
    def __init__(self):
        """Initialize audio player"""
        self.mixer_initialized = False
        self.current_music = None
        self.volume = 0.5  # Default volume
        self.use_pygame = True  # Try to use pygame first
        
        # Try multiple initialization methods
        self.initialize_audio_system()
    
    def initialize_audio_system(self):
        """Initialize audio system with multiple fallback methods"""
        # Method 1: Try pygame mixer
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self.mixer_initialized = True
                print("Audio system initialized successfully using pygame")
                self.use_pygame = True
                return
            except Exception as e:
                print(f"Pygame audio initialization failed: {e}")
                self.use_pygame = False
        
        # Method 2: Try using system commands as fallback
        print("Using system command fallback for audio playback")
        self.mixer_initialized = True  # Mark as initialized for fallback
        self.use_pygame = False
    
    def play(self, filepath, loops=0):
        """
        Play audio file
        
        Args:
            filepath: Audio file path
            loops: Number of loops, 0 for play once, -1 for infinite loop
            
        Returns:
            True if playback started successfully, False otherwise
        """
        if not os.path.exists(filepath):
            print(f"Audio file does not exist: {filepath}")
            return False
        
        # Stop any currently playing audio
        self.stop()
        
        # Try pygame first
        if self.use_pygame and PYGAME_AVAILABLE:
            try:
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.set_volume(self.volume)
                
                # Convert loops parameter for pygame
                # pygame uses -1 for infinite loops, 0 for play once, n for n+1 plays
                if loops == -1:
                    pygame_loops = -1
                elif loops == 0:
                    pygame_loops = 0
                else:
                    pygame_loops = loops - 1
                
                pygame.mixer.music.play(loops=pygame_loops)
                self.current_music = filepath
                print(f"Playing audio with pygame: {os.path.basename(filepath)}")
                return True
            except Exception as e:
                print(f"Failed to play audio with pygame: {e}")
                self.use_pygame = False  # Disable pygame for future attempts
        
        # Fallback method: Use system command
        return self.play_with_system_command(filepath, loops)
    
    def play_with_system_command(self, filepath, loops):
        """Play audio using system command as fallback"""
        import platform
        import subprocess
        import threading
        
        system = platform.system()
        basename = os.path.basename(filepath)
        
        def play_command():
            try:
                if system == "Windows":
                    # Windows - use start command
                    import winsound
                    try:
                        # Try to play as WAV file
                        winsound.PlaySound(filepath, winsound.SND_FILENAME | winsound.SND_ASYNC)
                        print(f"Playing audio with winsound: {basename}")
                    except:
                        # Fallback to using mpg123 or similar if installed
                        try:
                            subprocess.Popen(['mpg123', '-q', filepath])
                            print(f"Playing audio with mpg123: {basename}")
                        except:
                            print(f"Windows audio playback not available for: {basename}")
                
                elif system == "Darwin":  # macOS
                    # macOS - use afplay
                    cmd = ['afplay', filepath]
                    if loops > 0:
                        cmd.extend(['-l', str(loops)])
                    subprocess.Popen(cmd)
                    print(f"Playing audio with afplay: {basename}")
                
                elif system == "Linux":
                    # Linux - try multiple players
                    players = ['mpg123', 'mpg321', 'ffplay', 'aplay']
                    for player in players:
                        try:
                            cmd = [player]
                            if player in ['mpg123', 'mpg321']:
                                cmd.extend(['-q', filepath])
                            elif player == 'ffplay':
                                cmd.extend(['-nodisp', '-autoexit', filepath])
                            elif player == 'aplay':
                                cmd.append(filepath)
                            
                            subprocess.Popen(cmd)
                            print(f"Playing audio with {player}: {basename}")
                            return
                        except FileNotFoundError:
                            continue
                    print(f"No audio player found on Linux for: {basename}")
                
                else:
                    print(f"Unsupported system for audio playback: {system}")
            
            except Exception as e:
                print(f"System command audio playback failed: {e}")
        
        # Start playback in a separate thread to avoid blocking
        thread = threading.Thread(target=play_command, daemon=True)
        thread.start()
        
        self.current_music = filepath
        return True
    
    def stop(self):
        """Stop playing audio"""
        if self.use_pygame and PYGAME_AVAILABLE and self.mixer_initialized:
            try:
                pygame.mixer.music.stop()
            except:
                pass
        
        self.current_music = None
    
    def pause(self):
        """Pause audio playback"""
        if self.use_pygame and PYGAME_AVAILABLE and self.mixer_initialized:
            try:
                pygame.mixer.music.pause()
            except:
                pass
    
    def unpause(self):
        """Resume audio playback"""
        if self.use_pygame and PYGAME_AVAILABLE and self.mixer_initialized:
            try:
                pygame.mixer.music.unpause()
            except:
                pass
    
    def set_volume(self, volume):
        """
        Set volume
        
        Args:
            volume: Volume value (0.0 - 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        if self.use_pygame and PYGAME_AVAILABLE and self.mixer_initialized:
            try:
                pygame.mixer.music.set_volume(self.volume)
            except:
                pass
    
    def get_volume(self):
        """Get current volume"""
        return self.volume
    
    def is_playing(self):
        """Check if audio is playing"""
        if self.use_pygame and PYGAME_AVAILABLE and self.mixer_initialized:
            try:
                return pygame.mixer.music.get_busy()
            except:
                return False
        
        # For system command playback, we can't easily check if it's still playing
        # Return True if we have a current music file, False otherwise
        return self.current_music is not None
    
    def fadeout(self, duration_ms=1000):
        """
        Fade out audio
        
        Args:
            duration_ms: Fade out duration (milliseconds)
        """
        if self.use_pygame and PYGAME_AVAILABLE and self.mixer_initialized:
            try:
                pygame.mixer.music.fadeout(duration_ms)
            except:
                pass
        
        self.current_music = None