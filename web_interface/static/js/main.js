/**
 * Гриша Bot Web Interface - Main JavaScript
 * Интерактивность и функциональность веб-интерфейса
 */

// Глобальные переменные
let currentUser = null;
let refreshInterval = null;
let charts = {};

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Гриша Bot Web Interface загружен');
    
    // Инициализация компонентов
    initTooltips();
    initModals();
    initCharts();
    initSearch();
    initFilters();
    initAutoRefresh();
    
    // Загрузка данных
    loadInitialData();
    
    // Настройка обработчиков событий
    setupEventListeners();
});

/**
 * Инициализация tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Инициализация модальных окон
 */
function initModals() {
    // Автоматическое скрытие модальных окон при клике вне их
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            const modal = bootstrap.Modal.getInstance(event.target);
            if (modal) {
                modal.hide();
            }
        }
    });
}

/**
 * Инициализация графиков
 */
function initCharts() {
    // Инициализация графиков активности
    if (document.getElementById('activityChart')) {
        initActivityChart();
    }
    
    // Инициализация графиков распределения
    if (document.getElementById('videoDistributionChart')) {
        initVideoDistributionChart();
    }
}

/**
 * Инициализация поиска
 */
function initSearch() {
    const searchInputs = document.querySelectorAll('input[type="search"], input[placeholder*="Поиск"]');
    searchInputs.forEach(input => {
        input.addEventListener('input', debounce(handleSearch, 300));
    });
}

/**
 * Инициализация фильтров
 */
function initFilters() {
    const filterInputs = document.querySelectorAll('select, input[type="date"], input[type="range"]');
    filterInputs.forEach(input => {
        input.addEventListener('change', handleFilterChange);
    });
}

/**
 * Инициализация автообновления
 */
function initAutoRefresh() {
    // Автообновление каждые 30 секунд
    refreshInterval = setInterval(refreshData, 30000);
    
    // Обновление при возвращении на вкладку
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            refreshData();
        }
    });
}

/**
 * Загрузка начальных данных
 */
async function loadInitialData() {
    try {
        showLoading();
        
        // Загрузка статистики
        await loadStats();
        
        // Загрузка видео
        await loadVideos();
        
        // Загрузка пользователей
        await loadUsers();
        
        hideLoading();
    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
        showError('Ошибка загрузки данных');
    }
}

/**
 * Загрузка статистики
 */
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        updateStatsDisplay(data);
        updateCharts(data);
    } catch (error) {
        console.error('Ошибка загрузки статистики:', error);
    }
}

/**
 * Загрузка видео
 */
async function loadVideos() {
    try {
        const response = await fetch('/api/videos');
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        updateVideosDisplay(data);
    } catch (error) {
        console.error('Ошибка загрузки видео:', error);
    }
}

/**
 * Загрузка пользователей
 */
async function loadUsers() {
    try {
        const response = await fetch('/api/users');
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        updateUsersDisplay(data);
    } catch (error) {
        console.error('Ошибка загрузки пользователей:', error);
    }
}

/**
 * Обновление отображения статистики
 */
function updateStatsDisplay(stats) {
    const elements = {
        'total-videos': stats.total_videos,
        'total-users': stats.total_users,
        'total-chats': stats.total_chats,
        'videos-today': stats.videos_today
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            animateNumber(element, parseInt(value));
        }
    });
}

/**
 * Обновление графиков
 */
function updateCharts(stats) {
    if (charts.activityChart) {
        charts.activityChart.data.datasets[0].data = [
            stats.videos_this_week,
            stats.videos_this_month,
            stats.total_videos
        ];
        charts.activityChart.update();
    }
    
    if (charts.videoDistributionChart) {
        charts.videoDistributionChart.data.datasets[0].data = [
            stats.videos_this_week,
            stats.videos_this_month,
            stats.total_videos
        ];
        charts.videoDistributionChart.update();
    }
}

/**
 * Обновление отображения видео
 */
function updateVideosDisplay(videos) {
    const container = document.getElementById('videosGrid');
    if (!container) return;
    
    if (videos.length === 0) {
        container.innerHTML = `
            <div class="col-12">
                <div class="text-center py-5">
                    <i class="fas fa-video fa-4x text-muted mb-4"></i>
                    <h4 class="text-muted">Нет видео</h4>
                    <p class="text-muted">Видео появятся здесь, когда пользователи начнут их отправлять</p>
                </div>
            </div>
        `;
        return;
    }
    
    const html = videos.map(video => createVideoCard(video)).join('');
    container.innerHTML = html;
}

