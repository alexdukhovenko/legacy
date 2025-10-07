#!/usr/bin/env python3
"""
Тест для проверки API ключей
"""

import os
import openai
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv('config.production.env')

def test_openai_api():
    """Тестирует OpenAI API"""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ OPENAI_API_KEY не найден")
        return False
    
    print(f"🔑 API ключ найден: {api_key[:10]}...{api_key[-10:]}")
    
    try:
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Привет! Это тест API."}
            ],
            max_tokens=50
        )
        
        print("✅ OpenAI API работает!")
        print(f"Ответ: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка OpenAI API: {e}")
        return False

if __name__ == "__main__":
    test_openai_api()
