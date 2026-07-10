import { t } from '../domain/i18n.js';
import { escapeHtml, getStatusLabel, renderAvailability } from '../domain/library.js';

function renderEmptyState(icon, title, copy) {
    return `
        <div class="empty-state">
            <div class="empty-state-icon">
                <i class="fas fa-${icon}"></i>
            </div>
            <h3>${escapeHtml(title)}</h3>
            <p>${escapeHtml(copy)}</p>
        </div>
    `;
}

function encodeDisplayText(value) {
    return encodeURIComponent(value || '');
}

export function renderBooks(books) {
    const container = document.getElementById('booksContainer');
    if (!container) {
        return;
    }

    container.className = 'catalog-list';

    if (books.length === 0) {
        container.innerHTML = renderEmptyState('book', t('empty.booksTitle'), t('empty.booksCopy'));
        return;
    }

    container.innerHTML = books.map(book => {
        const availableCopyId = book.first_available_copy_id || '';
        const canLoan = Boolean(availableCopyId);
        const title = book.title || t('app.empty');
        const author = book.author || t('app.empty');
        return `
            <article class="book-row">
                <div class="row-icon">
                    <i class="fas fa-book"></i>
                </div>
                <div class="row-main">
                    <div class="row-title-line">
                        <h3>${escapeHtml(title)}</h3>
                        <span class="availability-badge ${canLoan ? 'available' : 'unavailable'}">${book.available_copies || 0}/${book.total_copies || 0}</span>
                    </div>
                    <p>${escapeHtml(t('book.byAuthor', { author }))}</p>
                    <div class="row-meta">
                        ${book.isbn ? `<span>${escapeHtml(t('book.isbn'))}: ${escapeHtml(book.isbn)}</span>` : ''}
                        ${book.pages ? `<span>${escapeHtml(t('book.pages'))}: ${book.pages}</span>` : ''}
                        <span>${escapeHtml(t('book.copies', { count: book.total_copies || 0 }))}</span>
                        <span>${escapeHtml(t('book.loanWeeks', { count: book.max_loan_weeks || 3 }))}</span>
                    </div>
                    ${renderAvailability(book)}
                </div>
                <div class="row-actions">
                    <button type="button" class="btn btn-primary compact" ${canLoan ? '' : 'disabled'} onclick="window.LibraryUI.startLoanFlow('${availableCopyId}', '${encodeDisplayText(title)}')">
                        <i class="fas fa-book-reader"></i>
                        <span>${escapeHtml(t('actions.createLoan'))}</span>
                    </button>
                </div>
            </article>
        `;
    }).join('');
}

export function renderLoansCollection(loans, mode = 'active') {
    const container = document.getElementById('booksContainer');
    if (!container) {
        return;
    }

    container.className = 'loan-list';

    if (loans.length === 0) {
        container.innerHTML = mode === 'overdue'
            ? renderEmptyState('shield-heart', t('empty.overdueTitle'), t('empty.overdueCopy'))
            : renderEmptyState('receipt', t('empty.openLoansTitle'), t('empty.openLoansCopy'));
        return;
    }

    container.innerHTML = loans.map(loan => {
        const title = loan.book_title || t('app.empty');
        const displayText = encodeDisplayText(`${title} · ${loan.member_name || t('loan.noMember')}`);
        const isOverdue = loan.status === 'overdue';
        return `
            <article class="loan-row ${isOverdue ? 'is-overdue' : ''}">
                <div class="row-icon">
                    <i class="fas fa-${isOverdue ? 'hourglass-half' : 'book-reader'}"></i>
                </div>
                <div class="row-main">
                    <div class="row-title-line">
                        <h3>${escapeHtml(title)}</h3>
                        <span class="badge ${isOverdue ? 'badge-warning' : 'badge-primary'}">${escapeHtml(getStatusLabel(loan.status))}</span>
                    </div>
                    <p>${escapeHtml(loan.book_author || t('app.empty'))}</p>
                    <div class="loan-facts">
                        <span><strong>${escapeHtml(t('loan.borrower'))}</strong> ${escapeHtml(loan.member_name || t('loan.noMember'))}</span>
                        <span><strong>${escapeHtml(t('loan.dueDate'))}</strong> ${escapeHtml(loan.due_date || 'N/A')}</span>
                        <span><strong>${escapeHtml(t('loan.processedBy'))}</strong> ${escapeHtml(loan.employee_name || t('loan.noEmployee'))}</span>
                    </div>
                </div>
                <div class="row-actions">
                    <button type="button" class="btn ${isOverdue ? 'btn-warning' : 'btn-success'} compact" onclick="window.LibraryUI.startReturnFlow('${loan.loan_id}', '${displayText}')">
                        <i class="fas fa-arrow-rotate-left"></i>
                        <span>${escapeHtml(t('actions.registerReturn'))}</span>
                    </button>
                </div>
            </article>
        `;
    }).join('');
}

