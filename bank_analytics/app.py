#!/usr/bin/env python3
"""
Веб-приложение для анализа банковских выписок
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os
import json
from pathlib import Path
from werkzeug.utils import secure_filename
from bank_analytics import BankStatementParser, FinancialAnalytics
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'statements'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Создаем папку для загрузок
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Глобальные переменные для хранения данных
current_analytics = None
current_transactions = []

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Загрузка файлов выписок"""
    global current_analytics, current_transactions
    
    if 'files' not in request.files:
        return jsonify({'error': 'Файлы не выбраны'}), 400
    
    files = request.files.getlist('files')
    if not files or all(file.filename == '' for file in files):
        return jsonify({'error': 'Файлы не выбраны'}), 400
    
    parser = BankStatementParser()
    all_transactions = []
    
    for file in files:
        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                bank_name = Path(filename).stem
                transactions = parser.parse_file(filepath, bank_name)
                all_transactions.extend(transactions)
            except Exception as e:
                return jsonify({'error': f'Ошибка обработки файла {filename}: {str(e)}'}), 400
    
    if all_transactions:
        current_transactions = all_transactions
        current_analytics = FinancialAnalytics(all_transactions)
        return jsonify({
            'success': True,
            'message': f'Обработано {len(all_transactions)} транзакций',
            'transactions_count': len(all_transactions)
        })
    else:
        return jsonify({'error': 'Не удалось обработать транзакции'}), 400

@app.route('/summary')
def get_summary():
    """Получение сводки"""
    if not current_analytics:
        return jsonify({'error': 'Нет данных для анализа'}), 400
    
    summary = current_analytics.get_summary()
    return jsonify(summary)

@app.route('/categories')
def get_categories():
    """Получение анализа по категориям"""
    if not current_analytics:
        return jsonify({'error': 'Нет данных для анализа'}), 400
    
    categories = current_analytics.get_category_analysis()
    return jsonify(categories)

@app.route('/monthly')
def get_monthly():
    """Получение месячного анализа"""
    if not current_analytics:
        return jsonify({'error': 'Нет данных для анализа'}), 400
    
    monthly = current_analytics.get_monthly_analysis()
    return jsonify(monthly)

@app.route('/trends')
def get_trends():
    """Получение трендов"""
    if not current_analytics:
        return jsonify({'error': 'Нет данных для анализа'}), 400
    
    trends = current_analytics.get_trends()
    return jsonify(trends)

@app.route('/transactions')
def get_transactions():
    """Получение списка транзакций"""
    if not current_analytics:
        return jsonify({'error': 'Нет данных для анализа'}), 400
    
    # Пагинация
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    transactions_data = current_analytics.df.iloc[start_idx:end_idx].to_dict('records')
    
    return jsonify({
        'transactions': transactions_data,
        'total': len(current_analytics.df),
        'page': page,
        'per_page': per_page,
        'total_pages': (len(current_analytics.df) + per_page - 1) // per_page
    })

@app.route('/export/excel')
def export_excel():
    """Экспорт в Excel"""
    if not current_analytics:
        return jsonify({'error': 'Нет данных для экспорта'}), 400
    
    filename = f"financial_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    current_analytics.export_to_excel(filepath)
    
    return send_file(filepath, as_attachment=True, download_name=filename)

@app.route('/export/csv')
def export_csv():
    """Экспорт в CSV"""
    if not current_analytics:
        return jsonify({'error': 'Нет данных для экспорта'}), 400
    
    filename = f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    current_analytics.df.to_csv(filepath, index=False, encoding='utf-8')
    
    return send_file(filepath, as_attachment=True, download_name=filename)

@app.route('/update_category', methods=['POST'])
def update_category():
    """Обновление категории транзакции"""
    if not current_analytics:
        return jsonify({'error': 'Нет данных для обновления'}), 400
    
    data = request.get_json()
    transaction_id = data.get('transaction_id')
    new_category = data.get('category')
    
    if transaction_id is None or new_category is None:
        return jsonify({'error': 'Не указаны ID транзакции или категория'}), 400
    
    try:
        # Обновляем категорию в DataFrame
        current_analytics.df.loc[transaction_id, 'category'] = new_category
        
        # Обновляем в списке транзакций
        if transaction_id < len(current_transactions):
            current_transactions[transaction_id].category = new_category
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
