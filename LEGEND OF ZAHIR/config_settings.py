# Screen settings (pixel sizes)
WIDTH = 960
HEIGHT = 540
FPS = 60
TILESIZE = 48
BULLETSIZE = 16

# Layer settings
PLAYER_LAYER = 3
ENEMY_LAYER = 2
BLOCK_LAYER = 1
WALL_LAYER = 1

# Player settings
PLAYER_SPEED = 4
PLAYER_HEALTH = 100
PLAYER_DAMAGE = 10
PLAYER_KNOCKBACK = 5

# Enemy settings
ENEMY_SPEED = 2
ENEMY_HEALTH = 50
ENEMY_DAMAGE = 5
ENEMY_KNOCKBACK = 3

# Experience and leveling
EXP_YIELD = 20
EXP_TO_LEVEL = 100

# Knowledge Points
KP_YIELD = 5

# Colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)


# Game colors
BACKGROUND_COLOR = BLACK
TEXT_COLOR = WHITE
HEALTH_BAR_COLOR = RED
EXP_BAR_COLOR = BLUE
KP_COLOR = YELLOW

# Tilemap Legend:
# "." - Empty space
# "P" - Player starting position
# "W" - Wall
# "E" - Enemy spawn point
# "D" - Door position (initially hidden, will appear after enemies are defeated)

TILEMAP = [
    "WWWWWWWWWWWWWWWWWWWW",
    "W..................W",
    "W..................W",
    "W..................W",
    "W........E.........W",
    "W..................W",
    "W.......WPW........W",
    "W........E.........W",
    "W........D.........W",
    "W....E.............W",
    "W..................W",
    "W..................W",
    "W.........E........W",
    "W..................W",
    "WWWWWWWWWWWWWWWWWWWW"
]

# Alternative slightly more complex tilemap with corridors:
TILEMAP_ALTERNATE = [
    "WWWWWWWWWWWWWWWWWWWW",
    "W..............D...W",
    "W..................W",
    "W......WWWW........W",
    "W........E.........W",
    "W..................W",
    "W....WWW...........W",
    "W........E.........W",
    "W........P.........W",
    "W....E....WWWW.....W",
    "W..................W",
    "W.......WWW........W",
    "W.........E........W",
    "W..................W",
    "WWWWWWWWWWWWWWWWWWWW"
]

# You can choose which tilemap to use by setting:
# TILEMAP = TILEMAP_ALTERNATE  # For the more complex version

MEMORY_TILEMAP = [
    'WWWWWWWWWWWWWWWWWWWW',
    'W..................W',
    'W..................W',
    'W..................W',
    'W........WW........W',
    'W.......WWWW.......W',
    'W......WW..WW......W',
    'W.....WW....WW.....W',
    'W....WW......WW....W',
    'W...WW...P....WW...W',
    'W...WW........WW...W',
    'W....WW......WW....W',
    'W.....WW....WW.....W',
    'W......WW..WW......W',
    'W.......WWWW.......W',
    'W........WW........W',
    'W..................W',
    'W..................W',
    'W..................W',
    'WWWWWWWWWWWWWWWWWWWW'
]


# Game states
INTRO = 0
PLAYING = 1
GAME_OVER = 2

# Inventory
MAX_INVENTORY = 10

# Item types
HEALTH_POTION = 'health_potion'
KP_BOOST = 'kp_boost'
EXP_BOOST = 'exp_boost'

# Item effects
HEALTH_RESTORE = 50
KP_BOOST_AMOUNT = 20
EXP_BOOST_AMOUNT = 50

# Difficulty settings
EASY = 0
NORMAL = 1
HARD = 2

DIFFICULTY_MULTIPLIERS = {
    EASY: 0.5,
    NORMAL: 1.0,
    HARD: 1.5
}