export function renderBookSearchResults(books) {
    const resultsContainer = document.getElementById('searchResults');
    if (!resultsContainer) {
        return;
    }

    if (books.length === 0) {
        resultsContainer.innerHTML = `<div class="search-result-item">${escapeHtml(t('empty.searchBooks'))}</div>`;
    } else {
        resultsContainer.innerHTML = books.map(book => `
            <button type="button" class="search-result-item" onclick="window.LibraryUI.selectBook('${book.book_id}')">
                <strong>${escapeHtml(book.title)}</strong>
                <span>${escapeHtml(t('book.byAuthor', { author: book.author }))} · ${escapeHtml(t('book.availableCount', { available: book.available_copies || 0 }))}</span>
            </button>
        `).join('');
    }

    resultsContainer.style.display = 'block';
}

export function hideSearchResults() {
    const resultsContainer = document.getElementById('searchResults');
    if (resultsContainer) {
        resultsContainer.style.display = 'none';
    }
}

export function renderLoanSearchResults(loans) {
    const resultsContainer = document.getElementById('loanSearchResults');
    if (!resultsContainer) {
        return;
    }

    if (loans.length === 0) {
        resultsContainer.innerHTML = `<div class="search-result-item">${escapeHtml(t('empty.searchLoans'))}</div>`;
    } else {
        resultsContainer.innerHTML = loans.map(loan => {
            const label = encodeDisplayText(`${loan.book_title || loan.loan_id} · ${loan.member_name || t('loan.noMember')}`);
            return `
                <button type="button" class="search-result-item" onclick="window.LibraryUI.selectLoanForReturn('${loan.loan_id}', '${label}')">
                    <strong>${escapeHtml(loan.book_title || t('app.empty'))}</strong>
                    <span>${escapeHtml(loan.member_name || t('loan.noMember'))} · ${escapeHtml(getStatusLabel(loan.status))} · ${escapeHtml(t('loan.dueDate'))}: ${escapeHtml(loan.due_date || 'N/A')}</span>
                </button>
            `;
        }).join('');
    }

    resultsContainer.style.display = 'block';
}

export function renderLoanBookResults(books) {
    const resultsContainer = document.getElementById('bookSearchResults');
    if (!resultsContainer) {
        return;
    }

    if (books.length === 0) {
        resultsContainer.innerHTML = `<div class="search-result-item">${escapeHtml(t('empty.searchBooks'))}</div>`;
    } else {
        resultsContainer.innerHTML = books.map(book => `
            <button type="button" class="search-result-item" onclick="window.LibraryUI.selectBookForLoan('${book.first_available_copy_id || ''}', '${encodeDisplayText(book.title || '')}')">
                <strong>${escapeHtml(book.title)}</strong>
                <span>${escapeHtml(t('book.byAuthor', { author: book.author }))} · ${escapeHtml(t('book.availableCount', { available: book.available_copies || 0 }))}</span>
            </button>
        `).join('');
    }

    resultsContainer.style.display = 'block';
}

