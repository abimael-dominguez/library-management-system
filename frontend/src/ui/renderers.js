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

export function renderBooks(books) {
    const container = document.getElementById('booksContainer');
    if (!container) {
        return;
    }

    if (books.length === 0) {
        container.innerHTML = renderEmptyState('book', 'No books found', 'Try a broader search or add a new title to keep the catalog moving.');
        return;
    }

    container.innerHTML = books.map(book => `
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
}

export function renderLoansCollection(loans, mode = 'active') {
    const container = document.getElementById('booksContainer');
    if (!container) {
        return;
    }

    if (loans.length === 0) {
        container.innerHTML = mode === 'overdue'
            ? renderEmptyState('shield-heart', 'No overdue loans', 'Everything is on track right now. No active loans need follow-up.')
            : renderEmptyState('receipt', 'No active loans', 'There are no books in circulation yet. New loans will appear here.');
        return;
    }

    container.innerHTML = loans.map(loan => {
        const displayText = encodeURIComponent(`${loan.book_title || loan.loan_id} · ${loan.member_name || 'No member'}`);
        const isOverdue = loan.status === 'overdue';
        return `
            <div class="loan-card ${loan.status === 'overdue' ? 'loan-card-overdue' : ''}">
                <div class="loan-card-header">
                    <div>
                        <h3 class="book-title">${escapeHtml(loan.book_title || 'Loan')}</h3>
                        <p class="book-author">${escapeHtml(loan.book_author || 'No author')}</p>
                    </div>
                    <span class="badge ${loan.status === 'overdue' ? 'badge-warning' : 'badge-primary'}">${getStatusLabel(loan.status)}</span>
                </div>
                <div class="loan-hero-strip ${isOverdue ? 'loan-hero-strip-overdue' : ''}">
                    <div class="loan-hero-block">
                        <span class="loan-hero-label">Borrower</span>
                        <strong>${escapeHtml(loan.member_name || 'No member')}</strong>
                    </div>
                    <div class="loan-hero-block">
                        <span class="loan-hero-label">Processed by</span>
                        <strong>${escapeHtml(loan.employee_name || 'No employee')}</strong>
                    </div>
                </div>
                <div class="loan-timeline">
                    <div class="loan-timeline-item">
                        <span>Loan date</span>
                        <strong>${escapeHtml(loan.loan_date || 'N/A')}</strong>
                    </div>
                    <div class="loan-timeline-divider"></div>
                    <div class="loan-timeline-item">
                        <span>Due date</span>
                        <strong>${escapeHtml(loan.due_date || 'N/A')}</strong>
                    </div>
                </div>
                <div class="loan-meta-grid">
                    <div class="loan-meta-item">
                        <span class="loan-meta-label">Copy status</span>
                        <strong>${isOverdue ? 'Attention needed' : 'Circulating'}</strong>
                    </div>
                    <div class="loan-meta-item">
                        <span class="loan-meta-label">Loan ID</span>
                        <strong>${escapeHtml(loan.loan_id || 'N/A')}</strong>
                    </div>
                </div>
                <div class="loan-card-footer">
                    <div class="book-meta">
                        <span class="badge badge-secondary">${escapeHtml(loan.book_author || 'Unknown author')}</span>
                        <span class="badge ${isOverdue ? 'badge-warning-soft' : 'badge-primary-soft'}">${isOverdue ? 'Priority follow-up' : 'On schedule'}</span>
                    </div>
                    <div class="loan-card-actions">
                        <button class="btn btn-outline" onclick="window.LibraryUI.startReturnFlow('${loan.loan_id}', '${displayText}')">
                            <i class="fas fa-undo"></i> Register return
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

export function renderBookSearchResults(books) {
    const resultsContainer = document.getElementById('searchResults');
    if (!resultsContainer) {
        return;
    }

    if (books.length === 0) {
        resultsContainer.innerHTML = '<div class="search-result-item">No books found</div>';
    } else {
        resultsContainer.innerHTML = books.map(book => `
            <div class="search-result-item" onclick="window.LibraryUI.selectBook('${book.book_id}')">
                <div style="font-weight: 500;">${escapeHtml(book.title)}</div>
                <div style="color: var(--text-muted); font-size: 0.875rem;">by ${escapeHtml(book.author)}</div>
            </div>
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
        resultsContainer.innerHTML = '<div class="search-result-item">No active loans found</div>';
    } else {
        resultsContainer.innerHTML = loans.map(loan => {
            const label = encodeURIComponent(`${loan.book_title || loan.loan_id} · ${loan.member_name || 'No member'}`);
            return `
                <div class="search-result-item" onclick="window.LibraryUI.selectLoanForReturn('${loan.loan_id}', '${label}')">
                    <div style="font-weight: 500;">${escapeHtml(loan.book_title || 'Loan')}</div>
                    <div style="color: var(--text-muted); font-size: 0.875rem;">${escapeHtml(loan.member_name || 'No member')} · ${getStatusLabel(loan.status)} · Due: ${loan.due_date}</div>
                </div>
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
        resultsContainer.innerHTML = '<div class="search-result-item">No books found</div>';
    } else {
        resultsContainer.innerHTML = books.map(book => `
            <div class="search-result-item" onclick="window.LibraryUI.selectBookForLoan('${book.first_available_copy_id || ''}', '${encodeURIComponent(book.title || '')}')">
                <div style="font-weight: 500;">${escapeHtml(book.title)}</div>
                <div style="color: var(--text-muted); font-size: 0.875rem;">by ${escapeHtml(book.author)} · ${book.available_copies || 0} available</div>
            </div>
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
        resultsContainer.innerHTML = '<div class="search-result-item">No members found</div>';
    } else {
        resultsContainer.innerHTML = members.map(member => `
            <div class="search-result-item" onclick="window.LibraryUI.selectMemberForLoan('${member.id}', '${encodeURIComponent(member.name || '')}')">
                <div style="font-weight: 500;">${escapeHtml(member.name)}</div>
            </div>
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
        resultsContainer.innerHTML = '<div class="search-result-item">No employees found</div>';
    } else {
        resultsContainer.innerHTML = employees.map(employee => `
            <div class="search-result-item" onclick="window.LibraryUI.selectEmployeeForLoan('${employee.employee_id}', '${encodeURIComponent(`${employee.first_name} ${employee.last_name}`)}')">
                <div style="font-weight: 500;">${escapeHtml(employee.first_name)} ${escapeHtml(employee.last_name)}</div>
                <div style="color: var(--text-muted); font-size: 0.875rem;">${escapeHtml(employee.position || 'Staff')}</div>
            </div>
        `).join('');
    }

    resultsContainer.style.display = 'block';
}

export function renderStats(state) {
    const totalBooks = document.getElementById('totalBooks');
    const activeLoans = document.getElementById('activeLoans');
    const totalMembers = document.getElementById('totalMembers');
    const overdueLoans = document.getElementById('overdueLoans');

    if (totalBooks) totalBooks.textContent = state.books.length;
    if (activeLoans) activeLoans.textContent = state.loans.filter(loan => loan.status === 'in_progress').length;
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
        eyebrow.textContent = 'Circulation';
        title.textContent = 'Loaned books';
        description.textContent = 'Operational list of active loans with quick access to returns.';
        return;
    }

    if (mode === 'overdue_loans') {
        eyebrow.textContent = 'Follow-up';
        title.textContent = 'Overdue books';
        description.textContent = 'Loans that need immediate attention because they are overdue.';
        return;
    }

    eyebrow.textContent = 'Collection';
    title.textContent = 'Available books';
    description.textContent = 'Browse the catalog and review availability by title.';
}

export function renderMembersList(members) {
    const container = document.getElementById('membersList');
    if (!container) {
        return;
    }

    if (members.length === 0) {
        container.innerHTML = '<div class="mini-empty">No members yet. Register your first borrower to start tracking circulation.</div>';
        return;
    }

    container.innerHTML = members.slice(0, 6).map(member => `
        <div class="mini-list-item">
            <div>
                <strong>${escapeHtml(member.first_name)} ${escapeHtml(member.last_name)}</strong>
                <p>${escapeHtml(member.email)}</p>
            </div>
            <span class="badge badge-secondary">${escapeHtml(member.status)}</span>
        </div>
    `).join('');
}

export function renderEmployeesList(employees) {
    const container = document.getElementById('employeesList');
    if (!container) {
        return;
    }

    if (employees.length === 0) {
        container.innerHTML = '<div class="mini-empty">No employees yet. Add staff members so loan processing stays traceable.</div>';
        return;
    }

    container.innerHTML = employees.slice(0, 6).map(employee => `
        <div class="mini-list-item">
            <div>
                <strong>${escapeHtml(employee.first_name)} ${escapeHtml(employee.last_name)}</strong>
                <p>${escapeHtml(employee.position || 'Staff')}</p>
            </div>
            <span class="badge badge-primary">On file</span>
        </div>
    `).join('');
}

export function renderImportSummary(importSummary) {
    if (!importSummary) {
        return;
    }

    const text = document.getElementById('importSummaryText');
    const warnings = document.getElementById('importWarnings');
    const copies = document.getElementById('importCopies');
    const card = document.getElementById('importSummaryCard');
    const source = document.getElementById('importSource');
    const status = document.getElementById('importStatusLabel');

    if (!text || !warnings || !copies || !card || !source || !status) {
        return;
    }

    const sourcePath = importSummary.csv_path || '';
    const shortSource = sourcePath.split('/').filter(Boolean).pop() || 'No file';
    const warningCount = importSummary.warnings || 0;
    text.textContent = warningCount > 0
        ? `The last sync completed with ${warningCount} warning${warningCount === 1 ? '' : 's'}. Review rows with missing member or date fields before the next import.`
        : 'The last sync completed cleanly. Your spreadsheet import is ready to use.';
    warnings.textContent = importSummary.warnings || 0;
    copies.textContent = importSummary.copies || 0;
    source.textContent = shortSource;
    status.textContent = warningCount > 0 ? 'Needs review' : 'Healthy';
    card.classList.toggle('has-warning', warningCount > 0);
}

export function renderBooksSkeleton(count = 6) {
    const container = document.getElementById('booksContainer');
    if (!container) {
        return;
    }

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

export function renderBooksLoadError() {
    const container = document.getElementById('booksContainer');
    if (container) {
        container.innerHTML = renderEmptyState('triangle-exclamation', 'Failed to load books', 'Refresh the catalog or check whether the backend is available.');
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
