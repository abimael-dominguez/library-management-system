// Internationalization for LMS
const translations = {
    en: {
        title: "Library Management System",
        search: {
            title: "Quick Search",
            books: "Search Books",
            books_placeholder: "Title, author, ISBN...",
            members: "Search Members", 
            members_placeholder: "Name, email..."
        },
        actions: {
            new_loan: "New Loan",
            checkout_book: "Checkout a book",
            return_book: "Return Book",
            process_return: "Process a return",
            new_member: "New Member",
            register_member: "Register new member",
            new_book: "New Book",
            add_book: "Add new book"
        },
        recent: {
            title: "Recent Activity",
            loading: "Loading recent activity..."
        }
    },
    es: {
        title: "Sistema de Gestión Bibliotecaria",
        search: {
            title: "Búsqueda Rápida",
            books: "Buscar Libros",
            books_placeholder: "Título, autor, ISBN...",
            members: "Buscar Miembros",
            members_placeholder: "Nombre, email..."
        },
        actions: {
            new_loan: "Nuevo Préstamo",
            checkout_book: "Prestar un libro",
            return_book: "Devolver Libro",
            process_return: "Procesar devolución",
            new_member: "Nuevo Miembro",
            register_member: "Registrar nuevo miembro",
            new_book: "Nuevo Libro",
            add_book: "Agregar nuevo libro"
        },
        recent: {
            title: "Actividad Reciente",
            loading: "Cargando actividad reciente..."
        }
    }
};

class I18n {
    constructor() {
        this.currentLanguage = localStorage.getItem('language') || 'en';
        this.init();
    }

    init() {
        this.updateTexts();
    }

    setLanguage(lang) {
        this.currentLanguage = lang;
        localStorage.setItem('language', lang);
        this.updateTexts();
    }

    updateTexts() {
        const elements = document.querySelectorAll('[data-i18n]');
        elements.forEach(element => {
            const key = element.getAttribute('data-i18n');
            const text = this.getText(key);
            if (text) {
                element.textContent = text;
            }
        });

        const placeholderElements = document.querySelectorAll('[data-i18n-placeholder]');
        placeholderElements.forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            const text = this.getText(key);
            if (text) {
                element.placeholder = text;
            }
        });
    }

    getText(key) {
        const keys = key.split('.');
        let value = translations[this.currentLanguage];
        
        for (const k of keys) {
            if (value && value[k]) {
                value = value[k];
            } else {
                return null;
            }
        }
        
        return value;
    }
}

function setLanguage(lang) {
    window.i18n.setLanguage(lang);
}

document.addEventListener('DOMContentLoaded', () => {
    window.i18n = new I18n();
});