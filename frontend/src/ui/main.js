import { createAppState } from '../application/state/app-state.js';
import { createLibraryService } from '../application/services/library-service.js';
import {
    detectLanguage,
    getLanguageLabel,
    setCurrentLanguage,
    t,
    translateStatic
} from '../domain/i18n.js';
import { matchesLoanSearch, isMobileDevice } from '../domain/library.js';
import { PALETTES } from '../domain/palettes.js';
import { createApiClient } from '../infrastructure/api/client.js';
import {
    loadLanguagePreference,
    loadPalettePreference,
    loadThemePreference,
    saveLanguagePreference,
    savePalettePreference,
    saveThemePreference
} from '../infrastructure/storage/preferences.js';
import {
    closeModal,
    showModal
} from './modals.js';
import {
    ensureToastAnimation,
    hideSearchResults,
    renderBookSearchResults,
    renderBooks,
    renderCollectionHeader,
    renderBooksLoadError,
    renderBooksSkeleton,
    renderEmployeeSearchResults,
    renderEmployeesList,
    renderImportSummary,
    renderLoansCollection,
    renderLoanBookResults,
    renderLoanSearchResults,
    renderMemberSearchResults,
    renderMembersList,
    renderStats,
    showToast
} from './renderers.js';

const state = createAppState();
const libraryService = createLibraryService(createApiClient());

function initializeApp() {
    ensureToastAnimation();

    state.language = loadLanguagePreference() || detectLanguage();
    setCurrentLanguage(state.language);
    translateStatic(document, state.language);

    state.theme = loadThemePreference();
    applyTheme(state.theme);

    state.palette = loadPalettePreference();
    applyPalette(state.palette);

    setupEventListeners();
    optimizeForMobile();
    applyView('home', { scroll: false });
    refreshAppData();
}

function setupEventListeners() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', event => {
            clearTimeout(state.searchTimeout);
            state.searchTimeout = setTimeout(() => {
                if (event.target.value.length > 2) {
                    searchBooks(event.target.value);
                } else {
                    hideSearchResults();
                }
            }, 300);
        });
    }

    document.addEventListener('touchstart', event => {
        if (event.target.classList.contains('modal')) {
            closeModal(event.target.id);
        }
        if (!event.target.closest('.search-container')) {
            hideAllSearchResults();
        }
    });

    document.addEventListener('click', event => {
        if (event.target.classList.contains('modal')) {
            closeModal(event.target.id);
        }
        if (!event.target.closest('.search-container')) {
            hideAllSearchResults();
        }
    });

    document.addEventListener('keydown', event => {
        if (event.key !== 'Escape') {
            return;
        }

        const activeModal = document.querySelector('.modal.active');
        if (activeModal) {
            closeModal(activeModal.id);
        }
    });

    let lastTouchEnd = 0;
    document.addEventListener('touchend', event => {
        const now = Date.now();
        if (now - lastTouchEnd <= 300) {
            event.preventDefault();
        }
        lastTouchEnd = now;
    }, false);
}

function hideAllSearchResults() {
    hideSearchResults();
    ['bookSearchResults', 'memberSearchResults', 'employeeSearchResults', 'loanSearchResults'].forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.style.display = 'none';
        }
    });
}

async function refreshAppData() {
    try {
        renderBooksSkeleton();
        const [books, loans, members, employees, importSummary] = await Promise.all([
            libraryService.listBooks(),
            libraryService.listLoans(),
            libraryService.listMembers(),
            libraryService.listEmployees(),
            libraryService.getImportSummary()
        ]);

        state.books = books.books || [];
        state.loans = loans.loans || [];
        state.members = members.members || [];
        state.employees = employees.employees || [];
        state.importSummary = importSummary;
        renderAll();
    } catch (error) {
        console.error('Refresh failed', error);
        renderBooksLoadError();
        showToast(t('toast.apiFailed', { message: error.message }), 'error');
    }
}