/**
 * Создание карточки видео
 */
function createVideoCard(video) {
    const size = (video.file_size / 1024 / 1024).toFixed(1);
    const date = new Date(video.created_at).toLocaleDateString('ru-RU');
    
    return `
        <div class="col-xl-3 col-lg-4 col-md-6 mb-4 video-card" data-video-id="${video.id}">
            <div class="card shadow-sm h-100">
                <div class="card-img-top bg-dark d-flex align-items-center justify-content-center" style="height: 200px;">
                    <i class="fas fa-video fa-3x text-white"></i>
                </div>
                <div class="card-body">
                    <h6 class="card-title">${video.username || 'Unknown'}</h6>
                    <p class="card-text">
                        <small class="text-muted">
                            <i class="fas fa-calendar me-1"></i>${date}
                        </small><br>
                        <small class="text-muted">
                            <i class="fas fa-hdd me-1"></i>${size} MB
                        </small><br>
                        <small class="text-muted">
                            <i class="fas fa-comments me-1"></i>${video.chat_id}
                        </small>
                    </p>
                </div>
                <div class="card-footer bg-transparent">
                    <div class="btn-group w-100" role="group">
                        <button type="button" class="btn btn-outline-primary btn-sm" onclick="viewVideo(${video.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button type="button" class="btn btn-outline-success btn-sm" onclick="downloadVideo(${video.id})">
                            <i class="fas fa-download"></i>
                        </button>
                        <button type="button" class="btn btn-outline-info btn-sm" onclick="showVideoInfo(${video.id})">
                            <i class="fas fa-info"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Обновление отображения пользователей
 */
function updateUsersDisplay(users) {
    const tbody = document.querySelector('#usersTable tbody');
    if (!tbody) return;
    
    if (users.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center py-4">
                    <i class="fas fa-users fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">Нет пользователей</h5>
                    <p class="text-muted">Пользователи появятся здесь, когда начнут взаимодействовать с ботом</p>
                </td>
            </tr>
        `;
        return;
    }
    
    const html = users.map(user => createUserRow(user)).join('');
    tbody.innerHTML = html;
}

/**
 * Создание строки пользователя
 */
function createUserRow(user) {
    const lastVideo = user.last_video_date ? new Date(user.last_video_date).toLocaleDateString('ru-RU') : 'Нет видео';
    const status = user.video_count > 0 ? 'Активный' : 'Неактивный';
    const statusClass = user.video_count > 0 ? 'success' : 'secondary';
    
    return `
        <tr data-user-id="${user.user_id}">
            <td>
                <div class="d-flex align-items-center">
                    <div class="avatar-sm bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3">
                        ${(user.username || user.first_name || '?')[0].toUpperCase()}
                    </div>
                    <div>
                        <div class="fw-bold">
                            ${user.username || 'Без username'}
                            ${user.username ? `<small class="text-muted">@${user.username}</small>` : ''}
                        </div>
                        <small class="text-muted">
                            ${user.first_name} ${user.last_name}
                        </small>
                    </div>
                </div>
            </td>
            <td>
                <span class="badge bg-primary">${user.video_count}</span>
            </td>
            <td>
                <span class="text-muted">${lastVideo}</span>
            </td>
            <td>
                <span class="text-muted">${new Date(user.created_at).toLocaleDateString('ru-RU')}</span>
            </td>
            <td>
                <span class="badge bg-${statusClass}">${status}</span>
            </td>
            <td>
                <div class="btn-group" role="group">
                    <button type="button" class="btn btn-sm btn-outline-primary" onclick="viewUserVideos(${user.user_id})">
                        <i class="fas fa-video"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-info" onclick="viewUserInfo(${user.user_id})">
                        <i class="fas fa-info"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-warning" onclick="editUserPrefs(${user.user_id})">
                        <i class="fas fa-cog"></i>
                    </button>
                </div>
            </td>
        </tr>
    `;
}

/**
 * Анимация чисел
 */
function animateNumber(element, targetValue) {
    const startValue = parseInt(element.textContent) || 0;
    const duration = 1000;
    const startTime = performance.now();
    
    function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const currentValue = Math.round(startValue + (targetValue - startValue) * progress);
        element.textContent = currentValue;
        
        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        }
    }
    
    requestAnimationFrame(updateNumber);
}

/**
 * Обработка поиска
 */
