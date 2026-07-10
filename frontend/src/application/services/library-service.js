import { buildQuery } from '../../infrastructure/api/client.js';

export function createLibraryService(apiClient) {
    return {
        listBooks({ limit = 50, offset = 0 } = {}) {
            return apiClient.request(`/books${buildQuery({ limit, offset })}`);
        },
        searchBooks(query, limit = 10) {
            return apiClient.request(`/search${buildQuery({ q: query, limit })}`);
        },
        listLoans({ status = 'all', limit = 50, offset = 0 } = {}) {
            return apiClient.request(`/loans${buildQuery({ status, limit, offset })}`);
        },
        listMembers({ limit = 50, offset = 0 } = {}) {
            return apiClient.request(`/members${buildQuery({ limit, offset })}`);
        },
        autocompleteMembers(query, limit = 5) {
            return apiClient.request(`/autocomplete${buildQuery({ q: query, type: 'member', limit })}`);
        },
        listEmployees({ limit = 50, offset = 0 } = {}) {
            return apiClient.request(`/employees${buildQuery({ limit, offset })}`);
        },
        getImportSummary() {
            return apiClient.request('/import-summary');
        },
        createBook(payload) {
            return apiClient.request('/books', {
                method: 'POST',
                body: JSON.stringify(payload)
            });
        },
        createLoan(payload) {
            return apiClient.request('/loans', {
                method: 'POST',
                body: JSON.stringify(payload)
            });
        },
        returnLoan(loanId, payload) {
            return apiClient.request(`/loans/${loanId}/return`, {
                method: 'PUT',
                body: JSON.stringify(payload)
            });
        },
        createMember(payload) {
            return apiClient.request('/members', {
                method: 'POST',
                body: JSON.stringify(payload)
            });
        },
        createEmployee(payload) {
            return apiClient.request('/employees', {
                method: 'POST',
                body: JSON.stringify(payload)
            });
        }
    };
}
