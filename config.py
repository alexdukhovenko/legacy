import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
MAX_TOKENS = int(os.getenv('MAX_TOKENS', '2000'))
TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))

# Notion Configuration
NOTION_API_KEY = os.getenv('NOTION_API_KEY')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

# Audio processing settings
MAX_AUDIO_DURATION = 300  # 5 minutes in seconds
SUPPORTED_AUDIO_FORMATS = ['ogg', 'mp3', 'wav', 'm4a']

# File paths
TEMP_AUDIO_DIR = 'temp_audio'
OUTPUT_DIR = 'outputs'

# Create directories if they don't exist
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
