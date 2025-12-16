// LMS Frontend Application
class LMSApp {
    constructor() {
        this.apiUrl = this.getApiUrl();
        this.init();
    }

    getApiUrl() {
        // For local development
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:3000';
        }
        // For production, this should be set via environment or config
        return 'https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/dev';
    }

    init() {
        this.setupEventListeners();
        this.loadRecentActivity();
    }

    setupEventListeners() {
        // Book search autocomplete
        const bookSearch = document.getElementById('bookSearch');
        if (bookSearch) {
            bookSearch.addEventListener('input', this.debounce((e) => {
                this.searchBooks(e.target.value);
            }, 300));

            bookSearch.addEventListener('blur', () => {
                setTimeout(() => {
                    document.getElementById('bookResults').style.display = 'none';
                }, 200);
            });
        }

        // Member search autocomplete
        const memberSearch = document.getElementById('memberSearch');
        if (memberSearch) {
            memberSearch.addEventListener('input', this.debounce((e) => {
                this.searchMembers(e.target.value);
            }, 300));

            memberSearch.addEventListener('blur', () => {
                setTimeout(() => {
                    document.getElementById('memberResults').style.display = 'none';
                }, 200);
            });
        }
    }

    async searchBooks(query) {
        if (query.length < 2) {
            document.getElementById('bookResults').style.display = 'none';
            return;
        }

        try {
            const response = await fetch(`${this.apiUrl}/autocomplete?q=${encodeURIComponent(query)}&type=book&limit=5`);
            const data = await response.json();
            
            this.displayBookResults(data.results || []);
        } catch (error) {
            console.error('Error searching books:', error);
        }
    }

    async searchMembers(query) {
        if (query.length < 2) {
            document.getElementById('memberResults').style.display = 'none';
            return;
        }

        try {
            const response = await fetch(`${this.apiUrl}/autocomplete?q=${encodeURIComponent(query)}&type=member&limit=5`);
            const data = await response.json();
            
            this.displayMemberResults(data.results || []);
        } catch (error) {
            console.error('Error searching members:', error);
        }
    }

    displayBookResults(results) {
        const resultsDiv = document.getElementById('bookResults');
        
        if (results.length === 0) {
            resultsDiv.style.display = 'none';
            return;
        }

        resultsDiv.innerHTML = results.map(book => `
            <div class="autocomplete-item" onclick="app.selectBook('${book.book_id}', '${book.title}')">
                <div class="fw-bold">${book.title}</div>
                <div class="text-muted small">${book.author} - ${book.isbn}</div>
            </div>
        `).join('');
        
        resultsDiv.style.display = 'block';
    }

    displayMemberResults(results) {
        const resultsDiv = document.getElementById('memberResults');
        
        if (results.length === 0) {
            resultsDiv.style.display = 'none';
            return;
        }

        resultsDiv.innerHTML = results.map(member => `
            <div class="autocomplete-item" onclick="app.selectMember('${member.member_id}', '${member.first_name} ${member.last_name}')">
                <div class="fw-bold">${member.first_name} ${member.last_name}</div>
                <div class="text-muted small">${member.email}</div>
            </div>
        `).join('');
        
        resultsDiv.style.display = 'block';
    }

    selectBook(bookId, title) {
        document.getElementById('bookSearch').value = title;
        document.getElementById('bookResults').style.display = 'none';
        console.log('Selected book:', bookId, title);
    }

    selectMember(memberId, name) {
        document.getElementById('memberSearch').value = name;
        document.getElementById('memberResults').style.display = 'none';
        console.log('Selected member:', memberId, name);
    }

    async loadRecentActivity() {
        try {
            const response = await fetch(`${this.apiUrl}/loans?limit=5`);
            const data = await response.json();
            
            const activityDiv = document.getElementById('recentActivity');
            
            if (data.loans && data.loans.length > 0) {
                activityDiv.innerHTML = data.loans.map(loan => `
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <div>
                            <strong>${loan.book_title}</strong> - ${loan.member_name}
                        </div>
                        <div class="text-muted small">
                            ${new Date(loan.loan_date).toLocaleDateString()}
                        </div>
                    </div>
                `).join('');
            } else {
                activityDiv.innerHTML = '<div class="text-muted">No recent activity</div>';
            }
        } catch (error) {
            console.error('Error loading recent activity:', error);
            document.getElementById('recentActivity').innerHTML = '<div class="text-muted">Unable to load recent activity</div>';
        }
    }

    debounce(func, wait) {
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
}

document.addEventListener('DOMContentLoaded', () => {
    window.app = new LMSApp();
});