export function renderMemberSearchResults(members) {
    const resultsContainer = document.getElementById('memberSearchResults');
    if (!resultsContainer) {
        return;
    }

    if (members.length === 0) {
        resultsContainer.innerHTML = `<div class="search-result-item">${escapeHtml(t('empty.searchMembers'))}</div>`;
    } else {
        resultsContainer.innerHTML = members.map(member => `
            <button type="button" class="search-result-item" onclick="window.LibraryUI.selectMemberForLoan('${member.id}', '${encodeDisplayText(member.name || '')}')">
                <strong>${escapeHtml(member.name)}</strong>
            </button>
        `).join('');
    }

    resultsContainer.style.display = 'block';
}

export function renderEmployeeSearchResults(employees) {
    const resultsContainer = document.getElementById('employeeSearchResults');
    if (!resultsContainer) {
        return;
    }

    if (employees.length === 0) {
        resultsContainer.innerHTML = `<div class="search-result-item">${escapeHtml(t('empty.searchEmployees'))}</div>`;
    } else {
        resultsContainer.innerHTML = employees.map(employee => {
            const name = `${employee.first_name} ${employee.last_name}`;
            return `
                <button type="button" class="search-result-item" onclick="window.LibraryUI.selectEmployeeForLoan('${employee.employee_id}', '${encodeDisplayText(name)}')">
                    <strong>${escapeHtml(name)}</strong>
                    <span>${escapeHtml(employee.position || t('app.empty'))}</span>
                </button>
            `;
        }).join('');
    }

    resultsContainer.style.display = 'block';
}

export function renderStats(state) {
    const totalBooks = document.getElementById('totalBooks');
    const activeLoans = document.getElementById('activeLoans');
    const totalMembers = document.getElementById('totalMembers');
    const overdueLoans = document.getElementById('overdueLoans');

    if (totalBooks) totalBooks.textContent = state.books.length;
    if (activeLoans) activeLoans.textContent = state.loans.filter(loan => ['in_progress', 'overdue'].includes(loan.status)).length;
    if (totalMembers) totalMembers.textContent = state.members.length;
    if (overdueLoans) overdueLoans.textContent = state.loans.filter(loan => loan.status === 'overdue').length;
}

export function renderCollectionHeader(mode = 'books') {
    const eyebrow = document.getElementById('collectionEyebrow');
    const title = document.getElementById('collectionTitle');
    const description = document.getElementById('collectionDescription');

    if (!eyebrow || !title || !description) {
        return;
    }

    if (mode === 'active_loans') {
        eyebrow.textContent = t('sections.loansEyebrow');
        title.textContent = t('sections.loansTitle');
        description.textContent = t('sections.loansDescription');
        return;
    }

    if (mode === 'overdue_loans') {
        eyebrow.textContent = t('sections.overdueEyebrow');
        title.textContent = t('sections.overdueTitle');
        description.textContent = t('sections.overdueDescription');
        return;
    }

    eyebrow.textContent = t('sections.catalogEyebrow');
    title.textContent = t('sections.catalogTitle');
    description.textContent = t('sections.catalogDescription');
}

export function renderMembersList(members) {
    const container = document.getElementById('membersList');
    if (!container) {
        return;
    }

    if (members.length === 0) {
        container.innerHTML = `<div class="mini-empty">${escapeHtml(t('empty.members'))}</div>`;
        return;
    }

    container.innerHTML = members.map(member => `
        <article class="directory-row">
            <div class="avatar">${escapeHtml((member.first_name || '?').slice(0, 1))}</div>
            <div>
                <strong>${escapeHtml(member.first_name)} ${escapeHtml(member.last_name)}</strong>
                <p>${escapeHtml(member.email || member.phone || t('app.empty'))}</p>
            </div>
            <span class="badge badge-secondary">${escapeHtml(getStatusLabel(member.status))}</span>
        </article>
    `).join('');
}

export function renderEmployeesList(employees) {
    const container = document.getElementById('employeesList');
    if (!container) {
        return;
    }

    if (employees.length === 0) {
        container.innerHTML = `<div class="mini-empty">${escapeHtml(t('empty.employees'))}</div>`;
        return;
    }

    container.innerHTML = employees.map(employee => `
        <article class="directory-row">
            <div class="avatar">${escapeHtml((employee.first_name || '?').slice(0, 1))}</div>
            <div>
                <strong>${escapeHtml(employee.first_name)} ${escapeHtml(employee.last_name)}</strong>
                <p>${escapeHtml(employee.position || t('app.empty'))}</p>
            </div>
            <span class="badge badge-primary">${escapeHtml(t('status.active'))}</span>
        </article>
    `).join('');
}

