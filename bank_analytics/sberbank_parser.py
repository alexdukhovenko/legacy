#!/usr/bin/env python3
"""
Специальный парсер для выписок Сбербанка
"""

import csv
import re
from datetime import datetime
from typing import List, Dict

def parse_sberbank_statement(file_path: str) -> List[Dict]:
    """Парсит выписку Сбербанка и возвращает список транзакций"""
    transactions = []
    
    try:
        # Пробуем разные кодировки
        encodings = ['cp1251', 'utf-8', 'windows-1251']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    content = file.read()
                    break
            except UnicodeDecodeError:
                continue
        else:
            print("Не удалось определить кодировку файла")
            return []
        
        # Разбиваем на строки
        lines = content.split('\n')
        
        # Ищем заголовки
        header_line = None
        for i, line in enumerate(lines):
            if 'statement_unid' in line or 'ID-записи' in line:
                header_line = i
                break
        
        if header_line is None:
            print("Не найден заголовок файла")
            return []
        
        # Парсим заголовки
        headers = lines[header_line].split('\t')
        
        # Ищем нужные колонки
        date_col = None
        amount_col = None
        description_col = None
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            if 'date_oper' in header_lower or 'дата_опер' in header_lower:
                date_col = i
            elif 'sum_rur' in header_lower or 'сум_руб' in header_lower:
                amount_col = i
            elif 'text70' in header_lower or 'назначение' in header_lower:
                description_col = i
        
        if not all([date_col, amount_col, description_col]):
            print(f"Не найдены нужные колонки. Найдены: дата={date_col}, сумма={amount_col}, описание={description_col}")
            return []
        
        # Парсим транзакции
        for line_num in range(header_line + 1, len(lines)):
            line = lines[line_num].strip()
            if not line or line.startswith('ID-записи'):
                continue
            
            # Разбиваем строку по табуляции
            values = line.split('\t')
            
            if len(values) <= max(date_col, amount_col, description_col):
                continue
            
            try:
                # Извлекаем данные
                date_str = values[date_col].strip()
                amount_str = values[amount_col].strip()
                description = values[description_col].strip()
                
                # Парсим дату
                try:
                    date = datetime.strptime(date_str, '%d.%m.%Y')
                except:
                    try:
                        date = datetime.strptime(date_str, '%Y-%m-%d')
                    except:
                        continue
                
                # Парсим сумму
                amount_str = amount_str.replace(',', '.').replace(' ', '')
                try:
                    amount = float(amount_str)
                except:
                    continue
                
                # Пропускаем нулевые суммы
                if amount == 0:
                    continue
                
                # Создаем транзакцию
                transaction = {
                    'date': date.strftime('%Y-%m-%d'),
                    'description': description,
                    'amount': amount,
                    'category': categorize_transaction(description),
                    'bank': 'Сбербанк',
                    'transaction_type': 'income' if amount > 0 else 'expense'
                }
                
                transactions.append(transaction)
                
            except Exception as e:
                print(f"Ошибка обработки строки {line_num}: {e}")
                continue
        
        print(f"Обработано {len(transactions)} транзакций")
        return transactions
        
    except Exception as e:
        print(f"Ошибка чтения файла: {e}")
        return []

def categorize_transaction(description: str) -> str:
    """Категоризирует транзакцию по описанию"""
    description_lower = description.lower()
    
    category_rules = {
        "Продукты": ["магнит", "пятерочка", "перекресток", "ашан", "лента", "продукты", "еда", "кафе", "ресторан", "яндекс.еда"],
        "Транспорт": ["яндекс.такси", "uber", "метро", "автобус", "бензин", "заправка", "парковка", "транспорт", "яндекс.го"],
        "Коммунальные": ["жкх", "электричество", "газ", "вода", "отопление", "коммунальные", "квартплата"],
        "Связь": ["мтс", "билайн", "мегафон", "теле2", "интернет", "связь", "мобильная связь"],
        "Здоровье": ["аптека", "больница", "поликлиника", "врач", "лекарства", "медицина"],
        "Образование": ["школа", "университет", "курсы", "обучение", "образование"],
        "Развлечения": ["кино", "театр", "концерт", "игры", "развлечения", "отдых", "netflix", "spotify"],
        "Одежда": ["одежда", "обувь", "магазин одежды", "h&m", "zara", "uniqlo"],
        "Доходы": ["зарплата", "доход", "перевод", "возврат", "проценты", "дивиденды", "пенсия"],
        "Инвестиции": ["акции", "облигации", "депозит", "инвестиции", "брокер"],
        "Прочее": []
    }
    
    for category, keywords in category_rules.items():
        if any(keyword in description_lower for keyword in keywords):
            return category
    
    return "Прочее"

def export_to_csv(transactions: List[Dict], filename: str = "sberbank_transactions.csv"):
    """Экспортирует транзакции в CSV"""
    if not transactions:
        print("Нет данных для экспорта")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['date', 'description', 'amount', 'category', 'bank', 'transaction_type'])
        writer.writeheader()
        writer.writerows(transactions)
    
    print(f"Экспортировано {len(transactions)} транзакций в файл {filename}")

def main():
    """Основная функция"""
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input("Введите путь к файлу выписки: ")
    
    print(f"Обрабатываю файл: {file_path}")
    transactions = parse_sberbank_statement(file_path)
    
    if transactions:
        # Выводим статистику
        total_income = sum(t['amount'] for t in transactions if t['amount'] > 0)
        total_expense = abs(sum(t['amount'] for t in transactions if t['amount'] < 0))
        balance = total_income - total_expense
        
        print(f"\n=== СТАТИСТИКА ===")
        print(f"Доходы: {total_income:,.2f} руб.")
        print(f"Расходы: {total_expense:,.2f} руб.")
        print(f"Баланс: {balance:,.2f} руб.")
        print(f"Транзакций: {len(transactions)}")
        
        # Анализ по категориям
        categories = {}
        for t in transactions:
            if t['amount'] < 0:  # Только расходы
                cat = t['category']
                categories[cat] = categories.get(cat, 0) + abs(t['amount'])
        
        print(f"\n=== РАСХОДЫ ПО КАТЕГОРИЯМ ===")
        for cat, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"{cat}: {amount:,.2f} руб.")
        
        # Экспорт
        export_to_csv(transactions)
    else:
        print("Не удалось обработать файл")

if __name__ == "__main__":
    main()
