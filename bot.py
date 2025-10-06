import logging
import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

from config import TELEGRAM_BOT_TOKEN
from audio_processor import AudioProcessor
from ai_processor import AIProcessor
from mindmap_generator import MindmapGenerator
from planner_system import PersonalPlanner
from smart_agent import SmartAgent

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramAIAssistant:
    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.ai_processor = AIProcessor()
        self.mindmap_generator = MindmapGenerator()
        self.planner = PersonalPlanner()
        self.smart_agent = SmartAgent()
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🤖 *Добро пожаловать в Умный AI Ассистент!*

*Я автоматически анализирую твои сообщения и:*
🔥 **Срочные задачи** → добавляю в Notion на сегодня
📅 **Задачи на неделю** → планирую на неделю  
📚 **Долгосрочные планы** → сохраняю без срока
🗺️ **Дорожные карты** → создаю файлы с планами
🔗 **Цепочки задач** → разбиваю на этапы
💭 **Мысли и идеи** → структурирую и сохраняю

*Просто отправь мне:*
• Текст или голосовое сообщение
• Любые мысли, задачи, планы
• Я сам определю, что с этим делать!

*Или используй меню ниже для ручного управления* 🚀
        """
        
        # Create inline keyboard with main menu
        keyboard = [
            [InlineKeyboardButton("📅 Планнер", callback_data="menu_planner")],
            [InlineKeyboardButton("🗓️ Расписание", callback_data="menu_schedule")],
            [InlineKeyboardButton("📋 Мои задачи", callback_data="menu_tasks")],
            [InlineKeyboardButton("📚 Сортировка материалов", callback_data="menu_materials")],
            [InlineKeyboardButton("🔧 Статус системы", callback_data="menu_status")],
            [InlineKeyboardButton("❓ Помощь", callback_data="menu_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
📚 *Помощь по использованию бота*

*🤖 Умный агент автоматически:*
• 🔥 Срочные задачи → добавляет в Notion на сегодня
• 📅 Задачи на неделю → планирует на неделю  
• 📚 Долгосрочные планы → сохраняет без срока
• 🗺️ Дорожные карты → создает файлы с планами
• 🔗 Цепочки задач → разбивает на этапы
• 💭 Мысли и идеи → структурирует и сохраняет

*📋 Команды:*
• `/start` - главное меню
• `/help` - эта справка
• `/tasks` - показать задачи из Notion
• `/expand <задача>` - развернуть задачу в детальный план
• `/schedule` - ежедневное расписание
• `/status` - статус системы

*🎤 Поддерживаемые форматы аудио:*
• OGG (голосовые сообщения Telegram)
• MP3, WAV, M4A

*⚡ Просто отправь:*
• Текст или голосовое сообщение
• Любые мысли, задачи, планы
• Я сам определю, что с этим делать!

Готов к работе! 🎯
        """
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        status_message = """
🔧 *Статус системы*

✅ Telegram Bot: Активен
✅ Audio Processor: Готов
✅ OpenAI Integration: Готов
✅ Mindmap Generator: Готов
✅ Personal Planner: Готов
✅ Notion Integration: Готов

*Конфигурация:*
• Модель OpenAI: GPT-3.5-turbo
• Максимальная длительность аудио: 5 минут
• Поддерживаемые форматы: OGG, MP3, WAV, M4A
• Notion API: Интегрирован

Система готова к работе! 🚀
        """
        await update.message.reply_text(status_message, parse_mode='Markdown')
    
    async def planner_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /planner command"""
        planner_message = """
📅 *Персональный Планнер*

*Доступные функции:*
• 📋 Создание планов задач
• 🗓️ Ежедневное планирование
• 📚 Сортировка материалов
• ⚡ Приоритизация задач
• 🔗 Интеграция с Notion

*Команды:*
/planner - показать это меню
/schedule - создать расписание на день
/tasks - показать приоритетные задачи
/materials - отсортировать материал

*Как использовать:*
1. Отправь текст или аудио
2. Выбери "📅 Создать план в Notion"
3. Получи структурированный план в Notion