function renderAll() {
    setCurrentLanguage(state.language);
    translateStatic(document, state.language);
    renderMainCollection();
    renderStats(state);
    renderMembersList(state.members);
    renderEmployeesList(state.employees);
    renderImportSummary(state.importSummary);
    updateLanguageControls();
    renderViewState();
}

function renderMainCollection() {
    if (state.collectionMode === 'active_loans') {
        const activeLoans = state.loans.filter(loan => ['in_progress', 'overdue'].includes(loan.status));
        renderCollectionHeader('active_loans');
        renderLoansCollection(activeLoans, 'active');
        return;
    }

    if (state.collectionMode === 'overdue_loans') {
        const overdueLoans = state.loans.filter(loan => loan.status === 'overdue');
        renderCollectionHeader('overdue_loans');
        renderLoansCollection(overdueLoans, 'overdue');
        return;
    }

    renderCollectionHeader('books');
    renderBooks(state.books);
}

function renderViewState() {
    const currentView = state.currentView || 'home';

    document.querySelectorAll('[data-view]').forEach(section => {
        const views = section.dataset.view.split(/\s+/).filter(Boolean);
        section.classList.toggle('view-hidden', !views.includes(currentView));
    });

    document.querySelectorAll('[data-nav-target]').forEach(item => {
        item.classList.toggle('active', item.dataset.navTarget === currentView);
    });
    document.body.dataset.workspaceView = currentView;
}

function applyView(view, options = {}) {
    state.currentView = view;
    renderViewState();

    if (options.scroll !== false) {
        window.scrollTo({ top: 0, behavior: options.smooth === false ? 'auto' : 'smooth' });
    }
}

function navigateTo(view) {
    if (view === 'members') {
        navigateToWorkspace('members');
        return;
    }

    if (view === 'employees') {
        navigateToWorkspace('more');
        return;
    }

    navigateToWorkspace(view);
}

function navigateToWorkspace(view) {
    const allowedViews = ['home', 'catalog', 'loans', 'members', 'more'];
    const nextView = allowedViews.includes(view) ? view : 'home';

    if (nextView === 'home' || nextView === 'catalog') {
        state.collectionMode = 'books';
        renderMainCollection();
    }

    if (nextView === 'loans') {
        state.collectionMode = 'active_loans';
        renderMainCollection();
    }

    applyView(nextView);
}

async function searchBooks(query) {
    if (!query || query.length < 2) {
        hideSearchResults();
        return;
    }

    try {
        const data = await libraryService.searchBooks(query, 10);
        renderBookSearchResults(data.books || []);
    } catch (error) {
        hideSearchResults();
    }
}

function selectBook(bookId) {
    const book = state.books.find(item => item.book_id === bookId);
    if (!book) {
        return;
    }

    const input = document.getElementById('searchInput');
    if (input) {
        input.value = book.title;
    }
    state.collectionMode = 'books';
    renderCollectionHeader('books');
    renderBooks([book]);
    applyView('catalog');
    hideSearchResults();
}

function showAddBookModal() {
    showModal('addBookModal');
}

function showCreateLoanModal() {
    const today = new Date().toISOString().split('T')[0];
    const dueDate = new Date();
    dueDate.setDate(dueDate.getDate() + 21);
    const dueDateStr = dueDate.toISOString().split('T')[0];

    const loanDateInput = document.querySelector('input[name="loan_date"]');
    const dueDateInput = document.querySelector('input[name="due_date"]');
    if (loanDateInput) loanDateInput.value = today;
    if (dueDateInput) dueDateInput.value = dueDateStr;

    if (state.employees.length === 1) {
        const employee = state.employees[0];
        const employeeSearch = document.getElementById('employeeSearch');
        const employeeInput = document.querySelector('input[name="employee_id"]');
        if (employeeSearch) {
            employeeSearch.value = `${employee.first_name} ${employee.last_name}`;
        }
        if (employeeInput) {
            employeeInput.value = employee.employee_id;
        }
    }

    showModal('createLoanModal');
}

