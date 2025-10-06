import os
import io
import logging
from typing import Optional
import speech_recognition as sr
import subprocess
from pydub import AudioSegment
import requests
from telegram import Update
from telegram.ext import ContextTypes
import openai
from openai import AsyncOpenAI

from config import TEMP_AUDIO_DIR, MAX_AUDIO_DURATION, SUPPORTED_AUDIO_FORMATS, OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        
    async def download_audio(self, file_path: str, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
        """Download audio file from Telegram"""
        try:
            # Get file info
            file = await context.bot.get_file(file_path)
            
            # Download file
            audio_data = await file.download_as_bytearray()
            
            # Save to temporary file
            temp_filename = f"{TEMP_AUDIO_DIR}/audio_{file_path.split('/')[-1]}.ogg"
            with open(temp_filename, 'wb') as f:
                f.write(audio_data)
                
            logger.info(f"Audio downloaded: {temp_filename}")
            return temp_filename
            
        except Exception as e:
            logger.error(f"Error downloading audio: {e}")
            return None
    
    def convert_audio_format(self, input_path: str) -> Optional[str]:
        """Convert audio to WAV format for speech recognition"""
        try:
            # Load audio file
            audio = AudioSegment.from_file(input_path)
            
            # Check duration
            duration = len(audio) / 1000  # Convert to seconds
            if duration > MAX_AUDIO_DURATION:
                logger.warning(f"Audio too long: {duration}s, max allowed: {MAX_AUDIO_DURATION}s")
                return None
            
            # Convert to WAV
            output_path = input_path.replace('.ogg', '.wav')
            audio.export(output_path, format="wav")
            
            logger.info(f"Audio converted: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error converting audio: {e}")
            return None
    
    async def extract_text_from_audio(self, audio_path: str) -> Optional[str]:
        """Extract text from audio using OpenAI Whisper"""
        try:
            # Check file size and duration first
            file_size = os.path.getsize(audio_path)
            if file_size > 25 * 1024 * 1024:  # 25MB limit for Whisper
                logger.error(f"File too large: {file_size / 1024 / 1024:.1f}MB")
                return "Файл слишком большой. Попробуй аудио до 5 минут."
            
            # Try OpenAI Whisper
            with open(audio_path, 'rb') as audio_file:
                transcript = await self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ru"
                )
                text = transcript.text
                logger.info(f"Text extracted with Whisper: {text[:100]}...")
                return text
                
        except Exception as e:
            logger.error(f"Whisper failed: {e}")
            # Return error message instead of trying fallback
            if "Invalid file format" in str(e):
                return "Неподдерживаемый формат аудио. Попробуй другое сообщение."
            elif "duration" in str(e).lower():
                return "Аудио слишком длинное. Попробуй сообщение до 5 минут."
            else:
                return f"Ошибка распознавания: {str(e)[:100]}"
    
    def cleanup_temp_files(self, *file_paths):
        """Clean up temporary files"""
        for file_path in file_paths:
            try:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Cleaned up: {file_path}")
            except Exception as e:
                logger.error(f"Error cleaning up {file_path}: {e}")
    
    async def process_audio_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
        """Main method to process audio message and extract text"""
        try:
            # Get audio file
            audio = update.message.voice or update.message.audio
            if not audio:
                return None
            
            # Check duration first
            duration = audio.duration if hasattr(audio, 'duration') else 0
            if duration > MAX_AUDIO_DURATION:
                return f"Аудио слишком длинное ({duration} сек). Максимум {MAX_AUDIO_DURATION} секунд."
            
            # Download audio
            audio_path = await self.download_audio(audio.file_id, context)
            if not audio_path:
                return None
            
            # Try to extract text directly from OGG file with Whisper
            text = await self.extract_text_from_audio(audio_path)
            
            # Cleanup
            self.cleanup_temp_files(audio_path)
            
            return text
            
        except Exception as e:
            logger.error(f"Error processing audio message: {e}")
            return None
