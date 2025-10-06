#!/usr/bin/env python3
"""
Упрощенная версия системы анализа банковских выписок
Работает без внешних зависимостей (только стандартная библиотека Python)
"""

import csv
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class Transaction:
    """Структура транзакции"""
    date: str
    description: str
    amount: float
    category: str = "Неопределено"
    bank: str = ""
    transaction_type: str = ""

class SimpleBankAnalytics:
    """Упрощенная система анализа банковских выписок"""
    
    def __init__(self):
        self.transactions = []
        self.category_rules = {
            "Продукты": ["магнит", "пятерочка", "перекресток", "ашан", "лента", "продукты", "еда", "кафе", "ресторан"],
            "Транспорт": ["яндекс.такси", "uber", "метро", "автобус", "бензин", "заправка", "парковка", "транспорт"],
            "Коммунальные": ["жкх", "электричество", "газ", "вода", "отопление", "коммунальные", "квартплата"],
            "Связь": ["мтс", "билайн", "мегафон", "теле2", "интернет", "связь", "мобильная связь"],
            "Здоровье": ["аптека", "больница", "поликлиника", "врач", "лекарства", "медицина"],
            "Образование": ["школа", "университет", "курсы", "обучение", "образование"],
            "Развлечения": ["кино", "театр", "концерт", "игры", "развлечения", "отдых"],
            "Одежда": ["одежда", "обувь", "магазин одежды", "h&m", "zara", "uniqlo"],
            "Доходы": ["зарплата", "доход", "перевод", "возврат", "проценты", "дивиденды"],
            "Инвестиции": ["акции", "облигации", "депозит", "инвестиции", "брокер"],
            "Прочее": []
        }
    
    def load_csv(self, file_path: str, bank_name: str = "") -> List[Transaction]:
        """Загружает транзакции из CSV файла"""
        transactions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Пробуем разные кодировки
                try:
                    reader = csv.DictReader(file)
                except UnicodeDecodeError:
                    file.close()
                    with open(file_path, 'r', encoding='cp1251') as file:
                        reader = csv.DictReader(file)
                
                for row in reader:
                    try:
                        # Ищем колонки с датой, суммой и описанием
                        date_col = self._find_date_column(row)
                        amount_col = self._find_amount_column(row)
                        desc_col = self._find_description_column(row)
                        
                        if date_col and amount_col and desc_col:
                            date_str = row[date_col]
                            amount_str = str(row[amount_col]).replace(',', '.').replace(' ', '')
                            description = str(row[desc_col]).strip()
                            
                            # Парсим дату
                            try:
                                date = datetime.strptime(date_str, '%Y-%m-%d')
                            except:
                                try:
                                    date = datetime.strptime(date_str, '%d.%m.%Y')
                                except:
                                    try:
                                        date = datetime.strptime(date_str, '%d/%m/%Y')
                                    except:
                                        continue
                            
                            # Парсим сумму
                            try:
                                amount = float(amount_str)
                            except:
                                continue
                            
                            transaction = Transaction(
                                date=date.strftime('%Y-%m-%d'),
                                description=description,
                                amount=amount,
                                bank=bank_name
                            )
                            
                            # Категоризация
                            self._categorize_transaction(transaction)
                            transactions.append(transaction)
                            
                    except Exception as e:
                        print(f"Ошибка обработки строки: {e}")
                        continue
                        
        except Exception as e:
            print(f"Ошибка чтения файла {file_path}: {e}")
        
        return transactions
    
    def _find_date_column(self, row: Dict) -> Optional[str]:
        """Находит колонку с датой"""
        date_keywords = ['дата', 'date', 'время', 'time', 'день']
        for col in row.keys():
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in date_keywords):
                return col
        return None
    
    def _find_amount_column(self, row: Dict) -> Optional[str]:
        """Находит колонку с суммой"""
        amount_keywords = ['сумма', 'amount', 'сум', 'руб', 'rub', 'деньги', 'money']
        for col in row.keys():
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in amount_keywords):
                return col
        return None
    
    def _find_description_column(self, row: Dict) -> Optional[str]:
        """Находит колонку с описанием"""
        desc_keywords = ['описание', 'description', 'назначение', 'комментарий', 'comment', 'детали']
        for col in row.keys():
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in desc_keywords):
                return col
        return None
    
    def _categorize_transaction(self, transaction: Transaction):
        """Автоматически категоризирует транзакцию"""
        description_lower = transaction.description.lower()
        
        # Определяем тип транзакции
        if transaction.amount > 0:
            transaction.transaction_type = "income"
        else:
            transaction.transaction_type = "expense"
        
        # Ищем подходящую категорию
        for category, keywords in self.category_rules.items():
            if any(keyword in description_lower for keyword in keywords):
                transaction.category = category
                return
        
        # Если не нашли, ставим "Прочее"
        transaction.category = "Прочее"
    
    def add_transactions(self, transactions: List[Transaction]):
        """Добавляет транзакции к существующим"""
        self.transactions.extend(transactions)
    
    def get_summary(self) -> Dict:
        """Получает общую сводку"""
        if not self.transactions:
            return {"error": "Нет данных для анализа"}
        
        total_income = sum(t.amount for t in self.transactions if t.amount > 0)
        total_expense = abs(sum(t.amount for t in self.transactions if t.amount < 0))
        balance = total_income - total_expense
        
        dates = [datetime.strptime(t.date, '%Y-%m-%d') for t in self.transactions]
        
        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance,
            "transaction_count": len(self.transactions),
            "period": {
                "start": min(dates).strftime('%Y-%m-%d') if dates else "",
                "end": max(dates).strftime('%Y-%m-%d') if dates else ""
            }
        }
    
    def get_category_analysis(self) -> Dict:
        """Анализ по категориям"""
        if not self.transactions:
            return {"error": "Нет данных для анализа"}
        
        # Группируем по категориям
        income_by_category = {}
        expense_by_category = {}
        
        for transaction in self.transactions:
            if transaction.amount > 0:
                income_by_category[transaction.category] = income_by_category.get(transaction.category, 0) + transaction.amount
            else:
                expense_by_category[transaction.category] = expense_by_category.get(transaction.category, 0) + transaction.amount
        
        # Сортируем по убыванию
        income_by_category = dict(sorted(income_by_category.items(), key=lambda x: x[1], reverse=True))
        expense_by_category = dict(sorted(expense_by_category.items(), key=lambda x: x[1], reverse=True))
        
        return {
            "income_by_category": income_by_category,
            "expense_by_category": expense_by_category,
            "top_expense_categories": dict(list(expense_by_category.items())[:10])
        }
    
    def get_monthly_analysis(self) -> Dict:
        """Месячный анализ"""
        if not self.transactions:
            return {"error": "Нет данных для анализа"}
        
        monthly_income = {}
        monthly_expense = {}
        monthly_balance = {}
        
        for transaction in self.transactions:
            date = datetime.strptime(transaction.date, '%Y-%m-%d')
            month_key = date.strftime('%Y-%m')
            
            if transaction.amount > 0:
                monthly_income[month_key] = monthly_income.get(month_key, 0) + transaction.amount
            else:
                monthly_expense[month_key] = monthly_expense.get(month_key, 0) + transaction.amount
        
        # Вычисляем баланс по месяцам
        all_months = set(monthly_income.keys()) | set(monthly_expense.keys())
        for month in all_months:
            income = monthly_income.get(month, 0)
            expense = monthly_expense.get(month, 0)
            monthly_balance[month] = income + expense  # expense уже отрицательные
        
        return {
            "monthly_income": monthly_income,
            "monthly_expense": monthly_expense,
            "monthly_balance": monthly_balance
        }
    
    def export_to_csv(self, filename: str = "financial_report.csv"):
        """Экспортирует отчет в CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            if self.transactions:
                writer = csv.DictWriter(file, fieldnames=['date', 'description', 'amount', 'category', 'bank', 'transaction_type'])
                writer.writeheader()
                for transaction in self.transactions:
                    writer.writerow(asdict(transaction))
    
    def export_summary_to_txt(self, filename: str = "summary.txt"):
        """Экспортирует сводку в текстовый файл"""
        with open(filename, 'w', encoding='utf-8') as file:
            summary = self.get_summary()
            if "error" not in summary:
                file.write("=== ФИНАНСОВАЯ СВОДКА ===\n")
                file.write(f"Общий доход: {summary['total_income']:,.2f} руб.\n")
                file.write(f"Общие расходы: {summary['total_expense']:,.2f} руб.\n")
                file.write(f"Баланс: {summary['balance']:,.2f} руб.\n")
                file.write(f"Количество транзакций: {summary['transaction_count']}\n")
                file.write(f"Период: {summary['period']['start']} - {summary['period']['end']}\n\n")
                
                # Анализ по категориям
                category_analysis = self.get_category_analysis()
                if "error" not in category_analysis:
                    file.write("=== РАСХОДЫ ПО КАТЕГОРИЯМ ===\n")
                    for category, amount in category_analysis['top_expense_categories'].items():
                        file.write(f"{category}: {abs(amount):,.2f} руб.\n")
                    
                    file.write("\n=== ДОХОДЫ ПО КАТЕГОРИЯМ ===\n")
                    for category, amount in category_analysis['income_by_category'].items():
                        file.write(f"{category}: {amount:,.2f} руб.\n")
                
                # Месячный анализ
                monthly_analysis = self.get_monthly_analysis()
                if "error" not in monthly_analysis:
                    file.write("\n=== МЕСЯЧНЫЙ БАЛАНС ===\n")
                    for month, balance in monthly_analysis['monthly_balance'].items():
                        file.write(f"{month}: {balance:,.2f} руб.\n")

def main():
    """Основная функция"""
    analytics = SimpleBankAnalytics()
    
    print("=== Система анализа банковских выписок ===")
    print("Поддерживаемые форматы: CSV")
    print("Поместите файлы выписок в папку 'statements' и запустите анализ")
    
    # Создаем папку для выписок
    statements_dir = Path("statements")
    statements_dir.mkdir(exist_ok=True)
    
    # Ищем файлы выписок
    all_transactions = []
    for file_path in statements_dir.glob("*.csv"):
        try:
            print(f"Обрабатываю файл: {file_path.name}")
            transactions = analytics.load_csv(str(file_path), file_path.stem)
            all_transactions.extend(transactions)
            print(f"Найдено транзакций: {len(transactions)}")
        except Exception as e:
            print(f"Ошибка обработки {file_path.name}: {e}")
    
    if all_transactions:
        print(f"\nВсего транзакций: {len(all_transactions)}")
        analytics.add_transactions(all_transactions)
        
        # Выводим сводку
        summary = analytics.get_summary()
        print("\n=== СВОДКА ===")
        print(f"Общий доход: {summary['total_income']:,.2f} руб.")
        print(f"Общие расходы: {summary['total_expense']:,.2f} руб.")
        print(f"Баланс: {summary['balance']:,.2f} руб.")
        print(f"Период: {summary['period']['start']} - {summary['period']['end']}")
        
        # Анализ по категориям
        category_analysis = analytics.get_category_analysis()
        print("\n=== ТОП-5 РАСХОДОВ ПО КАТЕГОРИЯМ ===")
        for category, amount in list(category_analysis['top_expense_categories'].items())[:5]:
            print(f"{category}: {abs(amount):,.2f} руб.")
        
        # Экспорт отчетов
        analytics.export_to_csv("financial_report.csv")
        analytics.export_summary_to_txt("summary.txt")
        print(f"\nОтчеты сохранены:")
        print(f"- financial_report.csv (все транзакции)")
        print(f"- summary.txt (сводка)")
        
    else:
        print("Файлы выписок не найдены. Поместите CSV файлы в папку 'statements'")

if __name__ == "__main__":
    main()
