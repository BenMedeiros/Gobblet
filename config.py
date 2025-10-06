# Gobblet Simulator Configuration

# Default simulation settings
BOARD_SIZE = 4
MAX_TURNS = 200
DEFAULT_GAMES = 10

# Available strategies
STRATEGIES = ["random", "greedy", "defensive"]

# Data storage
DEFAULT_DATA_FILE = "data/games.json"
BACKUP_DATA_FILE = "data/games_backup.json"

# Analysis settings
MIN_GAMES_FOR_ANALYSIS = 5
PLOT_DPI = 300
PLOT_STYLE = "seaborn"

# Performance settings
DEFAULT_THREAD_COUNT = 4
BATCH_SIZE = 100
