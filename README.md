# Breath Fog Treasure Game

This is an interactive game based on OpenCV and camera. Players trigger fog effects by making an "O" mouth shape breathing action, then use their hands to clear the fog and discover a hidden Christmas tree with music playing.

## Features

1. **Mouth Detection**: Use MediaPipe to detect faces and recognize O-shaped mouth breathing action
2. **Hand Detection**: Detect hand positions for interactive fog clearing
3. **Fog Effects**: Dynamic fog generation and display with erase functionality
4. **Christmas Tree Display**: Show Christmas tree image after clearing fog
5. **Background Music**: Play Christmas music when tree is discovered
6. **User Interface**: Real-time display of game status and operation hints

## System Requirements

- Python 3.8+
- Camera (built-in or external)
- Good lighting conditions

## Installation Steps

1. Clone or download this project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
##🚀 How to Play
#Start the game:

```bash
python main.py
```

Make "O" mouth shape:

Face the camera

Form an "O" shape with your mouth

Hold for about 1 second to trigger fog

Clear the fog:

Use your hand to make wiping motions in front of the camera

The fog will clear where your hand moves

Discover the treasure:

When all fog is cleared, a Christmas tree appears

Festive music starts playing automatically

🎯 Controls
Key	Action
q	Quit the game
r	Reset the game
Esc	Exit (alternative)
📁 Project Structure
```
breath_fog_game/
├── main.py                    # Main game loop and interface
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── LICENSE                    # MIT License
├── .gitignore                 # Git ignore rules
├── assets/                    # Media files
│   ├── tree.png              # Christmas tree image
│   └── music.mp3             # Background music
├── modules/                   # Core game modules
│   ├── face_detector.py      # Face and mouth detection
│   ├── hand_detector.py      # Hand detection
│   ├── fog_effect.py         # Fog generation and effects
│   └── game_logic.py         # Game state management
└── utils/                     # Utility functions
    ├── audio_player.py       # Audio playback
    └── image_utils.py        # Image processing helpers
```
