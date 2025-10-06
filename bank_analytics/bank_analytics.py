#!/usr/bin/env python3
"""
Универсальная система анализа банковских выписок
Поддерживает различные форматы: CSV, Excel, TXT
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
import os
from typing import Dict, List, Optional, Tuple
import json
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Transaction:
    """Структура транзакции"""
    date: datetime
    description: str
    amount: float
    category: str = "Неопределено"
    subcategory: str = ""
    bank: str = ""
    account: str = ""
    currency: str = "RUB"
    transaction_type: str = ""  # income/expense
    
    def to_dict(self) -> Dict:
        return {
            'date': self.date.strftime('%Y-%m-%d'),
            'description': self.description,
            'amount': self.amount,
            'category': self.category,
            'subcategory': self.subcategory,
            'bank': self.bank,
            'account': self.account,
            'currency': self.currency,
            'transaction_type': self.transaction_type
        }

class BankStatementParser:
    """Универсальный парсер банковских выписок"""
    
    def __init__(self):
        self.supported_formats = ['.csv', '.xlsx', '.xls', '.txt']
        self.category_rules = self._load_category_rules()
    
    def _load_category_rules(self) -> Dict[str, List[str]]:
        """Загружает правила категоризации транзакций"""
        return {
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
    
    def detect_format(self, file_path: str) -> str:
        """Определяет формат файла"""
        ext = Path(file_path).suffix.lower()
        if ext not in self.supported_formats:
            raise ValueError(f"Неподдерживаемый формат: {ext}")
        return ext
    
    def parse_file(self, file_path: str, bank_name: str = "") -> List[Transaction]:
        """Парсит файл выписки"""
        format_type = self.detect_format(file_path)
        
        if format_type == '.csv':
            return self._parse_csv(file_path, bank_name)
        elif format_type in ['.xlsx', '.xls']:
            return self._parse_excel(file_path, bank_name)
        elif format_type == '.txt':
            return self._parse_txt(file_path, bank_name)
        else:
            raise ValueError(f"Формат {format_type} не поддерживается")
    
    def _parse_csv(self, file_path: str, bank_name: str) -> List[Transaction]:
        """Парсит CSV файл"""
        try:
            # Пробуем разные кодировки
            for encoding in ['utf-8', 'cp1251', 'windows-1251']:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("Не удалось определить кодировку файла")
            
            return self._process_dataframe(df, bank_name)
        except Exception as e:
            raise ValueError(f"Ошибка парсинга CSV: {e}")
    
    def _parse_excel(self, file_path: str, bank_name: str) -> List[Transaction]:
        """Парсит Excel файл"""
        try:
            df = pd.read_excel(file_path)
            return self._process_dataframe(df, bank_name)
        except Exception as e:
            raise ValueError(f"Ошибка парсинга Excel: {e}")
    
    def _parse_txt(self, file_path: str, bank_name: str) -> List[Transaction]:
        """Парсит текстовый файл"""
        transactions = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Простой парсер для текстовых выписок
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Ищем паттерны даты и суммы
                date_match = re.search(r'(\d{1,2}[./]\d{1,2}[./]\d{2,4})', line)
                amount_match = re.search(r'([+-]?\d+[.,]\d{2})', line)
                
                if date_match and amount_match:
                    try:
                        date_str = date_match.group(1)
                        amount_str = amount_match.group(1).replace(',', '.')
                        
                        # Парсим дату
                        if '/' in date_str:
                            date = datetime.strptime(date_str, '%d/%m/%Y')
                        else:
                            date = datetime.strptime(date_str, '%d.%m.%Y')
                        
                        amount = float(amount_str)
                        description = line.replace(date_str, '').replace(amount_str, '').strip()
                        
                        transaction = Transaction(
                            date=date,
                            description=description,
                            amount=amount,
                            bank=bank_name
                        )
                        transactions.append(transaction)
                    except:
                        continue
                        
        except Exception as e:
            raise ValueError(f"Ошибка парсинга TXT: {e}")
        
        return transactions
    
    def _process_dataframe(self, df: pd.DataFrame, bank_name: str) -> List[Transaction]:
        """Обрабатывает DataFrame и создает транзакции"""
        transactions = []
        
        # Автоматическое определение колонок
        date_col = self._find_date_column(df)
        amount_col = self._find_amount_column(df)
        desc_col = self._find_description_column(df)
        
        if not all([date_col, amount_col, desc_col]):
            raise ValueError("Не удалось определить необходимые колонки в файле")
        
        for _, row in df.iterrows():
            try:
                # Парсим дату
                date = pd.to_datetime(row[date_col])
                
                # Парсим сумму
                amount = float(str(row[amount_col]).replace(',', '.').replace(' ', ''))
                
                # Описание
                description = str(row[desc_col]).strip()
                
                transaction = Transaction(
                    date=date,
                    description=description,
                    amount=amount,
                    bank=bank_name
                )
                
                # Автоматическая категоризация
                self._categorize_transaction(transaction)
                
                transactions.append(transaction)
                
            except Exception as e:
                print(f"Ошибка обработки строки: {e}")
                continue
        
        return transactions
    
    def _find_date_column(self, df: pd.DataFrame) -> Optional[str]:
        """Находит колонку с датами"""
        date_keywords = ['дата', 'date', 'время', 'time', 'день']
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in date_keywords):
                return col
        
        # Если не нашли по ключевым словам, ищем колонку с датами
        for col in df.columns:
            try:
                pd.to_datetime(df[col].iloc[0])
                return col
            except:
                continue
        
        return None
    
    def _find_amount_column(self, df: pd.DataFrame) -> Optional[str]:
        """Находит колонку с суммами"""
        amount_keywords = ['сумма', 'amount', 'сум', 'руб', 'rub', 'деньги', 'money']
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in amount_keywords):
                return col
        
        # Ищем колонку с числовыми значениями
        for col in df.columns:
            try:
                float(str(df[col].iloc[0]).replace(',', '.').replace(' ', ''))
                return col
            except:
                continue
        
        return None
    
    def _find_description_column(self, df: pd.DataFrame) -> Optional[str]:
        """Находит колонку с описанием"""
        desc_keywords = ['описание', 'description', 'назначение', 'комментарий', 'comment', 'детали']
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in desc_keywords):
                return col
        
        # Берем первую текстовую колонку
        for col in df.columns:
            if df[col].dtype == 'object':
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

class FinancialAnalytics:
    """Аналитика финансовых данных"""
    
    def __init__(self, transactions: List[Transaction]):
        self.transactions = transactions
        self.df = pd.DataFrame([t.to_dict() for t in transactions])
        if not self.df.empty:
            self.df['date'] = pd.to_datetime(self.df['date'])
            self.df['amount'] = pd.to_numeric(self.df['amount'])
    
    def get_summary(self) -> Dict:
        """Получает общую сводку"""
        if self.df.empty:
            return {"error": "Нет данных для анализа"}
        
        total_income = self.df[self.df['amount'] > 0]['amount'].sum()
        total_expense = abs(self.df[self.df['amount'] < 0]['amount'].sum())
        balance = total_income - total_expense
        
        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance,
            "transaction_count": len(self.df),
            "period": {
                "start": self.df['date'].min().strftime('%Y-%m-%d'),
                "end": self.df['date'].max().strftime('%Y-%m-%d')
            }
        }
    
    def get_category_analysis(self) -> Dict:
        """Анализ по категориям"""
        if self.df.empty:
            return {"error": "Нет данных для анализа"}
        
        # Доходы по категориям
        income_by_category = self.df[self.df['amount'] > 0].groupby('category')['amount'].sum().sort_values(ascending=False)
        
        # Расходы по категориям
        expense_by_category = self.df[self.df['amount'] < 0].groupby('category')['amount'].sum().sort_values(ascending=True)
        
        return {
            "income_by_category": income_by_category.to_dict(),
            "expense_by_category": expense_by_category.to_dict(),
            "top_expense_categories": expense_by_category.head(10).to_dict()
        }
    
    def get_monthly_analysis(self) -> Dict:
        """Месячный анализ"""
        if self.df.empty:
            return {"error": "Нет данных для анализа"}
        
        self.df['month'] = self.df['date'].dt.to_period('M')
        
        monthly_income = self.df[self.df['amount'] > 0].groupby('month')['amount'].sum()
        monthly_expense = self.df[self.df['amount'] < 0].groupby('month')['amount'].sum()
        monthly_balance = monthly_income + monthly_expense  # expense уже отрицательные
        
        return {
            "monthly_income": {str(k): v for k, v in monthly_income.items()},
            "monthly_expense": {str(k): v for k, v in monthly_expense.items()},
            "monthly_balance": {str(k): v for k, v in monthly_balance.items()}
        }
    
    def get_trends(self) -> Dict:
        """Анализ трендов"""
        if self.df.empty:
            return {"error": "Нет данных для анализа"}
        
        # Средние значения
        avg_monthly_income = self.df[self.df['amount'] > 0]['amount'].mean()
        avg_monthly_expense = abs(self.df[self.df['amount'] < 0]['amount'].mean())
        
        # Тренд последних 3 месяцев
        last_3_months = self.df[self.df['date'] >= (self.df['date'].max() - timedelta(days=90))]
        recent_avg_income = last_3_months[last_3_months['amount'] > 0]['amount'].mean()
        recent_avg_expense = abs(last_3_months[last_3_months['amount'] < 0]['amount'].mean())
        
        return {
            "average_monthly_income": avg_monthly_income,
            "average_monthly_expense": avg_monthly_expense,
            "recent_3_months_avg_income": recent_avg_income,
            "recent_3_months_avg_expense": recent_avg_expense,
            "income_trend": "рост" if recent_avg_income > avg_monthly_income else "снижение",
            "expense_trend": "рост" if recent_avg_expense > avg_monthly_expense else "снижение"
        }
    
    def export_to_excel(self, filename: str = "financial_report.xlsx"):
        """Экспортирует отчет в Excel"""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Основные данные
            self.df.to_excel(writer, sheet_name='Транзакции', index=False)
            
            # Сводка
            summary = self.get_summary()
            summary_df = pd.DataFrame(list(summary.items()), columns=['Показатель', 'Значение'])
            summary_df.to_excel(writer, sheet_name='Сводка', index=False)
            
            # Анализ по категориям
            category_analysis = self.get_category_analysis()
            if 'expense_by_category' in category_analysis:
                expense_df = pd.DataFrame(list(category_analysis['expense_by_category'].items()), 
                                        columns=['Категория', 'Сумма'])
                expense_df.to_excel(writer, sheet_name='Расходы по категориям', index=False)
            
            # Месячный анализ
            monthly_analysis = self.get_monthly_analysis()
            if 'monthly_balance' in monthly_analysis:
                monthly_df = pd.DataFrame(list(monthly_analysis['monthly_balance'].items()), 
                                        columns=['Месяц', 'Баланс'])
                monthly_df.to_excel(writer, sheet_name='Месячный баланс', index=False)

def main():
    """Основная функция для тестирования"""
    parser = BankStatementParser()
    analytics = None
    
    print("=== Система анализа банковских выписок ===")
    print("Поддерживаемые форматы: CSV, Excel, TXT")
    print("Поместите файлы выписок в папку 'statements' и запустите анализ")
    
    # Создаем папку для выписок
    statements_dir = Path("statements")
    statements_dir.mkdir(exist_ok=True)
    
    # Ищем файлы выписок
    all_transactions = []
    for file_path in statements_dir.glob("*"):
        if file_path.suffix.lower() in ['.csv', '.xlsx', '.xls', '.txt']:
            try:
                print(f"Обрабатываю файл: {file_path.name}")
                transactions = parser.parse_file(str(file_path), file_path.stem)
                all_transactions.extend(transactions)
                print(f"Найдено транзакций: {len(transactions)}")
            except Exception as e:
                print(f"Ошибка обработки {file_path.name}: {e}")
    
    if all_transactions:
        print(f"\nВсего транзакций: {len(all_transactions)}")
        analytics = FinancialAnalytics(all_transactions)
        
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
        
        # Экспорт в Excel
        analytics.export_to_excel("financial_report.xlsx")
        print(f"\nОтчет сохранен в файл: financial_report.xlsx")
        
    else:
        print("Файлы выписок не найдены. Поместите файлы в папку 'statements'")

if __name__ == "__main__":
    main()
