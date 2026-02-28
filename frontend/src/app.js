// Configuration
const API_BASE_URL = 'https://2sf6gfaqu3.execute-api.us-east-1.amazonaws.com/dev';

const PALETTES = {
    indigo: {
        primary: '#3f51b5', primaryDark: '#303f9f', success: '#4caf50', background: '#f5f7fb', surface: '#ffffff', text: '#0f172a', textMuted: '#5c6b7a', border: '#e3e7ef'
    },
    teal: {
        primary: '#009688', primaryDark: '#00796b', success: '#26a69a', background: '#f3f7f6', surface: '#ffffff', text: '#0f172a', textMuted: '#4b5563', border: '#d7e2dd'
    },
    amber: {
        primary: '#ffb300', primaryDark: '#f59e00', success: '#4caf50', background: '#fdf8ed', surface: '#ffffff', text: '#0f172a', textMuted: '#6b7280', border: '#f0e6d7'
    },
    slate: {
        primary: '#546e7a', primaryDark: '#37474f', success: '#8bc34a', background: '#f6f7f9', surface: '#ffffff', text: '#0f172a', textMuted: '#4b5563', border: '#e4e8ee'
    }
};

// Global state
let searchTimeout;
let currentBooks = [];
let currentTheme = 'light';

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    loadTheme();
    loadPalette();
    loadBooks();
    updateStats();
    setupEventListeners();
    optimizeForMobile();
}

function setupEventListeners() {
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', function(e) {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            if (e.target.value.length > 2) {
                searchBooks(e.target.value);
            } else {
                hideSearchResults();
            }
        }, 300);
    });

    // Touch events for mobile
    document.addEventListener('touchstart', function(e) {
        if (e.target.classList.contains('modal')) {
            closeModal(e.target.id);
        }
        if (!e.target.closest('.search-container')) {
            hideSearchResults();
        }
    });

    // Close modals on outside click
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            closeModal(e.target.id);
        }
        if (!e.target.closest('.search-container')) {
            hideSearchResults();
        }
    });

    // Close modals on escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const activeModal = document.querySelector('.modal.active');
            if (activeModal) {
                closeModal(activeModal.id);
            }
            if (isMobileMenuOpen()) {
                closeMobileMenu();
            }
            if (isFabSheetOpen()) {
                closeFabSheet();
            }
        }
    });

    // Prevent zoom on double tap for iOS
    let lastTouchEnd = 0;
    document.addEventListener('touchend', function(e) {
        const now = (new Date()).getTime();
        if (now - lastTouchEnd <= 300) {
            e.preventDefault();
        }
        lastTouchEnd = now;
    }, false);
}

// Theme Management
function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    currentTheme = savedTheme;
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon();
}

function toggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    localStorage.setItem('theme', currentTheme);
    updateThemeIcon();
}

function updateThemeIcon() {
    const icon = document.getElementById('themeIcon');
    if (!icon) return;
    icon.className = currentTheme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
}

// API Functions
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        showToast('API call failed: ' + error.message, 'error');
        throw error;
    }
}

// Book Functions
async function loadBooks() {
    try {
        showBooksSkeleton();
        const data = await apiCall('/books');
        currentBooks = data.books || [];
        displayBooks(currentBooks);
        updateStats();
    } catch (error) {
        document.getElementById('booksContainer').innerHTML = 
            '<div class="loading"><i class="fas fa-exclamation-triangle"></i><p>Failed to load books</p></div>';
    }
}

function displayBooks(books) {
    const container = document.getElementById('booksContainer');
    
    if (books.length === 0) {
        container.innerHTML = '<div class="loading"><i class="fas fa-book"></i><p>No books found</p></div>';
        return;
    }

    const booksHtml = books.map(book => `
        <div class="book-card">
            <div class="book-header">
                <h3 class="book-title">${escapeHtml(book.title)}</h3>
                <p class="book-author">by ${escapeHtml(book.author)}</p>
            </div>
            ${book.isbn ? `<p class="book-isbn"><strong>ISBN:</strong> ${escapeHtml(book.isbn)}</p>` : ''}
            ${book.publisher ? `<p><strong>Publisher:</strong> ${escapeHtml(book.publisher)}</p>` : ''}
            ${book.publication_year ? `<p><strong>Year:</strong> ${book.publication_year}</p>` : ''}
            ${book.pages ? `<p><strong>Pages:</strong> ${book.pages}</p>` : ''}
            ${renderAvailability(book)}
            <div class="book-meta">
                <span class="badge badge-primary">${book.total_copies} copies</span>
                <span class="badge badge-secondary">${book.max_loan_weeks}w loan</span>
            </div>
        </div>
    `).join('');

    container.innerHTML = booksHtml;
}

