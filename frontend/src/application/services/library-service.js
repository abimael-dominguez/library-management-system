export function createLibraryService(apiClient) {
    return {
        listBooks() {
            return apiClient.request('/books');
        },
        searchBooks(query, limit = 10) {
            return apiClient.request(`/search?q=${encodeURIComponent(query)}&limit=${limit}`);
        },
        listLoans() {
            return apiClient.request('/loans');
        },
        listMembers() {
            return apiClient.request('/members');
        },
        autocompleteMembers(query, limit = 5) {
            return apiClient.request(`/autocomplete?q=${encodeURIComponent(query)}&type=member&limit=${limit}`);
        },
        listEmployees() {
            return apiClient.request('/employees');
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
