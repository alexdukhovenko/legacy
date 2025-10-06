#!/usr/bin/env python3
"""
Упрощенный бот для СДВГ
Четкое разделение задач по сервисам
"""

import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from config import TELEGRAM_BOT_TOKEN
from audio_processor_fixed import AudioProcessorFixed
from task_router import TaskRouter, TaskType

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SimpleTelegramBot:
    """Упрощенный бот для СДВГ"""
    
    def __init__(self):
        self.audio_processor = AudioProcessorFixed()
        self.task_router = TaskRouter()
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🤖 *Простой AI Ассистент для СДВГ*

*Я автоматически распределяю твои задачи:*

🔥 **СРОЧНЫЕ** → Apple Reminders (напоминание через 2 часа)
📅 **СОБЫТИЯ** → Apple Calendar (с временем)
🔄 **ПРИВЫЧКИ** → Apple Reminders (ежедневно)
📋 **ПРОЕКТЫ** → Notion (для детальной проработки)
✅ **РУТИНА** → Apple Reminders (на завтра)
💡 **ИДЕИ** → Notion (для сохранения)

*Просто отправь:*
• Текст или голосовое сообщение
• Любую задачу, мысль, идею
• Я сам определю, куда это отправить!

*Примеры:*
• "Срочно позвонить маме" → Apple Reminders
• "Встреча завтра в 15:00" → Apple Calendar  
• "Каждый день пить воду" → Apple Reminders (привычка)
• "Создать сайт" → Notion (проект)
• "Купить молоко" → Apple Reminders (рутина)

Готов помочь! 🚀
        """
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
📚 *Как это работает*

*🎯 Простота для СДВГ:*
• Один бот - все сервисы
• Автоматическое распределение
• Никаких сложных меню

*📱 Куда идут задачи:*

**Apple Reminders:**
• 🔥 Срочные (напоминание через 2 часа)
• 🔄 Привычки (ежедневно)
• ✅ Рутина (на завтра)

**Apple Calendar:**
• 📅 События с временем
• 📞 Встречи и звонки

**Notion:**
• 📋 Проекты (для детальной работы)
• 💡 Идеи (для сохранения)

*🎤 Поддерживает:*
• Голосовые сообщения
• Текстовые сообщения
• Автоматическое распознавание

*⚡ Ключевые слова:*
• "срочно", "сегодня" → Срочные
• "встреча", "время" → Календарь
• "каждый день" → Привычки
• "создать", "проект" → Notion
• "купить", "позвонить" → Рутина

Просто говори - я разберусь! 🎯
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
            
            # Update processing message
            await processing_msg.edit_text("🧠 Анализирую и распределяю задачу...")
            
            # Route the task
            user_id = update.effective_user.id
            result = await self.task_router.route_task(text, user_id)
            
            if result["success"]:
                # Show result
                service_emoji = {
                    "Apple Reminders": "📱",
                    "Apple Calendar": "📅", 
                    "Notion": "📋"
                }
                
                emoji = service_emoji.get(result["service"], "✅")
                message = f"{emoji} {result['message']}"
                
                await processing_msg.edit_text(message, parse_mode='Markdown')
            else:
                await processing_msg.edit_text(f"❌ {result['message']}")
                
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
            
            # Send processing message
            processing_msg = await update.message.reply_text("🧠 Анализирую и распределяю задачу...")
            
            # Route the task
            user_id = update.effective_user.id
            result = await self.task_router.route_task(text, user_id)
            
            if result["success"]:
                # Show result
                service_emoji = {
                    "Apple Reminders": "📱",
                    "Apple Calendar": "📅", 
                    "Notion": "📋"
                }
                
                emoji = service_emoji.get(result["service"], "✅")
                message = f"{emoji} {result['message']}"
                
                await processing_msg.edit_text(message, parse_mode='Markdown')
            else:
                await processing_msg.edit_text(f"❌ {result['message']}")
                
        except Exception as e:
            logger.error(f"Error handling text message: {e}")
            await update.message.reply_text("❌ Произошла ошибка при обработке сообщения.")
    
    async def test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test command to show task routing"""
        if not context.args:
            await update.message.reply_text(
                "🧪 *Тест маршрутизации*\n\n"
                "Использование: `/test <текст задачи>`\n\n"
                "Примеры:\n"
                "• `/test Срочно позвонить маме`\n"
                "• `/test Встреча завтра в 15:00`\n"
                "• `/test Каждый день пить воду`\n"
                "• `/test Создать сайт`\n"
                "• `/test Купить молоко`",
                parse_mode='Markdown'
            )
            return
        
        text = " ".join(context.args)
        user_id = update.effective_user.id
        
        # Route the task
        result = await self.task_router.route_task(text, user_id)
        
        if result["success"]:
            message = f"""
🧪 *Тест маршрутизации*

**Текст:** {text}
**Тип:** {result['task_type']}
**Сервис:** {result['service']}

{result['message']}
            """
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ {result['message']}")
    
    def run(self):
        """Run the bot"""
        # Create application
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("test", self.test_command))
        
        # Handle audio and voice messages
        application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, self.handle_audio_message))
        
        # Handle text messages
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        
        # Start the bot
        logger.info("Starting Simple Telegram Bot...")
        application.run_polling()

if __name__ == "__main__":
    bot = SimpleTelegramBot()
    bot.run()