async function searchBooks(query) {
    if (!query || query.length < 2) {
        hideSearchResults();
        return;
    }

    try {
        const data = await apiCall(`/search?q=${encodeURIComponent(query)}&limit=10`);
        displaySearchResults(data.books || []);
    } catch (error) {
        hideSearchResults();
    }
}

function displaySearchResults(books) {
    const resultsContainer = document.getElementById('searchResults');
    
    if (books.length === 0) {
        resultsContainer.innerHTML = '<div class="search-result-item">No books found</div>';
    } else {
        const resultsHtml = books.map(book => `
            <div class="search-result-item" onclick="selectBook('${book.book_id}')">
                <div style="font-weight: 500;">${escapeHtml(book.title)}</div>
                <div style="color: var(--text-muted); font-size: 0.875rem;">by ${escapeHtml(book.author)}</div>
            </div>
        `).join('');
        resultsContainer.innerHTML = resultsHtml;
    }
    
    resultsContainer.style.display = 'block';
}

function hideSearchResults() {
    document.getElementById('searchResults').style.display = 'none';
}

function selectBook(bookId) {
    const book = currentBooks.find(b => b.book_id === bookId);
    if (book) {
        document.getElementById('searchInput').value = book.title;
        hideSearchResults();
    }
}

// Modal Functions
function showAddBookModal() {
    showModal('addBookModal');
}

function showCreateLoanModal() {
    // Set default dates
    const today = new Date().toISOString().split('T')[0];
    const dueDate = new Date();
    dueDate.setDate(dueDate.getDate() + 21); // 3 weeks default
    const dueDateStr = dueDate.toISOString().split('T')[0];
    
    document.querySelector('input[name="loan_date"]').value = today;
    document.querySelector('input[name="due_date"]').value = dueDateStr;
    
    showModal('createLoanModal');
}

function showReturnBookModal() {
    // Set default return date to today
    const today = new Date().toISOString().split('T')[0];
    document.querySelector('input[name="return_date"]').value = today;
    
    showModal('returnBookModal');
}

async function searchActiveLoans(query) {
    if (!query || query.length < 2) {
        document.getElementById('loanSearchResults').style.display = 'none';
        return;
    }

    try {
        const data = await apiCall('/loans');
        const activeLoans = (data.loans || []).filter(loan => loan.status === 'Prestado');
        const filteredLoans = activeLoans.filter(loan => 
            loan.loan_id.toLowerCase().includes(query.toLowerCase())
        );
        displayLoanSearchResults(filteredLoans);
    } catch (error) {
        document.getElementById('loanSearchResults').style.display = 'none';
    }
}

function displayLoanSearchResults(loans) {
    const resultsContainer = document.getElementById('loanSearchResults');
    
    if (loans.length === 0) {
        resultsContainer.innerHTML = '<div class="search-result-item">No se encontraron préstamos activos</div>';
    } else {
        const resultsHtml = loans.map(loan => `
            <div class="search-result-item" onclick="selectLoanForReturn('${loan.loan_id}', '${loan.loan_id}')">
                <div style="font-weight: 500;">Préstamo: ${loan.loan_id}</div>
                <div style="color: var(--text-muted); font-size: 0.875rem;">Vence: ${loan.due_date}</div>
            </div>
        `).join('');
        resultsContainer.innerHTML = resultsHtml;
    }
    
    resultsContainer.style.display = 'block';
}

function selectLoanForReturn(loanId, displayText) {
    document.getElementById('loanSearch').value = displayText;
    document.querySelector('input[name="loan_id"]').value = loanId;
    document.getElementById('loanSearchResults').style.display = 'none';
}

async function createLoan() {
    const form = document.getElementById('createLoanForm');
    const formData = new FormData(form);
    
    // Validate required fields
    if (!formData.get('book_copy_id') || !formData.get('member_id') || 
        !formData.get('loan_date') || !formData.get('due_date')) {
        showToast('Por favor completa todos los campos requeridos', 'error');
        return;
    }
    
    const loanData = {
        book_copy_id: formData.get('book_copy_id'),
        member_id: formData.get('member_id'),
        employee_id: formData.get('employee_id') || null,
        loan_date: formData.get('loan_date'),
        due_date: formData.get('due_date')
    };

    try {
        await apiCall('/loans', {
            method: 'POST',
            body: JSON.stringify(loanData)
        });

        showToast('Préstamo creado exitosamente!', 'success');
        closeModal('createLoanModal');
        loadBooks();
        updateStats();
    } catch (error) {
        showToast('Error al crear préstamo. Intenta de nuevo.', 'error');
    }
}

