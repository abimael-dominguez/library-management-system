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
    buildBookPayload,
    buildCreateLoanPayload,
    buildEmployeePayload,
    buildMemberPayload,
    buildReturnPayload,
    dateInputValue
} from './form-payloads.js';
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
import {
    getCollectionModeForWorkspaceView,
    renderWorkspaceView,
    resolveWorkspaceView,
    scrollWorkspaceToTop
} from './workspace.js';

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
            libraryService.listLoans({ status: 'open' }),
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
    renderWorkspaceView(state.currentView || 'home');
}

function applyView(view, options = {}) {
    state.currentView = resolveWorkspaceView(view);
    renderViewState();
    scrollWorkspaceToTop({ scroll: options.scroll !== false, smooth: options.smooth !== false });
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
    const nextView = resolveWorkspaceView(view);
    const nextCollectionMode = getCollectionModeForWorkspaceView(nextView, state.collectionMode);
    if (nextCollectionMode !== state.collectionMode) {
        state.collectionMode = nextCollectionMode;
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
    const loanDateInput = document.querySelector('input[name="loan_date"]');
    const dueDateInput = document.querySelector('input[name="due_date"]');
    if (loanDateInput) loanDateInput.value = dateInputValue();
    if (dueDateInput) dueDateInput.value = dateInputValue(21);

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
    const returnDateInput = document.querySelector('input[name="return_date"]');
    if (returnDateInput) {
        returnDateInput.value = dateInputValue();
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
    const { isValid, payload } = buildCreateLoanPayload();
    if (!isValid) {
        showToast(t('toast.loanRequired'), 'error');
        return;
    }

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
    const { isValid, loanId, payload } = buildReturnPayload();
    if (!isValid) {
        showToast(t('toast.returnSelectLoan'), 'error');
        return;
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
    const payload = buildBookPayload();
    if (!payload) {
        showToast(t('toast.bookAddFailed'), 'error');
        return;
    }

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
    const payload = buildMemberPayload();
    if (!payload) {
        showToast(t('toast.memberAddFailed'), 'error');
        return;
    }

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
    const payload = buildEmployeePayload();
    if (!payload) {
        showToast(t('toast.employeeAddFailed'), 'error');
        return;
    }

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
