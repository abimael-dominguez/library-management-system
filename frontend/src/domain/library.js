export function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text ? String(text).replace(/[&<>"']/g, match => map[match]) : '';
}

export function renderAvailability(book) {
    const total = book.total_copies || 0;
    const available = book.available_copies != null ? book.available_copies : total;
    const percent = total ? Math.max(0, Math.min(100, Math.round((available / total) * 100))) : 0;

    if (total === 0) {
        return '';
    }

    return `
        <div class="availability">
            <div class="availability-text">
                <span>Availability</span>
                <span>${available} / ${total}</span>
            </div>
            <div class="availability-bar">
                <div class="availability-fill" style="width: ${percent}%"></div>
            </div>
        </div>
    `;
}

export function getStatusLabel(status) {
    const labels = {
        in_progress: 'Active loan',
        returned: 'Returned',
        overdue: 'Overdue',
        available: 'Available',
        loaned: 'Loaned',
        damaged: 'Damaged',
        lost: 'Lost'
    };
    return labels[status] || status;
}

export function matchesLoanSearch(loan, query) {
    const term = query.toLowerCase();
    return [
        loan.loan_id,
        loan.book_title,
        loan.book_author,
        loan.member_name,
        loan.employee_name
    ].some(value => (value || '').toLowerCase().includes(term));
}

export function isMobileDevice() {
    return window.innerWidth <= 768 || /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}
