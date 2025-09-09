# Game Configuration
import pygame
import os

# Screen settings
GAME_WIDTH = 1200
GAME_HEIGHT = 800
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)

# Enhanced Colors for better design
SKY_BLUE = (135, 206, 235)
DEEP_BLUE = (25, 25, 112)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
FOREST_GREEN = (34, 139, 34)
LIME_GREEN = (50, 205, 50)
CORAL = (255, 127, 80)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# Gradient colors
GRADIENT_START = (135, 206, 250)
GRADIENT_END = (70, 130, 180)

# Pipe colors
PIPE_GREEN = (34, 139, 34)
PIPE_DARK = (0, 100, 0)
PIPE_HIGHLIGHT = (144, 238, 144)

# Game settings
GRAVITY = 0.8
JUMP_STRENGTH = -12
PIPE_WIDTH = 100
PIPE_GAP = 280  # Increased gap for better gameplay
PIPE_SPEED = 5
PIPE_SPAWN_TIME = 2200  # milliseconds - adjusted for larger screen
SPEED_INCREASE = 0.2  # Speed increase per pipe passed

# Player settings
PLAYER_SIZE = 60
PLAYER_X = 200

# Font settings
FONT_SIZE_LARGE = 64
FONT_SIZE_MEDIUM = 48
FONT_SIZE_SMALL = 32

# File paths
BIRD_IMAGE = os.path.join("images", "bird_850x594.png")
RANKING_FILE = "rankings.json"

# Game states
LOBBY = 0
PLAYING = 1
GAME_OVER = 2

# Input settings
MAX_ID_LENGTH = 5