function handleSearch(event) {
    const searchTerm = event.target.value.toLowerCase();
    const table = event.target.closest('.card').querySelector('table');
    
    if (!table) return;
    
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
}

/**
 * Обработка изменения фильтров
 */
function handleFilterChange(event) {
    // Логика фильтрации в зависимости от типа фильтра
    console.log('Фильтр изменен:', event.target.name, event.target.value);
}

/**
 * Обновление данных
 */
function refreshData() {
    console.log('🔄 Обновление данных...');
    loadInitialData();
}

/**
 * Показать загрузку
 */
function showLoading() {
    const loadingElements = document.querySelectorAll('.loading');
    loadingElements.forEach(el => el.classList.add('loading'));
}

/**
 * Скрыть загрузку
 */
function hideLoading() {
    const loadingElements = document.querySelectorAll('.loading');
    loadingElements.forEach(el => el.classList.remove('loading'));
}

/**
 * Показать ошибку
 */
function showError(message) {
    // Создание toast уведомления
    const toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white bg-danger border-0';
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-exclamation-triangle me-2"></i>${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Удаление после скрытия
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

/**
 * Показать успех
 */
function showSuccess(message) {
    const toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white bg-success border-0';
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-check-circle me-2"></i>${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

/**
 * Настройка обработчиков событий
 */
function setupEventListeners() {
    // Обработчик для кнопок обновления
    document.addEventListener('click', function(event) {
        if (event.target.matches('[onclick*="refresh"]')) {
            refreshData();
        }
    });
    
    // Обработчик для кнопок экспорта
    document.addEventListener('click', function(event) {
        if (event.target.matches('[onclick*="export"]')) {
            handleExport(event.target);
        }
    });
    
    // Обработчик для кнопок действий
    document.addEventListener('click', function(event) {
        if (event.target.matches('[onclick*="view"], [onclick*="download"], [onclick*="edit"]')) {
            handleAction(event.target);
        }
    });
}

/**
 * Обработка экспорта
 */
function handleExport(button) {
    const action = button.getAttribute('onclick');
    
    if (action.includes('exportData')) {
        exportDashboardData();
    } else if (action.includes('exportVideos')) {
        exportVideosData();
    } else if (action.includes('exportUsers')) {
        exportUsersData();
    }
}

/**
 * Обработка действий
 */
function handleAction(button) {
    const action = button.getAttribute('onclick');
    
    if (action.includes('viewVideo')) {
        const videoId = extractId(action);
        viewVideoDetails(videoId);
    } else if (action.includes('downloadVideo')) {
        const videoId = extractId(action);
        downloadVideoFile(videoId);
    } else if (action.includes('viewUserInfo')) {
        const userId = extractId(action);
        viewUserDetails(userId);
    }
}

/**
 * Извлечение ID из строки
 */
function extractId(actionString) {
    const match = actionString.match(/\((\d+)\)/);
    return match ? parseInt(match[1]) : null;
}

/**
 * Экспорт данных dashboard
 */
function exportDashboardData() {
    // Реализация экспорта данных dashboard
    showSuccess('Экспорт данных dashboard выполнен');
}

/**
 * Экспорт данных видео
 */
function exportVideosData() {
    // Реализация экспорта данных видео
    showSuccess('Экспорт данных видео выполнен');
}

/**
 * Экспорт данных пользователей
 */
function exportUsersData() {
    // Реализация экспорта данных пользователей
    showSuccess('Экспорт данных пользователей выполнен');
}

/**
 * Просмотр деталей видео
 */
function viewVideoDetails(videoId) {
    // Реализация просмотра деталей видео
    console.log('Просмотр видео:', videoId);
}

/**
 * Скачивание файла видео
 */
function downloadVideoFile(videoId) {
    // Реализация скачивания видео
    console.log('Скачивание видео:', videoId);
}

/**
 * Просмотр деталей пользователя
 */
function viewUserDetails(userId) {
    // Реализация просмотра деталей пользователя
    console.log('Просмотр пользователя:', userId);
}

/**
 * Функция debounce для оптимизации поиска
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Функция throttle для ограничения частоты вызовов
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Форматирование размера файла
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Форматирование даты
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Очистка при выгрузке страницы
 */
window.addEventListener('beforeunload', function() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});

// Экспорт функций для использования в других скриптах
window.GrishaBot = {
    refreshData,
    showError,
    showSuccess,
    formatFileSize,
    formatDate
};