function showReturnBookModal() {
    const today = new Date().toISOString().split('T')[0];
    const returnDateInput = document.querySelector('input[name="return_date"]');
    if (returnDateInput) {
        returnDateInput.value = today;
    }
    showModal('returnBookModal');
}

async function searchActiveLoans(query) {
    const results = document.getElementById('loanSearchResults');
    if (!results) {
        return;
    }

    if (!query || query.length < 2) {
        results.style.display = 'none';
        return;
    }

    const activeLoans = state.loans.filter(loan => ['in_progress', 'overdue'].includes(loan.status));
    const filteredLoans = activeLoans.filter(loan => matchesLoanSearch(loan, query));
    renderLoanSearchResults(filteredLoans);
}

function selectLoanForReturn(loanId, displayText) {
    const loanSearch = document.getElementById('loanSearch');
    const loanIdInput = document.querySelector('input[name="loan_id"]');
    const results = document.getElementById('loanSearchResults');

    if (loanSearch) loanSearch.value = decodeURIComponent(displayText);
    if (loanIdInput) loanIdInput.value = loanId;
    if (results) results.style.display = 'none';
}

function startReturnFlow(loanId, displayText) {
    showReturnBookModal();
    selectLoanForReturn(loanId, displayText);
}

async function createLoan() {
    const form = document.getElementById('createLoanForm');
    const formData = new FormData(form);

    if (!formData.get('book_copy_id') || !formData.get('member_id') || !formData.get('loan_date') || !formData.get('due_date')) {
        showToast(t('toast.loanRequired'), 'error');
        return;
    }

    const payload = {
        book_copy_id: formData.get('book_copy_id'),
        member_id: formData.get('member_id'),
        employee_id: formData.get('employee_id') || null,
        loan_date: formData.get('loan_date'),
        due_date: formData.get('due_date')
    };

    try {
        await libraryService.createLoan(payload);
        showToast(t('toast.loanCreated'), 'success');
        closeModal('createLoanModal');
        await refreshAppData();
        navigateToWorkspace('loans');
    } catch (error) {
        showToast(error.message || t('toast.loanCreateFailed'), 'error');
    }
}

async function searchBooksForLoan(query) {
    const results = document.getElementById('bookSearchResults');
    if (!results) {
        return;
    }

    if (!query || query.length < 2) {
        results.style.display = 'none';
        return;
    }

    try {
        const data = await libraryService.searchBooks(query, 5);
        renderLoanBookResults(data.books || []);
    } catch (error) {
        results.style.display = 'none';
    }
}

function selectBookForLoan(bookCopyId, title) {
    if (!bookCopyId) {
        showToast(t('toast.bookUnavailable'), 'warning');
        return;
    }

    const search = document.getElementById('bookSearch');
    const hidden = document.querySelector('input[name="book_copy_id"]');
    const results = document.getElementById('bookSearchResults');

    if (search) search.value = decodeURIComponent(title);
    if (hidden) hidden.value = bookCopyId;
    if (results) results.style.display = 'none';
}

function startLoanFlow(bookCopyId, title) {
    showCreateLoanModal();
    selectBookForLoan(bookCopyId, title);
}

function searchEmployeesForLoan(query) {
    const results = document.getElementById('employeeSearchResults');
    if (!results) {
        return;
    }

    if (!query || query.length < 1) {
        results.style.display = 'none';
        return;
    }

    const filtered = state.employees
        .filter(employee => `${employee.first_name} ${employee.last_name}`.toLowerCase().includes(query.toLowerCase()))
        .slice(0, 5);

    renderEmployeeSearchResults(filtered);
}

function selectEmployeeForLoan(employeeId, name) {
    const search = document.getElementById('employeeSearch');
    const hidden = document.querySelector('input[name="employee_id"]');
    const results = document.getElementById('employeeSearchResults');

    if (search) search.value = decodeURIComponent(name);
    if (hidden) hidden.value = employeeId;
    if (results) results.style.display = 'none';
}