export function renderImportSummary(importSummary) {
    if (!importSummary) {
        return;
    }

    const text = document.getElementById('importSummaryText');
    const warnings = document.getElementById('importWarnings');
    const errors = document.getElementById('importErrors');
    const copies = document.getElementById('importCopies');
    const card = document.getElementById('importSummaryCard');
    const source = document.getElementById('importSource');
    const status = document.getElementById('importStatusLabel');
    const dataAlert = document.getElementById('dataAlert');
    const dataAlertText = document.getElementById('dataAlertText');
    const syncTexts = [
        document.getElementById('syncStatusText'),
        document.getElementById('mobileSyncStatusText')
    ].filter(Boolean);
    const syncDots = document.querySelectorAll('.sync-dot');

    if (!text || !warnings || !errors || !copies || !card || !source || !status) {
        return;
    }

    const sourcePath = importSummary.csv_path || '';
    const shortSource = sourcePath.split('/').filter(Boolean).pop() || 'No file';
    const warningCount = importSummary.warnings || 0;
    const errorCount = importSummary.errors || 0;
    const hasWarnings = warningCount > 0;
    const hasErrors = errorCount > 0;

    text.textContent = hasErrors
        ? t('import.errorText', { count: errorCount })
        : hasWarnings
        ? t('import.warningText', { count: warningCount })
        : t('import.cleanText');
    warnings.textContent = warningCount;
    errors.textContent = errorCount;
    copies.textContent = importSummary.copies || 0;
    source.textContent = shortSource;
    status.textContent = hasErrors ? t('import.blocked') : hasWarnings ? t('import.needsReview') : t('import.healthy');
    card.classList.toggle('has-warning', hasWarnings);
    card.classList.toggle('has-error', hasErrors);

    if (dataAlert && dataAlertText) {
        dataAlert.classList.toggle('is-hidden', !hasWarnings && !hasErrors);
        dataAlertText.textContent = hasErrors
            ? t('workspace.syncError', { count: errorCount })
            : t('workspace.syncWarning', { count: warningCount });
    }

    syncTexts.forEach(element => {
        element.textContent = hasErrors
            ? t('workspace.syncError', { count: errorCount })
            : hasWarnings
            ? t('workspace.syncWarning', { count: warningCount })
            : t('workspace.syncHealthy');
    });
    syncDots.forEach(element => {
        element.classList.toggle('has-warning', hasWarnings || hasErrors);
    });
}

export function renderBooksSkeleton(count = 6) {
    const container = document.getElementById('booksContainer');
    if (!container) {
        return;
    }

    container.className = 'catalog-list';
    const skeletons = Array.from({ length: count }).map(() => `
        <div class="skeleton-row">
            <span class="skeleton-avatar skeleton-pulse"></span>
            <div class="skeleton-copy">
                <span class="skeleton-line w-80 skeleton-pulse"></span>
                <span class="skeleton-line w-60 skeleton-pulse"></span>
                <span class="skeleton-line w-40 skeleton-pulse"></span>
            </div>
        </div>
    `).join('');

    container.innerHTML = skeletons;
}

export function renderBooksLoadError() {
    const container = document.getElementById('booksContainer');
    if (container) {
        container.innerHTML = renderEmptyState('triangle-exclamation', t('error.loadBooksTitle'), t('error.loadBooksCopy'));
    }
}

export function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) {
        return;
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas fa-${getToastIcon(type)}"></i>
            <span>${escapeHtml(message)}</span>
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

export function ensureToastAnimation() {
    if (document.getElementById('toast-slide-out-style')) {
        return;
    }

    const style = document.createElement('style');
    style.id = 'toast-slide-out-style';
    style.textContent = `
        @keyframes slideOut {
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}
