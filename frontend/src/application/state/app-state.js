export function createAppState() {
    return {
        searchTimeout: null,
        books: [],
        loans: [],
        members: [],
        employees: [],
        importSummary: null,
        currentView: 'home',
        collectionMode: 'books',
        theme: 'light',
        palette: 'indigo'
    };
}