async function searchMembersForLoan(query) {
    const results = document.getElementById('memberSearchResults');
    if (!results) {
        return;
    }

    if (!query || query.length < 2) {
        results.style.display = 'none';
        return;
    }

    try {
        const data = await libraryService.autocompleteMembers(query, 5);
        renderMemberSearchResults(data.results || []);
    } catch (error) {
        results.style.display = 'none';
    }
}

function selectMemberForLoan(memberId, name) {
    const search = document.getElementById('memberSearch');
    const hidden = document.querySelector('input[name="member_id"]');
    const results = document.getElementById('memberSearchResults');

    if (search) search.value = decodeURIComponent(name);
    if (hidden) hidden.value = memberId;
    if (results) results.style.display = 'none';
}

async function returnBook() {
    const form = document.getElementById('returnBookForm');
    const formData = new FormData(form);
    const loanId = formData.get('loan_id');
    const returnDate = formData.get('return_date');

    if (!loanId) {
        showToast(t('toast.returnSelectLoan'), 'error');
        return;
    }

    const payload = {};
    if (returnDate) {
        payload.actual_return_date = returnDate;
    }

    try {
        await libraryService.returnLoan(loanId, payload);
        showToast(t('toast.returned'), 'success');
        closeModal('returnBookModal');
        await refreshAppData();
        navigateToWorkspace('loans');
    } catch (error) {
        showToast(error.message || t('toast.returnFailed'), 'error');
    }
}

async function addBook() {
    const form = document.getElementById('addBookForm');
    const formData = new FormData(form);
    const payload = {
        title: formData.get('title'),
        author: formData.get('author'),
        isbn: formData.get('isbn') || null,
        publisher: formData.get('publisher') || null,
        publication_year: formData.get('publication_year') ? parseInt(formData.get('publication_year'), 10) : null,
        pages: formData.get('pages') ? parseInt(formData.get('pages'), 10) : null,
        max_loan_weeks: parseInt(formData.get('max_loan_weeks'), 10) || 3,
        total_copies: parseInt(formData.get('total_copies'), 10) || 1
    };

    try {
        await libraryService.createBook(payload);
        showToast(t('toast.bookAdded'), 'success');
        closeModal('addBookModal');
        await refreshAppData();
        navigateToWorkspace('catalog');
    } catch (error) {
        showToast(error.message || t('toast.bookAddFailed'), 'error');
    }
}

function showAddMemberModal() {
    navigateToWorkspace('members');
    showModal('addMemberModal');
}

function showAddEmployeeModal() {
    navigateToWorkspace('more');
    showModal('addEmployeeModal');
}

async function addMember() {
    const form = document.getElementById('addMemberForm');
    const formData = new FormData(form);
    const payload = {
        first_name: formData.get('first_name'),
        last_name: formData.get('last_name'),
        email: formData.get('email') || null,
        address: formData.get('address') || null,
        phone: formData.get('phone') || null
    };

    try {
        await libraryService.createMember(payload);
        showToast(t('toast.memberAdded'), 'success');
        closeModal('addMemberModal');
        await refreshAppData();
        navigateToWorkspace('members');
    } catch (error) {
        showToast(error.message || t('toast.memberAddFailed'), 'error');
    }
}

async function addEmployee() {
    const form = document.getElementById('addEmployeeForm');
    const formData = new FormData(form);
    const payload = {
        first_name: formData.get('first_name'),
        last_name: formData.get('last_name'),
        position: formData.get('position')
    };

    try {
        await libraryService.createEmployee(payload);
        showToast(t('toast.employeeAdded'), 'success');
        closeModal('addEmployeeModal');
        await refreshAppData();
        navigateToWorkspace('more');
    } catch (error) {
        showToast(error.message || t('toast.employeeAddFailed'), 'error');
    }
}

