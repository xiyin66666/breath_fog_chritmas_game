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