Готов помочь с планированием! 📊
        """
        await update.message.reply_text(planner_message, parse_mode='Markdown')
    
    async def schedule_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /schedule command"""
        try:
            await update.message.reply_text("🗓️ Создаю расписание на день...")
            
            # Create daily schedule
            schedule_result = await self.planner.create_daily_schedule()
            
            if schedule_result.get("success"):
                message = f"✅ *Расписание создано!*\n\n"
                message += f"📅 *Дата:* {schedule_result.get('date', '')}\n"
                message += f"📋 *Всего задач:* {schedule_result.get('total_tasks', 0)}\n\n"
                
                time_blocks = schedule_result.get("time_blocks", [])
                for block in time_blocks:
                    message += f"⏰ *{block.get('time', '')}*\n"
                    message += f"   {block.get('title', '')}\n"
                    message += f"   Задач: {len(block.get('tasks', []))}\n\n"
                
                message += f"🔗 *Проверь Notion для детального расписания!*"
                
                await update.message.reply_text(message, parse_mode='Markdown')
            else:
                await update.message.reply_text(f"❌ Ошибка создания расписания: {schedule_result.get('error', '')}")
                
        except Exception as e:
            logger.error(f"Error creating schedule: {e}")
            await update.message.reply_text("❌ Ошибка при создании расписания.")
    
    async def tasks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /tasks command"""
        try:
            await update.message.reply_text("📋 Получаю приоритетные задачи...")
            
            # Get priority tasks
            tasks = await self.planner.get_priority_tasks(limit=10)
            
            if tasks:
                message = "📋 *Приоритетные задачи:*\n\n"
                for i, task in enumerate(tasks, 1):
                    priority_emoji = {"🔴 High": "🔴", "🟡 Medium": "🟡", "🟢 Low": "🟢"}.get(task.get("priority", "🟡 Medium"), "🟡")
                    message += f"{priority_emoji} *{i}. {task.get('title', '')}*\n"
                    message += f"   📂 {task.get('category', '')}\n"
                    message += f"   ⏱️ {task.get('estimated_time', '')}\n"
                    if task.get('due_date'):
                        message += f"   📅 {task.get('due_date')}\n"
                    message += "\n"
                
                await update.message.reply_text(message, parse_mode='Markdown')
            else:
                await update.message.reply_text("📋 Нет активных задач. Создай новый план!")
                
        except Exception as e:
            logger.error(f"Error getting tasks: {e}")
            await update.message.reply_text("❌ Ошибка при получении задач.")

    async def expand_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /expand command for detailed task planning"""
        try:
            # Get the task description from command arguments
            if not context.args:
                await update.message.reply_text(
                    "📋 *Расширение задачи в детальный план*\n\n"
                    "Использование: `/expand <описание задачи>`\n\n"
                    "Пример: `/expand Создать мобильное приложение`\n\n"
                    "Я разверну твою задачу в детальный план с:\n"
                    "• Целью и стратегией\n"
                    "• Этапами и подзадачами\n"
                    "• Временными рамками\n"
                    "• Ресурсами и рисками\n"
                    "• Критериями успеха",
                    parse_mode='Markdown'
                )
                return
            
            task_description = " ".join(context.args)
            
            # Use smart agent to expand the task
            result = await self.smart_agent.analyze_and_process(f"разверни детально: {task_description}", update.effective_user.id)
            
            if result["success"]:
                await update.message.reply_text(result["message"], parse_mode='Markdown')
                
                # If there's detailed plan data, show it
                if result.get("result", {}).get("plan_data"):
                    plan_data = result["result"]["plan_data"]
                    plan_message = f"""
📋 **Детальный план создан:**

**🎯 Цель:** {plan_data.get('goal', 'Не указана')}

**📈 Стратегия:** {plan_data.get('strategy', 'Не указана')}

**📊 Этапы:** {len(plan_data.get('phases', []))} этапов
**✅ Подзадачи:** {result['result'].get('tasks_created', 0)} задач создано

**📚 Ресурсы:** {', '.join(plan_data.get('resources', [])[:3])}{'...' if len(plan_data.get('resources', [])) > 3 else ''}

**⚠️ Риски:** {len(plan_data.get('risks', []))} выявлено
**🎯 Критерии успеха:** {len(plan_data.get('success_criteria', []))} определено

Все подзадачи добавлены в Notion, план сохранен как материал!
                    """
                    await update.message.reply_text(plan_message, parse_mode='Markdown')
            else:
                await update.message.reply_text(f"❌ {result.get('message', 'Ошибка при создании детального плана')}")
                
        except Exception as e:
            logger.error(f"Error in expand command: {e}")
            await update.message.reply_text("❌ Ошибка при расширении задачи в детальный план.")
    
    async def handle_audio_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming audio/voice messages with smart agent"""
        try:
            # Send processing message
            processing_msg = await update.message.reply_text("🔄 Обрабатываю аудиосообщение...")
            
            # Extract text from audio
            text = await self.audio_processor.process_audio_message(update, context)
            
            if not text:
                await processing_msg.edit_text("❌ Не удалось извлечь текст из аудио. Попробуй еще раз с более четкой речью.")
                return
            
            # Check if text is an error message
            if text.startswith("Аудио слишком длинное") or text.startswith("Файл слишком большой") or text.startswith("Неподдерживаемый формат") or text.startswith("Ошибка распознавания"):
                await processing_msg.edit_text(f"❌ {text}")
                return
            
            # Update processing message
            await processing_msg.edit_text("🧠 Анализирую твое сообщение...")
            
            # Use smart agent to analyze and process
            user_id = update.effective_user.id
            result = await self.smart_agent.analyze_and_process(text, user_id)
            
            if result["success"]:
                # Send the response message
                await processing_msg.edit_text(result["message"], parse_mode='Markdown')
                
                # If roadmap was created, send the file
                if result["type"] == "roadmap" and result["result"].get("file_path"):
                    file_path = result["result"]["file_path"]
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as doc:
                            await update.message.reply_document(
                                doc, 
                                caption="🗺️ *Дорожная карта*",
                                parse_mode='Markdown'
                            )
                        # Clean up file
                        os.remove(file_path)
                
                # If thoughts were structured, show the structure
                elif result["type"] == "thoughts" and result["result"].get("structure"):
                    structure = result["result"]["structure"]
                    await self._send_task_structure(update, structure)
                    
            else:
                await processing_msg.edit_text(f"❌ {result['message']}")
            
        except Exception as e:
            logger.error(f"Error handling audio message: {e}")
            await update.message.reply_text("❌ Произошла ошибка при обработке. Попробуй еще раз.")
    
    async def _send_results(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                          text: str, task_structure: dict, mindmap_data: dict, summary: str):
        """Send all results to user"""
        try:
            # Send extracted text
            await update.message.reply_text(f"📝 *Извлеченный текст:*\n\n{text}", parse_mode='Markdown')
            
            # Send summary
            await update.message.reply_text(f"📋 *Краткое резюме:*\n\n{summary}", parse_mode='Markdown')
            
            # Send task structure
            await self._send_task_structure(update, task_structure)
            
            # Generate and send mindmap
            await self._send_mindmap(update, context, mindmap_data)
            
        except Exception as e:
            logger.error(f"Error sending results: {e}")
            await update.message.reply_text("❌ Ошибка при отправке результатов.")
    
    async def _send_task_structure(self, update: Update, task_structure: dict):
        """Send task structure as formatted message"""
        try:
            message = f"📋 *СТРУКТУРИРОВАННЫЙ ПЛАН ЗАДАЧ*\n\n"
            message += f"🎯 *Основная цель:* {task_structure.get('main_goal', 'Не указана')}\n\n"
            
            tasks = task_structure.get('tasks', [])
            for i, task in enumerate(tasks, 1):
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.get('priority', 'medium'), "🟡")
                message += f"{priority_emoji} *{i}. {task.get('title', f'Задача {i}')}*\n"
                message += f"   📝 {task.get('description', 'Описание отсутствует')}\n"
                message += f"   ⏱️ Время: {task.get('estimated_time', 'Не указано')}\n"
                message += f"   📂 Категория: {task.get('category', 'Общее')}\n\n"
            
            categories = task_structure.get('categories', [])
            if categories:
                message += f"📂 *Категории:* {', '.join(categories)}\n"
            
            timeline = task_structure.get('timeline', '')
            if timeline:
                message += f"⏰ *Общее время:* {timeline}\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error sending task structure: {e}")
    
    async def _send_mindmap(self, update: Update, context: ContextTypes.DEFAULT_TYPE, mindmap_data: dict):
        """Generate and send mindmap"""
        try:
            # Generate mindmap image
            image_path = self.mindmap_generator.generate_mindmap_image(mindmap_data)
            
            if image_path and os.path.exists(image_path):
                # Send text file as document
                with open(image_path, 'rb') as doc:
                    await update.message.reply_document(doc, caption="🗺️ *Майндмэп (текстовый файл)*", parse_mode='Markdown')
                
                # Clean up file
                os.remove(image_path)
            else:
                # Send text mindmap as fallback
                text_mindmap = self.mindmap_generator.generate_mindmap_text(mindmap_data)
                await update.message.reply_text(text_mindmap, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"Error sending mindmap: {e}")
            # Send text mindmap as fallback
            text_mindmap = self.mindmap_generator.generate_mindmap_text(mindmap_data)
            await update.message.reply_text(text_mindmap, parse_mode='Markdown')
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages with smart agent"""
        text = update.message.text
        
        if text.startswith('/'):
            return  # Commands are handled separately
        
        # Store the text in context for callback processing
        context.user_data['last_text'] = text
        
        # Show processing message
        processing_msg = await update.message.reply_text("🧠 Анализирую твое сообщение...")
        
        try:
            # Use smart agent to analyze and process
            user_id = update.effective_user.id
            result = await self.smart_agent.analyze_and_process(text, user_id)
            
            if result["success"]:
                # Send the response message
                await processing_msg.edit_text(result["message"], parse_mode='Markdown')
                
                # If roadmap was created, send the file
                if result["type"] == "roadmap" and result["result"].get("file_path"):
                    file_path = result["result"]["file_path"]
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as doc:
                            await update.message.reply_document(
                                doc, 
                                caption="🗺️ *Дорожная карта*",
                                parse_mode='Markdown'
                            )
                        # Clean up file
                        os.remove(file_path)
                
                # If thoughts were structured, show the structure
                elif result["type"] == "thoughts" and result["result"].get("structure"):
                    structure = result["result"]["structure"]
                    await self._send_task_structure(update, structure)
                    
            else:
                await processing_msg.edit_text(f"❌ {result['message']}")
                
        except Exception as e:
            logger.error(f"Error in smart agent processing: {e}")
            await processing_msg.edit_text("❌ Произошла ошибка при обработке. Попробуй еще раз.")
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        try:
            # Handle main menu callbacks
            if query.data == "menu_planner":
                await self._show_planner_menu(query, context)
            elif query.data == "menu_schedule":
                await self._handle_schedule_menu(query, context)
            elif query.data == "menu_tasks":
                await self._handle_tasks_menu(query, context)
            elif query.data == "menu_materials":
                await self._show_materials_menu(query, context)
            elif query.data == "menu_status":
                await self._show_status_menu(query, context)
            elif query.data == "menu_help":
                await self._show_help_menu(query, context)
            elif query.data == "back_to_main":
                await self._show_main_menu(query, context)
            
            # Handle text processing callbacks
            elif query.data in ["process_text", "mindmap_text", "create_plan", "sort_material"]:
                # Get the stored text from user data
                text = context.user_data.get('last_text')
                if not text:
                    await query.edit_message_text("❌ Не удалось найти исходный текст.")
                    return
                
                if query.data == "process_text":
                    # Show processing message
                    await query.edit_message_text("🤖 Создаю план задач...")
                    
                    # Process the text
                    await self._process_text_direct(query, context, text)
                    
                elif query.data == "mindmap_text":
                    # Show processing message
                    await query.edit_message_text("🗺️ Создаю майндмэп...")
                    
                    # Process only mindmap
                    await self._process_mindmap_direct(query, context, text)
                    
                elif query.data == "create_plan":
                    # Show processing message
                    await query.edit_message_text("📅 Создаю план в Notion...")
                    
                    # Create smart plan with Notion integration
                    await self._create_notion_plan(query, context, text)
                    
                elif query.data == "sort_material":
                    # Show processing message
                    await query.edit_message_text("📚 Сортирую материал...")
                    
                    # Sort material
                    await self._sort_material_direct(query, context, text)
                
        except Exception as e:
            logger.error(f"Error handling callback: {e}")
            await query.edit_message_text("❌ Ошибка при обработке запроса.")
    
    async def _process_text_message(self, message, context: ContextTypes.DEFAULT_TYPE):
        """Process text message similar to audio"""
        try:
            text = message.text
            
            # Generate task structure
            task_structure = await self.ai_processor.generate_task_structure(text)
            
            # Generate mindmap
            mindmap_data = await self.ai_processor.generate_mindmap_data(text)
            
            # Generate summary
            summary = await self.ai_processor.generate_summary(text)
            
            # Send results
            await self._send_results(message, context, text, task_structure, mindmap_data, summary)
            
        except Exception as e:
            logger.error(f"Error processing text message: {e}")
    
    async def _process_mindmap_only(self, message, context: ContextTypes.DEFAULT_TYPE):
        """Process text message for mindmap only"""
        try:
            text = message.text
            
            # Generate mindmap
            mindmap_data = await self.ai_processor.generate_mindmap_data(text)
            
            # Send only mindmap
            await self._send_mindmap(message, context, mindmap_data)
            
        except Exception as e:
            logger.error(f"Error processing mindmap: {e}")
            await message.reply_text("❌ Ошибка при создании майндмэпа.")
    
    async def _process_text_direct(self, query, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Process text directly from callback"""
        try:
            # Generate task structure
            task_structure = await self.ai_processor.generate_task_structure(text)
            
            # Generate mindmap
            mindmap_data = await self.ai_processor.generate_mindmap_data(text)
            
            # Generate summary
            summary = await self.ai_processor.generate_summary(text)
            
            # Send results
            await self._send_results_direct(query, context, text, task_structure, mindmap_data, summary)
            
        except Exception as e:
            logger.error(f"Error processing text: {e}")
            await query.edit_message_text("❌ Ошибка при создании плана задач.")
    
    async def _process_mindmap_direct(self, query, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Process text for mindmap only from callback"""
        try:
            # Generate mindmap
            mindmap_data = await self.ai_processor.generate_mindmap_data(text)
            
            # Send only mindmap
            await self._send_mindmap_direct(query, context, mindmap_data)
            
        except Exception as e:
            logger.error(f"Error processing mindmap: {e}")
            await query.edit_message_text("❌ Ошибка при создании майндмэпа.")
    
    async def _send_results_direct(self, query, context: ContextTypes.DEFAULT_TYPE, 
                                  text: str, task_structure: dict, mindmap_data: dict, summary: str):
        """Send all results to user from callback"""
        try:
            # Send extracted text
            await context.bot.send_message(
                chat_id=query.from_user.id,
                text=f"📝 *Исходный текст:*\n\n{text}",
                parse_mode='Markdown'
            )
            
            # Send summary
            await context.bot.send_message(
                chat_id=query.from_user.id,
                text=f"📋 *Краткое резюме:*\n\n{summary}",
                parse_mode='Markdown'
            )
            
            # Send task structure
            await self._send_task_structure_direct(query, context, task_structure)
            
            # Generate and send mindmap
            await self._send_mindmap_direct(query, context, mindmap_data)
            
        except Exception as e:
            logger.error(f"Error sending results: {e}")
            await query.edit_message_text("❌ Ошибка при отправке результатов.")
    
    async def _send_task_structure_direct(self, query, context: ContextTypes.DEFAULT_TYPE, task_structure: dict):
        """Send task structure as formatted message from callback"""
        try:
            message = f"📋 *СТРУКТУРИРОВАННЫЙ ПЛАН ЗАДАЧ*\n\n"
            message += f"🎯 *Основная цель:* {task_structure.get('main_goal', 'Не указана')}\n\n"
            
            tasks = task_structure.get('tasks', [])
            for i, task in enumerate(tasks, 1):
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.get('priority', 'medium'), "🟡")
                message += f"{priority_emoji} *{i}. {task.get('title', f'Задача {i}')}*\n"
                message += f"   📝 {task.get('description', 'Описание отсутствует')}\n"
                message += f"   ⏱️ Время: {task.get('estimated_time', 'Не указано')}\n"
                message += f"   📂 Категория: {task.get('category', 'Общее')}\n\n"
            
            categories = task_structure.get('categories', [])
            if categories:
                message += f"📂 *Категории:* {', '.join(categories)}\n"
            
            timeline = task_structure.get('timeline', '')
            if timeline:
                message += f"⏰ *Общее время:* {timeline}\n"
            
            await context.bot.send_message(
                chat_id=query.from_user.id,
                text=message,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error sending task structure: {e}")
    
    async def _send_mindmap_direct(self, query, context: ContextTypes.DEFAULT_TYPE, mindmap_data: dict):
        """Generate and send mindmap from callback"""
        try:
            # Generate mindmap image
            image_path = self.mindmap_generator.generate_mindmap_image(mindmap_data)
            
            if image_path and os.path.exists(image_path):
                # Send text file as document
                with open(image_path, 'rb') as doc:
                    await context.bot.send_document(
                        chat_id=query.from_user.id,
                        document=doc,
                        caption="🗺️ *Майндмэп (текстовый файл)*",
                        parse_mode='Markdown'
                    )
                
                # Clean up file
                os.remove(image_path)
            else:
                # Send text mindmap as fallback
                text_mindmap = self.mindmap_generator.generate_mindmap_text(mindmap_data)
                await context.bot.send_message(
                    chat_id=query.from_user.id,
                    text=text_mindmap,
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"Error sending mindmap: {e}")
            # Send text mindmap as fallback
            text_mindmap = self.mindmap_generator.generate_mindmap_text(mindmap_data)
            await context.bot.send_message(
                chat_id=query.from_user.id,
                text=text_mindmap,
                parse_mode='Markdown'
            )
    
    async def _create_notion_plan(self, query, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Create smart plan with Notion integration"""
        try:
            # Create smart plan
            plan_result = await self.planner.create_smart_plan(text)
            
            if plan_result.get("success"):
                # Send success message
                message = f"✅ *План создан в Notion!*\n\n"
                message += f"🎯 *Цель:* {plan_result.get('main_goal', '')}\n"
                message += f"📋 *Задач создано:* {plan_result.get('tasks_created', 0)}\n"
                message += f"📂 *Категории:* {', '.join(plan_result.get('categories', []))}\n"
                message += f"⏰ *Временные рамки:* {plan_result.get('timeline', '')}\n\n"
                message += f"🔗 *Проверь свой Notion для просмотра задач!*"
                
                await context.bot.send_message(
                    chat_id=query.from_user.id,
                    text=message,
                    parse_mode='Markdown'
                )
                
                # Send task details
                tasks = plan_result.get("tasks", [])
                if tasks:
                    task_message = "📋 *Созданные задачи:*\n\n"
                    for i, task in enumerate(tasks[:5], 1):  # Show first 5 tasks
                        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.get("priority", "medium"), "🟡")
                        task_message += f"{priority_emoji} *{i}. {task.get('title', '')}*\n"
                        task_message += f"   ⏱️ {task.get('estimated_time', '')}\n"
                        task_message += f"   📂 {task.get('category', '')}\n\n"
                    
                    await context.bot.send_message(
                        chat_id=query.from_user.id,
                        text=task_message,
                        parse_mode='Markdown'
                    )
            else:
                await query.edit_message_text(f"❌ Ошибка создания плана: {plan_result.get('error', 'Неизвестная ошибка')}")
                
        except Exception as e:
            logger.error(f"Error creating Notion plan: {e}")
            await query.edit_message_text("❌ Ошибка при создании плана в Notion.")
    
    async def _sort_material_direct(self, query, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Sort material using AI and Notion"""
        try:
            # Sort material
            sort_result = await self.planner.sort_material(text)
            
            if sort_result.get("success"):
                message = f"✅ *Материал отсортирован!*\n\n"
                message += f"📂 *Категория:* {sort_result.get('category', '')}\n"
                message += f"🏷️ *Теги:* {', '.join(sort_result.get('tags', []))}\n"
                message += f"⚡ *Приоритет:* {sort_result.get('priority', 'medium')}\n\n"
                message += f"📝 *Анализ:*\n{sort_result.get('analysis', '')}\n\n"
                message += f"🔗 *Материал сохранен в Notion!*"
                
                await context.bot.send_message(
                    chat_id=query.from_user.id,
                    text=message,
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text(f"❌ Ошибка сортировки: {sort_result.get('error', 'Неизвестная ошибка')}")
                
        except Exception as e:
            logger.error(f"Error sorting material: {e}")
            await query.edit_message_text("❌ Ошибка при сортировке материала.")
    
    async def _show_main_menu(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Show main menu"""
        welcome_message = """
🤖 *AI Ассистент - Главное меню*

Выбери действие:
        """
        
        keyboard = [
            [InlineKeyboardButton("📅 Планнер", callback_data="menu_planner")],
            [InlineKeyboardButton("🗓️ Расписание", callback_data="menu_schedule")],
            [InlineKeyboardButton("📋 Мои задачи", callback_data="menu_tasks")],
            [InlineKeyboardButton("📚 Сортировка материалов", callback_data="menu_materials")],
            [InlineKeyboardButton("🔧 Статус системы", callback_data="menu_status")],
            [InlineKeyboardButton("❓ Помощь", callback_data="menu_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(welcome_message, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_planner_menu(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Show planner menu"""
        planner_message = """
📅 *Персональный Планнер*

*Доступные функции:*
• 🗓️ Ежедневное планирование  
• 📋 Просмотр задач
• ⚡ Приоритизация задач
• 🔗 Интеграция с Notion

*Как использовать:*
1. Отправь текст или аудио боту
2. Умный агент автоматически определит тип
3. Получи структурированный план в Notion

Готов помочь с планированием! 📊
        """
        
        keyboard = [
            [InlineKeyboardButton("🗓️ Ежедневное расписание", callback_data="menu_schedule")],
            [InlineKeyboardButton("📋 Мои задачи", callback_data="menu_tasks")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(planner_message, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _handle_schedule_menu(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Handle schedule menu"""
        await query.edit_message_text("🗓️ Создаю расписание на день...")
        
        try:
            # Create daily schedule
            schedule_result = await self.planner.create_daily_schedule()
            
            if schedule_result.get("success"):
                message = f"✅ *Расписание создано!*\n\n"
                message += f"📅 *Дата:* {schedule_result.get('date', '')}\n"
                message += f"📋 *Всего задач:* {schedule_result.get('total_tasks', 0)}\n\n"
                
                time_blocks = schedule_result.get("time_blocks", [])
                for block in time_blocks:
                    message += f"⏰ *{block.get('time', '')}*\n"
                    message += f"   {block.get('title', '')}\n"
                    message += f"   Задач: {len(block.get('tasks', []))}\n\n"
                
                message += f"🔗 *Проверь Notion для детального расписания!*"
                
                keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            else:
                await query.edit_message_text(f"❌ Ошибка создания расписания: {schedule_result.get('error', '')}")
                
        except Exception as e:
            logger.error(f"Error creating schedule: {e}")
            await query.edit_message_text("❌ Ошибка при создании расписания.")
    
    async def _handle_tasks_menu(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Handle tasks menu"""
        await query.edit_message_text("📋 Получаю приоритетные задачи...")
        
        try:
            # Get priority tasks
            tasks = await self.planner.get_priority_tasks(limit=10)
            
            if tasks:
                message = "📋 *Приоритетные задачи:*\n\n"
                for i, task in enumerate(tasks, 1):
                    priority_emoji = {"🔴 High": "🔴", "🟡 Medium": "🟡", "🟢 Low": "🟢"}.get(task.get("priority", "🟡 Medium"), "🟡")
                    message += f"{priority_emoji} *{i}. {task.get('title', '')}*\n"
                    message += f"   📂 {task.get('category', '')}\n"
                    message += f"   ⏱️ {task.get('estimated_time', '')}\n"
                    if task.get('due_date'):
                        message += f"   📅 {task.get('due_date')}\n"
                    message += "\n"
                
                keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            else:
                await query.edit_message_text("📋 Нет активных задач. Создай новый план!")
                
        except Exception as e:
            logger.error(f"Error getting tasks: {e}")
            await query.edit_message_text("❌ Ошибка при получении задач.")
    
    async def _show_materials_menu(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Show materials menu"""
        materials_message = """
📚 *Сортировка материалов*

*Что я умею:*
• 📝 Анализировать тексты
• 🏷️ Автоматически добавлять теги
• 📂 Категоризировать по типам
• ⚡ Определять приоритет
• 🔗 Сохранять в Notion

*Как использовать:*
1. Отправь любой текст боту
2. Умный агент автоматически проанализирует
3. Получи анализ и категоризацию

Готов анализировать материалы! 🧠
        """
        
        keyboard = [
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(materials_message, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_status_menu(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Show status menu"""
        status_message = """
🔧 *Статус системы*

✅ Telegram Bot: Активен
✅ Audio Processor: Готов
✅ OpenAI Integration: Готов
✅ Mindmap Generator: Готов
✅ Personal Planner: Готов
✅ Notion Integration: Готов

*Конфигурация:*
• Модель OpenAI: GPT-3.5-turbo
• Максимальная длительность аудио: 5 минут
• Поддерживаемые форматы: OGG, MP3, WAV, M4A
• Notion API: Интегрирован

Система готова к работе! 🚀
        """
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(status_message, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_help_menu(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Show help menu"""
        help_message = """
📚 *Помощь по использованию бота*

*Поддерживаемые форматы аудио:*
• OGG (голосовые сообщения Telegram)
• MP3, WAV, M4A

*Ограничения:*
• Максимальная длительность: 5 минут
• Язык распознавания: русский

*Что я делаю:*
1. 🎤 Получаю твое аудиосообщение
2. 🔄 Конвертирую в нужный формат
3. 📝 Извлекаю текст с помощью Google Speech Recognition
4. 🤖 Отправляю текст в OpenAI для анализа
5. 📋 Создаю структурированный план задач
6. 🗺️ Генерирую майндмэп
7. 📤 Отправляю результат в чат

*Если что-то не работает:*
• Проверь качество аудио
• Убедись, что говоришь четко
• Попробуй сократить сообщение

Готов к работе! 🎯
        """
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(help_message, parse_mode='Markdown', reply_markup=reply_markup)
    
    def run(self):
        """Start the bot"""
        if not TELEGRAM_BOT_TOKEN:
            logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
            return
        
        # Create application
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("planner", self.planner_command))
        application.add_handler(CommandHandler("schedule", self.schedule_command))
        application.add_handler(CommandHandler("tasks", self.tasks_command))
        application.add_handler(CommandHandler("expand", self.expand_command))
        
        # Handle audio and voice messages
        application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, self.handle_audio_message))
        
        # Handle text messages
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        
        # Handle callback queries
        application.add_handler(CallbackQueryHandler(self.handle_callback_query))
        
        # Start the bot
        logger.info("Starting Telegram AI Assistant...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    import os
    bot = TelegramAIAssistant()
    bot.run()