function toggleTheme() {
    setTheme(state.theme === 'light' ? 'dark' : 'light');
}

function setTheme(theme) {
    const nextTheme = theme === 'dark' ? 'dark' : 'light';
    state.theme = nextTheme;
    applyTheme(nextTheme);
    saveThemePreference(nextTheme);
    showToast(t('toast.themeChanged', { theme: t(`theme.${nextTheme}`) }), 'info');
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    updateThemeControls();
    updateThemeMeta(theme);
}

function updateThemeControls() {
    document.querySelectorAll('[data-theme-option]').forEach(button => {
        button.classList.toggle('active', button.dataset.themeOption === state.theme);
    });
}

function updateThemeMeta(theme) {
    const metaTheme = document.querySelector('meta[name="theme-color"]');
    if (!metaTheme) {
        return;
    }
    metaTheme.setAttribute('content', theme === 'dark' ? '#08101f' : '#2563eb');
}

function applyPalette(name) {
    const palette = PALETTES[name];
    if (!palette) {
        return;
    }

    state.palette = name;
    const root = document.documentElement;
    root.style.setProperty('--primary', palette.primary);
    root.style.setProperty('--primary-dark', palette.primaryDark);
    root.style.setProperty('--success', palette.success);
    savePalettePreference(name);
    updatePaletteControls();
}

function updatePaletteControls() {
    document.querySelectorAll('.palette-chip').forEach(button => {
        const onclick = button.getAttribute('onclick') || '';
        button.classList.toggle('active', onclick.includes(`'${state.palette}'`));
    });
}

function setLanguage(language) {
    state.language = setCurrentLanguage(language);
    saveLanguagePreference(state.language);
    translateStatic(document, state.language);
    renderAll();
    showToast(t('toast.languageChanged', { language: getLanguageLabel(state.language) }), 'info');
}

function updateLanguageControls() {
    document.querySelectorAll('[data-language-option]').forEach(button => {
        button.classList.toggle('active', button.dataset.languageOption === state.language);
    });
}

function filterBooks(type) {
    if (type !== 'all') {
        return;
    }
    state.collectionMode = 'books';
    state.currentView = 'catalog';
    renderViewState();
    renderMainCollection();
    showToast(t('toast.showingBooks'), 'info');
}

function filterLoans(mode) {
    state.collectionMode = mode === 'overdue' ? 'overdue_loans' : 'active_loans';
    state.currentView = 'loans';
    renderViewState();
    renderMainCollection();
    const message = mode === 'overdue'
        ? t('toast.showingOverdueLoans')
        : t('toast.showingOpenLoans');
    showToast(message, 'info');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function optimizeForMobile() {
    if (!isMobileDevice()) {
        return;
    }

    document.documentElement.style.setProperty('--animation-duration', '0.2s');
    document.body.style.touchAction = 'manipulation';

    document.querySelectorAll('.btn, .btn-icon, .kpi-card, .action-tile').forEach(button => {
        button.style.webkitUserSelect = 'none';
        button.style.userSelect = 'none';
    });
}

window.LibraryUI = {
    addBook,
    addEmployee,
    addMember,
    applyPalette,
    setTheme,
    closeModal,
    createLoan,
    filterBooks,
    filterLoans,
    loadBooks: refreshAppData,
    navigateTo,
    navigateToWorkspace,
    refreshAppData,
    returnBook,
    startReturnFlow,
    searchActiveLoans,
    searchBooks,
    searchBooksForLoan,
    searchEmployeesForLoan,
    searchMembersForLoan,
    setLanguage,
    selectBook,
    selectBookForLoan,
    selectEmployeeForLoan,
    selectLoanForReturn,
    selectMemberForLoan,
    showAddBookModal,
    showAddEmployeeModal,
    showAddMemberModal,
    showCreateLoanModal,
    showReturnBookModal,
    startLoanFlow,
    toggleTheme
};

document.addEventListener('DOMContentLoaded', initializeApp);