async function searchBooksForLoan(query) {
    if (!query || query.length < 2) {
        document.getElementById('bookSearchResults').style.display = 'none';
        return;
    }

    try {
        const data = await apiCall(`/search?q=${encodeURIComponent(query)}&limit=5`);
        displayBookSearchResults(data.books || []);
    } catch (error) {
        document.getElementById('bookSearchResults').style.display = 'none';
    }
}

function displayBookSearchResults(books) {
    const resultsContainer = document.getElementById('bookSearchResults');
    
    if (books.length === 0) {
        resultsContainer.innerHTML = '<div class="search-result-item">No se encontraron libros</div>';
    } else {
        const resultsHtml = books.map(book => `
            <div class="search-result-item" onclick="selectBookForLoan('${book.book_id}-001', '${escapeHtml(book.title)}')">
                <div style="font-weight: 500;">${escapeHtml(book.title)}</div>
                <div style="color: var(--text-muted); font-size: 0.875rem;">por ${escapeHtml(book.author)}</div>
            </div>
        `).join('');
        resultsContainer.innerHTML = resultsHtml;
    }
    
    resultsContainer.style.display = 'block';
}

function selectBookForLoan(bookCopyId, title) {
    document.getElementById('bookSearch').value = title;
    document.querySelector('input[name="book_copy_id"]').value = bookCopyId;
    document.getElementById('bookSearchResults').style.display = 'none';
}

async function searchMembersForLoan(query) {
    if (!query || query.length < 2) {
        document.getElementById('memberSearchResults').style.display = 'none';
        return;
    }

    try {
        const data = await apiCall(`/autocomplete?q=${encodeURIComponent(query)}&type=member&limit=5`);
        displayMemberSearchResults(data.results || []);
    } catch (error) {
        document.getElementById('memberSearchResults').style.display = 'none';
    }
}

function displayMemberSearchResults(members) {
    const resultsContainer = document.getElementById('memberSearchResults');
    
    if (members.length === 0) {
        resultsContainer.innerHTML = '<div class="search-result-item">No se encontraron miembros</div>';
    } else {
        const resultsHtml = members.map(member => `
            <div class="search-result-item" onclick="selectMemberForLoan('${member.id}', '${escapeHtml(member.name)}')">
                <div style="font-weight: 500;">${escapeHtml(member.name)}</div>
            </div>
        `).join('');
        resultsContainer.innerHTML = resultsHtml;
    }
    
    resultsContainer.style.display = 'block';
}

function selectMemberForLoan(memberId, name) {
    document.getElementById('memberSearch').value = name;
    document.querySelector('input[name="member_id"]').value = memberId;
    document.getElementById('memberSearchResults').style.display = 'none';
}

async function returnBook() {
    const form = document.getElementById('returnBookForm');
    const formData = new FormData(form);
    const loanId = formData.get('loan_id');
    const returnDate = formData.get('return_date');
    
    if (!loanId) {
        showToast('Por favor selecciona un préstamo', 'error');
        return;
    }
    
    const returnData = {};
    if (returnDate) {
        returnData.actual_return_date = returnDate;
    }
    
    try {
        await apiCall(`/loans/${loanId}/return`, {
            method: 'PUT',
            body: JSON.stringify(returnData)
        });

        showToast('Libro devuelto exitosamente!', 'success');
        closeModal('returnBookModal');
        loadBooks();
        updateStats();
    } catch (error) {
        showToast('Error al devolver libro. Intenta de nuevo.', 'error');
    }
}

function showModal(modalId) {
    document.getElementById(modalId).classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
    document.body.style.overflow = '';
    
    // Reset form if it exists
    const form = document.querySelector(`#${modalId} form`);
    if (form) {
        form.reset();
    }
}

async function addBook() {
    const form = document.getElementById('addBookForm');
    const formData = new FormData(form);
    
    const bookData = {
        title: formData.get('title'),
        author: formData.get('author'),
        isbn: formData.get('isbn') || null,
        publisher: formData.get('publisher') || null,
        publication_year: formData.get('publication_year') ? parseInt(formData.get('publication_year')) : null,
        pages: formData.get('pages') ? parseInt(formData.get('pages')) : null,
        max_loan_weeks: parseInt(formData.get('max_loan_weeks')) || 3,
        total_copies: parseInt(formData.get('total_copies')) || 1
    };

    try {
        await apiCall('/books', {
            method: 'POST',
            body: JSON.stringify(bookData)
        });

        showToast('Book added successfully!', 'success');
        closeModal('addBookModal');
        loadBooks();
    } catch (error) {
        showToast('Failed to add book. Please try again.', 'error');
    }
}

// Stats Functions
function updateStats() {
    document.getElementById('totalBooks').textContent = currentBooks.length;
    document.getElementById('activeLoans').textContent = '0'; // TODO: Implement
    document.getElementById('totalMembers').textContent = '0'; // TODO: Implement
}

