// Основной JavaScript для приложения анализа банковских выписок

let currentPage = 1;
let totalPages = 1;
let categoryChart = null;
let monthlyChart = null;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initializeUpload();
    initializeEventListeners();
});

// Инициализация загрузки файлов
function initializeUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');

    // Клик по области загрузки
    uploadArea.addEventListener('click', () => fileInput.click());

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        handleFiles(files);
    });

    // Выбор файлов
    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });
}

// Обработка загруженных файлов
async function handleFiles(files) {
    if (files.length === 0) return;

    const formData = new FormData();
    for (let file of files) {
        formData.append('files', file);
    }

    showLoading(true);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            showSuccess(result.message);
            await loadAnalytics();
        } else {
            showError(result.error);
        }
    } catch (error) {
        showError('Ошибка загрузки файлов: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Загрузка аналитики
async function loadAnalytics() {
    try {
        await Promise.all([
            loadSummary(),
            loadCategories(),
            loadMonthly(),
            loadTransactions()
        ]);
        
        showSections();
    } catch (error) {
        showError('Ошибка загрузки аналитики: ' + error.message);
    }
}

// Загрузка сводки
async function loadSummary() {
    const response = await fetch('/summary');
    const data = await response.json();

    if (data.error) {
        throw new Error(data.error);
    }

    document.getElementById('totalIncome').textContent = formatCurrency(data.total_income);
    document.getElementById('totalExpense').textContent = formatCurrency(data.total_expense);
    document.getElementById('totalBalance').textContent = formatCurrency(data.balance);
}

// Загрузка категорий
async function loadCategories() {
    const response = await fetch('/categories');
    const data = await response.json();

    if (data.error) {
        throw new Error(data.error);
    }

    createCategoryChart(data.expense_by_category);
}

// Загрузка месячных данных
async function loadMonthly() {
    const response = await fetch('/monthly');
    const data = await response.json();

    if (data.error) {
        throw new Error(data.error);
    }

    createMonthlyChart(data.monthly_balance);
}

// Загрузка транзакций
async function loadTransactions(page = 1) {
    const response = await fetch(`/transactions?page=${page}&per_page=50`);
    const data = await response.json();

    if (data.error) {
        throw new Error(data.error);
    }

    currentPage = data.page;
    totalPages = data.total_pages;
    
    displayTransactions(data.transactions);
    updatePagination();
}

// Создание графика категорий
function createCategoryChart(categoryData) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    if (categoryChart) {
        categoryChart.destroy();
    }

    const labels = Object.keys(categoryData);
    const values = Object.values(categoryData).map(v => Math.abs(v));

    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                    '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF',
                    '#4BC0C0', '#FF6384', '#36A2EB', '#FFCE56'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Создание месячного графика
function createMonthlyChart(monthlyData) {
    const ctx = document.getElementById('monthlyChart').getContext('2d');
    
    if (monthlyChart) {
        monthlyChart.destroy();
    }

    const labels = Object.keys(monthlyData);
    const values = Object.values(monthlyData);

    monthlyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Баланс',
                data: values,
                borderColor: '#36A2EB',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

// Отображение транзакций
function displayTransactions(transactions) {
    const tbody = document.getElementById('transactionsTable');
    tbody.innerHTML = '';

    transactions.forEach(transaction => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${formatDate(transaction.date)}</td>
            <td>${transaction.description}</td>
            <td class="${transaction.amount > 0 ? 'text-success' : 'text-danger'}">
                ${formatCurrency(transaction.amount)}
            </td>
            <td>
                <span class="badge bg-secondary category-badge">${transaction.category}</span>
            </td>
            <td>${transaction.bank}</td>
        `;
        tbody.appendChild(row);
    });
}

// Обновление пагинации
function updatePagination() {
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';

    // Предыдущая страница
    const prevLi = document.createElement('li');
    prevLi.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
    prevLi.innerHTML = `<a class="page-link" href="#" onclick="loadTransactions(${currentPage - 1})">Предыдущая</a>`;
    pagination.appendChild(prevLi);

    // Номера страниц
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);

    for (let i = startPage; i <= endPage; i++) {
        const li = document.createElement('li');
        li.className = `page-item ${i === currentPage ? 'active' : ''}`;
        li.innerHTML = `<a class="page-link" href="#" onclick="loadTransactions(${i})">${i}</a>`;
        pagination.appendChild(li);
    }

    // Следующая страница
    const nextLi = document.createElement('li');
    nextLi.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
    nextLi.innerHTML = `<a class="page-link" href="#" onclick="loadTransactions(${currentPage + 1})">Следующая</a>`;
    pagination.appendChild(nextLi);
}

// Экспорт в Excel
async function exportExcel() {
    try {
        const response = await fetch('/export/excel');
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'financial_report.xlsx';
            a.click();
            window.URL.revokeObjectURL(url);
        } else {
            showError('Ошибка экспорта в Excel');
        }
    } catch (error) {
        showError('Ошибка экспорта: ' + error.message);
    }
}

// Экспорт в CSV
async function exportCSV() {
    try {
        const response = await fetch('/export/csv');
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'transactions.csv';
            a.click();
            window.URL.revokeObjectURL(url);
        } else {
            showError('Ошибка экспорта в CSV');
        }
    } catch (error) {
        showError('Ошибка экспорта: ' + error.message);
    }
}

// Показать секции
function showSections() {
    document.getElementById('summarySection').style.display = 'block';
    document.getElementById('chartsSection').style.display = 'block';
    document.getElementById('transactionsSection').style.display = 'block';
}

// Показать загрузку
function showLoading(show) {
    const loading = document.querySelector('.loading');
    if (show) {
        loading.classList.add('show');
    } else {
        loading.classList.remove('show');
    }
}

// Показать успех
function showSuccess(message) {
    showAlert(message, 'success');
}

// Показать ошибку
function showError(message) {
    showAlert(message, 'danger');
}

// Показать уведомление
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Автоматически скрыть через 5 секунд
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Форматирование валюты
function formatCurrency(amount) {
    return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 2
    }).format(amount);
}

// Форматирование даты
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU');
}

// Инициализация обработчиков событий
function initializeEventListeners() {
    // Обработчики для пагинации уже добавлены в updatePagination()
}
