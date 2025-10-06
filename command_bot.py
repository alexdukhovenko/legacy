#!/usr/bin/env python3
"""
Простой бот с командами
Пользователь сам указывает, что делать с информацией
"""

import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

from config import TELEGRAM_BOT_TOKEN
from audio_processor_fixed import AudioProcessorFixed
from apple_integration import AppleCalendarIntegration
from notion_integration import NotionPlanner

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class CommandTelegramBot:
    """Простой бот с командами"""
    
    def __init__(self):
        self.audio_processor = AudioProcessorFixed()
        self.calendar = AppleCalendarIntegration()
        self.notion = NotionPlanner()
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🤖 *Простой AI Ассистент с командами*

*Как использовать:*

**Для календаря:**
• "Добавь в календарь: встреча завтра в 15:00"
• "Календарь: звонок в 10:30"
• "В календарь: событие в понедельник в 14:00"

**Для Notion:**
• "Сохрани в notion: идея для проекта"
• "Notion: заметка о важном"
• "В notion: план на неделю"

**Примеры:**
• "Добавь в календарь: разбор документов в МФЦ 27.09 в 10:00"
• "Сохрани в notion: идея создать мобильное приложение"

*Просто укажи, что делать с информацией!* 🚀
        """
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
📚 *Команды бота*

**📅 Календарь:**
• "добавь в календарь: [событие]"
• "календарь: [событие]"
• "в календарь: [событие]"

**📋 Notion:**
• "сохрани в notion: [информация]"
• "notion: [информация]"
• "в notion: [информация]"

**🎤 Голосовые сообщения:**
• Записывай голосовое с командой
• Бот распознает и выполнит действие

**Примеры:**
• "Добавь в календарь: встреча с клиентом завтра в 15:00"
• "Сохрани в notion: идея для нового проекта"
• "Календарь: звонок врачу в понедельник в 10:00"

*Все просто - указывай команду и информацию!* ✨
        """
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def handle_audio_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming audio/voice messages"""
        try:
            # Send processing message
            processing_msg = await update.message.reply_text("🔄 Обрабатываю аудиосообщение...")
            
            # Extract text from audio
            text = await self.audio_processor.process_audio_message(update, context)
            
            if not text:
                await processing_msg.edit_text("❌ Не удалось извлечь текст из аудио. Попробуй еще раз с более четкой речью.")
                return
            
            # Check if text is an error message
            if any(text.startswith(error) for error in [
                "Аудио слишком длинное", "Файл слишком большой", 
                "Неподдерживаемый формат", "Ошибка распознавания",
                "❌ Ошибка распознавания", "Whisper API недоступен"
            ]):
                await processing_msg.edit_text(text, parse_mode='Markdown')
                return
            
            # Process the command
            await self._process_command(text, processing_msg, update.effective_user.id)
                
        except Exception as e:
            logger.error(f"Error handling audio message: {e}")
            await update.message.reply_text("❌ Произошла ошибка при обработке аудиосообщения.")
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming text messages"""
        try:
            text = update.message.text
            
            # Skip if it's a command
            if text.startswith('/'):
                return
            
            # Process the command
            await self._process_command(text, update.message, update.effective_user.id)
                
        except Exception as e:
            logger.error(f"Error handling text message: {e}")
            await update.message.reply_text("❌ Произошла ошибка при обработке сообщения.")
    
    async def _process_command(self, text: str, message_obj, user_id: int):
        """Process command from text"""
        text_lower = text.lower()
        
        # Check for calendar commands
        calendar_keywords = ["добавь в календарь", "календарь:", "в календарь"]
        for keyword in calendar_keywords:
            if keyword in text_lower:
                # Extract event text
                event_text = text[text.lower().find(keyword) + len(keyword):].strip()
                if event_text.startswith(':'):
                    event_text = event_text[1:].strip()
                
                await self._add_to_calendar(event_text, message_obj)
                return
        
        # Check for notion commands
        notion_keywords = ["сохрани в notion", "notion:", "в notion"]
        for keyword in notion_keywords:
            if keyword in text_lower:
                # Extract content text
                content_text = text[text.lower().find(keyword) + len(keyword):].strip()
                if content_text.startswith(':'):
                    content_text = content_text[1:].strip()
                
                await self._add_to_notion(content_text, message_obj)
                return
        
        # If no command found, show help
        await message_obj.reply_text(
            "❓ Не понял команду. Используй:\n\n"
            "📅 **Календарь:** 'добавь в календарь: [событие]'\n"
            "📋 **Notion:** 'сохрани в notion: [информация]'\n\n"
            "Пример: 'Добавь в календарь: встреча завтра в 15:00'",
            parse_mode='Markdown'
        )
    
    async def _add_to_calendar(self, event_text: str, message_obj):
        """Add event to calendar"""
        try:
            # Try to extract time from text
            event_time = self._extract_time_from_text(event_text)
            
            result = await self.calendar.create_event(
                title=event_text,
                start_time=event_time,
                duration=60  # 1 hour default
            )
            
            if result.get("success", False):
                await message_obj.reply_text(
                    f"📅 **СОБЫТИЕ** добавлено в Apple Calendar!\n\n"
                    f"**Событие:** {event_text}\n"
                    f"**Время:** {event_time.strftime('%H:%M %d.%m.%Y')}",
                    parse_mode='Markdown'
                )
            else:
                await message_obj.reply_text(f"❌ Ошибка добавления в календарь: {result.get('error', 'Неизвестная ошибка')}")
                
        except Exception as e:
            logger.error(f"Error adding to calendar: {e}")
            await message_obj.reply_text(f"❌ Ошибка добавления в календарь: {str(e)}")
    
    async def _add_to_notion(self, content_text: str, message_obj):
        """Add content to Notion"""
        try:
            result = await self.notion.create_material_entry(
                title=f"📝 {content_text[:50]}...",
                content=content_text,
                category="notes",
                tags=["заметка", "пользователь"]
            )
            
            if result:
                await message_obj.reply_text(
                    f"📋 **ИНФОРМАЦИЯ** сохранена в Notion!\n\n"
                    f"**Содержание:** {content_text}",
                    parse_mode='Markdown'
                )
            else:
                await message_obj.reply_text("❌ Ошибка сохранения в Notion")
                
        except Exception as e:
            logger.error(f"Error adding to Notion: {e}")
            await message_obj.reply_text(f"❌ Ошибка сохранения в Notion: {str(e)}")
    
    def _extract_time_from_text(self, text: str):
        """Extract time from text"""
        import re
        from datetime import datetime, timedelta
        
        text_lower = text.lower()
        
        # Look for time patterns
        time_patterns = [
            r'(\d{1,2}):(\d{2})',  # 15:30
            r'(\d{1,2})\.(\d{2})',  # 15.30
            r'в (\d{1,2})',  # в 15
        ]
        
        hour = 12  # Default hour
        minute = 0  # Default minute
        
        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    hour = int(match.group(1))
                    minute = int(match.group(2)) if len(match.groups()) > 1 else 0
                    
                    if 0 <= hour <= 23 and 0 <= minute <= 59:
                        break
                except (ValueError, IndexError):
                    continue
        
        # Determine date
        event_date = self._determine_date(text_lower)
        return event_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    def _determine_date(self, text_lower: str):
        """Determine date from text"""
        from datetime import datetime, timedelta
        
        now = datetime.now()
        
        # Today
        if any(word in text_lower for word in ["сегодня", "сейчас"]):
            return now
        
        # Tomorrow
        if "завтра" in text_lower:
            return now + timedelta(days=1)
        
        # Specific dates
        if "27.09" in text_lower or "27 сентября" in text_lower:
            return now.replace(month=9, day=27, hour=12, minute=0, second=0, microsecond=0)
        
        # Weekdays
        weekdays = {
            "понедельник": 0, "вторник": 1, "среда": 2, "четверг": 3,
            "пятница": 4, "суббота": 5, "воскресенье": 6
        }
        
        for day, day_num in weekdays.items():
            if day in text_lower:
                days_ahead = day_num - now.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                return now + timedelta(days=days_ahead)
        
        # Default: tomorrow
        return now + timedelta(days=1)
    
    def run(self):
        """Run the bot"""
        # Create application
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        
        # Handle audio and voice messages
        application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, self.handle_audio_message))
        
        # Handle text messages
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        
        # Start the bot
        logger.info("Starting Command Telegram Bot...")
        application.run_polling()

if __name__ == "__main__":
    bot = CommandTelegramBot()
    bot.run()