// Mobile Functions
function toggleMobileMenu() {
    const drawer = document.getElementById('mobileMenu');
    const overlay = document.getElementById('mobileMenuOverlay');
    if (!drawer || !overlay) return;

    const isOpen = drawer.classList.toggle('open');
    overlay.classList.toggle('active', isOpen);
    document.body.classList.toggle('menu-open', isOpen);
}

function closeMobileMenu() {
    const drawer = document.getElementById('mobileMenu');
    const overlay = document.getElementById('mobileMenuOverlay');
    if (!drawer || !overlay) return;
    drawer.classList.remove('open');
    overlay.classList.remove('active');
    document.body.classList.remove('menu-open');
}

function isMobileMenuOpen() {
    const drawer = document.getElementById('mobileMenu');
    return drawer ? drawer.classList.contains('open') : false;
}

function toggleFabSheet() {
    const sheet = document.getElementById('fabSheet');
    const overlay = document.getElementById('fabOverlay');
    if (!sheet || !overlay) return;
    const isOpen = sheet.classList.toggle('open');
    overlay.classList.toggle('active', isOpen);
    document.body.classList.toggle('menu-open', isOpen);
}

function closeFabSheet() {
    const sheet = document.getElementById('fabSheet');
    const overlay = document.getElementById('fabOverlay');
    if (!sheet || !overlay) return;
    sheet.classList.remove('open');
    overlay.classList.remove('active');
    document.body.classList.remove('menu-open');
}

function isFabSheetOpen() {
    const sheet = document.getElementById('fabSheet');
    return sheet ? sheet.classList.contains('open') : false;
}

function applyPalette(name) {
    const palette = PALETTES[name];
    if (!palette) return;
    const root = document.documentElement;
    root.style.setProperty('--primary', palette.primary);
    root.style.setProperty('--primary-dark', palette.primaryDark);
    root.style.setProperty('--success', palette.success);
    root.style.setProperty('--background', palette.background);
    root.style.setProperty('--surface', palette.surface);
    root.style.setProperty('--text', palette.text);
    root.style.setProperty('--text-muted', palette.textMuted);
    root.style.setProperty('--border', palette.border);
    localStorage.setItem('palette', name);
}

function loadPalette() {
    const saved = localStorage.getItem('palette') || 'indigo';
    applyPalette(saved);
}

function filterBooks(type) {
    if (type === 'all') {
        displayBooks(currentBooks);
        showToast('Showing all books', 'info');
    }
}

// Utility Functions
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text ? text.replace(/[&<>"']/g, m => map[m]) : '';
}

function renderAvailability(book) {
    const total = book.total_copies || 0;
    const available = book.available_copies != null ? book.available_copies : total;
    const percent = total ? Math.max(0, Math.min(100, Math.round((available / total) * 100))) : 0;
    if (total === 0) return '';
    return `
        <div class="availability">
            <div class="availability-text">
                <span>Disponibilidad</span>
                <span>${available} / ${total}</span>
            </div>
            <div class="availability-bar">
                <div class="availability-fill" style="width: ${percent}%"></div>
            </div>
        </div>
    `;
}

function showBooksSkeleton(count = 6) {
    const container = document.getElementById('booksContainer');
    if (!container) return;
    const skeletons = Array.from({ length: count }).map(() => `
        <div class="skeleton-card">
            <div class="skeleton-line w-80 skeleton-pulse"></div>
            <div class="skeleton-line w-60 skeleton-pulse"></div>
            <div class="skeleton-line w-40 skeleton-pulse"></div>
            <div style="margin-top: 0.8rem; display: flex; gap: 0.4rem;">
                <span class="skeleton-pill skeleton-pulse"></span>
                <span class="skeleton-pill skeleton-pulse" style="width: 60px;"></span>
            </div>
        </div>
    `).join('');
    container.innerHTML = `<div class="skeleton-grid">${skeletons}</div>`;
}

// Detect mobile device
function isMobile() {
    return window.innerWidth <= 768 || /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

// Optimize for mobile performance
function optimizeForMobile() {
    if (isMobile()) {
        // Reduce animation duration on mobile
        document.documentElement.style.setProperty('--animation-duration', '0.2s');
        
        // Add touch-action for better scrolling
        document.body.style.touchAction = 'manipulation';
        
        // Prevent text selection on buttons
        const buttons = document.querySelectorAll('.btn, .btn-icon, .stat-card');
        buttons.forEach(btn => {
            btn.style.webkitUserSelect = 'none';
            btn.style.userSelect = 'none';
        });
    }
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <i class="fas fa-${getToastIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => {
            if (container.contains(toast)) {
                container.removeChild(toast);
            }
        }, 300);
    }, 4000);
}

function getToastIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Add slideOut animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);