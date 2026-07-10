const DEFAULT_LANGUAGE = 'es';

export const SUPPORTED_LANGUAGES = {
    es: {
        label: 'Español',
        shortLabel: 'ES'
    },
    en: {
        label: 'English',
        shortLabel: 'EN'
    }
};

const TRANSLATIONS = {
    es: {
        'app.title': 'Biblioteca CBG',
        'app.subtitle': 'Circulación',
        'app.documentTitle': 'Biblioteca CBG',
        'app.loading': 'Cargando...',
        'app.empty': 'Sin datos todavía',

        'nav.home': 'Inicio',
        'nav.catalog': 'Catálogo',
        'nav.loans': 'Préstamos',
        'nav.members': 'Miembros',
        'nav.more': 'Más',
        'nav.employees': 'Equipo',
        'nav.settings': 'Config.',
        'nav.overdue': 'Vencidos',

        'actions.createLoan': 'Prestar',
        'actions.returnBook': 'Devolver',
        'actions.addBook': 'Agregar libro',
        'actions.addMember': 'Nuevo miembro',
        'actions.addEmployee': 'Nuevo empleado',
        'actions.refresh': 'Actualizar',
        'actions.save': 'Guardar',
        'actions.cancel': 'Cancelar',
        'actions.close': 'Cerrar',
        'actions.registerReturn': 'Registrar devolución',
        'actions.openSettings': 'Abrir configuración',
        'actions.search': 'Buscar',
        'actions.backHome': 'Volver al inicio',

        'workspace.eyebrow': 'Mostrador',
        'workspace.title': 'Circulación rápida',
        'workspace.copy': 'Busca, presta y recibe libros sin perder de vista el flujo principal.',
        'workspace.searchLabel': 'Búsqueda global',
        'workspace.searchPlaceholder': 'Buscar título, autor o ISBN',
        'workspace.searchHint': 'Resultados instantáneos del catálogo',
        'workspace.syncHealthy': 'Datos listos',
        'workspace.syncWarning': '{count} alertas de datos',
        'workspace.syncChecking': 'Revisando datos',
        'workspace.primaryActions': 'Acciones principales',

        'metrics.catalog': 'Catálogo',
        'metrics.catalogHint': 'títulos',
        'metrics.openLoans': 'Abiertos',
        'metrics.openLoansHint': 'en circulación',
        'metrics.members': 'Miembros',
        'metrics.membersHint': 'registrados',
        'metrics.overdue': 'Vencidos',
        'metrics.overdueHint': 'requieren seguimiento',

        'sections.catalogEyebrow': 'Catálogo',
        'sections.catalogTitle': 'Libros disponibles',
        'sections.catalogDescription': 'Consulta disponibilidad por título y encuentra copias para prestar.',
        'sections.loansEyebrow': 'Circulación',
        'sections.loansTitle': 'Préstamos abiertos',
        'sections.loansDescription': 'Libros fuera de estantería, incluidos vencidos, con devolución rápida.',
        'sections.overdueEyebrow': 'Seguimiento',
        'sections.overdueTitle': 'Préstamos vencidos',
        'sections.overdueDescription': 'Casos que requieren atención prioritaria del equipo.',
        'sections.membersEyebrow': 'Directorio',
        'sections.membersTitle': 'Miembros',
        'sections.membersDescription': 'Perfiles de usuarios registrados para préstamo.',
        'sections.moreEyebrow': 'Operación',
        'sections.moreTitle': 'Más herramientas',
        'sections.moreDescription': 'Configuración, datos de importación y equipo interno.',

        'settings.title': 'Configuración',
        'settings.language': 'Idioma',
        'settings.languageHelp': 'La preferencia se guarda en este navegador.',
        'settings.appearance': 'Apariencia',
        'settings.palette': 'Paleta',
        'settings.dataHealth': 'Estado de datos',
        'settings.staff': 'Equipo interno',
        'settings.themeLight': 'Claro',
        'settings.themeDark': 'Oscuro',
        'settings.paletteIndigo': 'Índigo',
        'settings.paletteTeal': 'Verde',
        'settings.paletteAmber': 'Ámbar',
        'settings.paletteSlate': 'Pizarra',

        'import.title': 'Estado del CSV',
        'import.source': 'Fuente',
        'import.status': 'Estado',
        'import.warnings': 'Alertas',
        'import.copies': 'Copias',
        'import.loadingSource': 'Cargando...',
        'import.checking': 'Revisando',
        'import.needsReview': 'Revisar',
        'import.healthy': 'Saludable',
        'import.warningText': 'La última sincronización terminó con {count} alerta(s). Revisa filas incompletas antes del próximo import.',
        'import.cleanText': 'La última sincronización terminó sin alertas. La data local está lista para usar.',

        'forms.book.title': 'Título',
        'forms.book.author': 'Autor',
        'forms.book.isbn': 'ISBN',
        'forms.book.publisher': 'Editorial',
        'forms.book.year': 'Año',
        'forms.book.pages': 'Páginas',
        'forms.book.loanWeeks': 'Semanas de préstamo',
        'forms.book.copies': 'Copias',
        'forms.loan.book': 'Buscar libro',
        'forms.loan.bookPlaceholder': 'Título o autor...',
        'forms.loan.member': 'Buscar miembro',
        'forms.loan.memberPlaceholder': 'Nombre del miembro...',
        'forms.loan.employee': 'Empleado',
        'forms.loan.employeePlaceholder': 'Buscar empleado...',
        'forms.loan.loanDate': 'Fecha de préstamo',
        'forms.loan.dueDate': 'Fecha límite',
        'forms.return.loan': 'Buscar préstamo activo',
        'forms.return.loanPlaceholder': 'Libro o miembro...',
        'forms.return.returnDate': 'Fecha de devolución',
        'forms.member.firstName': 'Nombre',
        'forms.member.lastName': 'Apellido',
        'forms.member.email': 'Email',
        'forms.member.address': 'Dirección',
        'forms.member.phone': 'Teléfono',
        'forms.employee.position': 'Cargo',

        'modal.addBook.title': 'Agregar libro',
        'modal.addBook.subtitle': 'Crea un título y define copias listas para circular.',
        'modal.createLoan.title': 'Crear préstamo',
        'modal.createLoan.subtitle': 'Selecciona libro, miembro y fecha de entrega.',
        'modal.returnBook.title': 'Registrar devolución',
        'modal.returnBook.subtitle': 'Encuentra el préstamo abierto y marca la copia como recibida.',
        'modal.addMember.title': 'Registrar miembro',
        'modal.addMember.subtitle': 'Agrega un perfil para mantener trazabilidad de circulación.',
        'modal.addEmployee.title': 'Registrar empleado',
        'modal.addEmployee.subtitle': 'Mantén actualizado el equipo que procesa préstamos.',

        'empty.booksTitle': 'No hay libros',
        'empty.booksCopy': 'Prueba otra búsqueda o agrega un título nuevo.',
        'empty.openLoansTitle': 'No hay préstamos abiertos',
        'empty.openLoansCopy': 'Los próximos préstamos aparecerán aquí.',
        'empty.overdueTitle': 'No hay préstamos vencidos',
        'empty.overdueCopy': 'Todo está en orden por ahora.',
        'empty.members': 'No hay miembros todavía. Registra el primer usuario para iniciar circulación.',
        'empty.employees': 'No hay empleados todavía. Agrega equipo para mantener trazabilidad.',
        'empty.searchBooks': 'No encontramos libros',
        'empty.searchMembers': 'No encontramos miembros',
        'empty.searchEmployees': 'No encontramos empleados',
        'empty.searchLoans': 'No encontramos préstamos activos',

        'book.byAuthor': 'por {author}',
        'book.isbn': 'ISBN',
        'book.publisher': 'Editorial',
        'book.year': 'Año',
        'book.pages': 'Páginas',
        'book.copies': '{count} copias',
        'book.loanWeeks': '{count} sem.',
        'book.availableCount': '{available} disponibles',
        'availability.label': 'Disponibilidad',

        'loan.borrower': 'Usuario',
        'loan.processedBy': 'Atendió',
        'loan.noEmployee': 'Sin empleado',
        'loan.noMember': 'Sin miembro',
        'loan.loanDate': 'Préstamo',
        'loan.dueDate': 'Entrega',
        'loan.copyStatus': 'Estado',
        'loan.circulating': 'En circulación',
        'loan.attentionNeeded': 'Atención',
        'loan.id': 'ID',
        'loan.onSchedule': 'En tiempo',
        'loan.priorityFollowUp': 'Seguimiento',

        'status.in_progress': 'Activo',
        'status.returned': 'Devuelto',
        'status.overdue': 'Vencido',
        'status.available': 'Disponible',
        'status.damaged': 'Dañado',
        'status.lost': 'Perdido',
        'status.active': 'Activo',

        'toast.apiFailed': 'Falló la llamada al API: {message}',
        'toast.loanRequired': 'Completa los campos requeridos del préstamo.',
        'toast.loanCreated': 'Préstamo creado correctamente.',
        'toast.loanCreateFailed': 'No se pudo crear el préstamo. Intenta de nuevo.',
        'toast.bookUnavailable': 'Ese libro no tiene copias disponibles ahora.',
        'toast.returnSelectLoan': 'Selecciona un préstamo primero.',
        'toast.returned': 'Devolución registrada correctamente.',
        'toast.returnFailed': 'No se pudo registrar la devolución. Intenta de nuevo.',
        'toast.bookAdded': 'Libro agregado correctamente.',
        'toast.bookAddFailed': 'No se pudo agregar el libro.',
        'toast.memberAdded': 'Miembro registrado correctamente.',
        'toast.memberAddFailed': 'No se pudo registrar el miembro.',
        'toast.employeeAdded': 'Empleado registrado correctamente.',
        'toast.employeeAddFailed': 'No se pudo registrar el empleado.',
        'toast.themeChanged': 'Modo {theme} activado.',
        'toast.languageChanged': 'Idioma cambiado a {language}.',
        'toast.showingBooks': 'Mostrando catálogo.',
        'toast.showingOpenLoans': 'Mostrando préstamos abiertos.',
        'toast.showingOverdueLoans': 'Mostrando vencidos.',
        'theme.light': 'claro',
        'theme.dark': 'oscuro',
        'error.loadBooksTitle': 'No se pudieron cargar los libros',
        'error.loadBooksCopy': 'Actualiza el catálogo o revisa si el backend está disponible.'
    },
    en: {
        'app.title': 'CBG Library',
        'app.subtitle': 'Circulation',
        'app.documentTitle': 'CBG Library',
        'app.loading': 'Loading...',
        'app.empty': 'No data yet',

        'nav.home': 'Home',
        'nav.catalog': 'Catalog',
        'nav.loans': 'Loans',
        'nav.members': 'Members',
        'nav.more': 'More',
        'nav.employees': 'Team',
        'nav.settings': 'Settings',
        'nav.overdue': 'Overdue',

        'actions.createLoan': 'Loan',
        'actions.returnBook': 'Return',
        'actions.addBook': 'Add book',
        'actions.addMember': 'New member',
        'actions.addEmployee': 'New employee',
        'actions.refresh': 'Refresh',
        'actions.save': 'Save',
        'actions.cancel': 'Cancel',
        'actions.close': 'Close',
        'actions.registerReturn': 'Register return',
        'actions.openSettings': 'Open settings',
        'actions.search': 'Search',
        'actions.backHome': 'Back home',

        'workspace.eyebrow': 'Desk',
        'workspace.title': 'Fast circulation',
        'workspace.copy': 'Search, loan, and receive books without losing the main workflow.',
        'workspace.searchLabel': 'Global search',
        'workspace.searchPlaceholder': 'Search title, author, or ISBN',
        'workspace.searchHint': 'Instant catalog results',
        'workspace.syncHealthy': 'Data ready',
        'workspace.syncWarning': '{count} data alerts',
        'workspace.syncChecking': 'Checking data',
        'workspace.primaryActions': 'Primary actions',

        'metrics.catalog': 'Catalog',
        'metrics.catalogHint': 'titles',
        'metrics.openLoans': 'Open',
        'metrics.openLoansHint': 'in circulation',
        'metrics.members': 'Members',
        'metrics.membersHint': 'registered',
        'metrics.overdue': 'Overdue',
        'metrics.overdueHint': 'need follow-up',

        'sections.catalogEyebrow': 'Catalog',
        'sections.catalogTitle': 'Available books',
        'sections.catalogDescription': 'Check title availability and find copies for loan.',
        'sections.loansEyebrow': 'Circulation',
        'sections.loansTitle': 'Open loans',
        'sections.loansDescription': 'Books away from shelf, including overdue items, with fast returns.',
        'sections.overdueEyebrow': 'Follow-up',
        'sections.overdueTitle': 'Overdue loans',
        'sections.overdueDescription': 'Cases that need staff attention first.',
        'sections.membersEyebrow': 'Directory',
        'sections.membersTitle': 'Members',
        'sections.membersDescription': 'Registered borrower profiles.',
        'sections.moreEyebrow': 'Operations',
        'sections.moreTitle': 'More tools',
        'sections.moreDescription': 'Settings, import data, and internal staff.',

        'settings.title': 'Settings',
        'settings.language': 'Language',
        'settings.languageHelp': 'This preference is saved in this browser.',
        'settings.appearance': 'Appearance',
        'settings.palette': 'Palette',
        'settings.dataHealth': 'Data health',
        'settings.staff': 'Internal team',
        'settings.themeLight': 'Light',
        'settings.themeDark': 'Dark',
        'settings.paletteIndigo': 'Indigo',
        'settings.paletteTeal': 'Teal',
        'settings.paletteAmber': 'Amber',
        'settings.paletteSlate': 'Slate',

        'import.title': 'CSV status',
        'import.source': 'Source',
        'import.status': 'Status',
        'import.warnings': 'Alerts',
        'import.copies': 'Copies',
        'import.loadingSource': 'Loading...',
        'import.checking': 'Checking',
        'import.needsReview': 'Review',
        'import.healthy': 'Healthy',
        'import.warningText': 'The last sync completed with {count} alert(s). Review incomplete rows before the next import.',
        'import.cleanText': 'The last sync completed without alerts. Local data is ready to use.',

        'forms.book.title': 'Title',
        'forms.book.author': 'Author',
        'forms.book.isbn': 'ISBN',
        'forms.book.publisher': 'Publisher',
        'forms.book.year': 'Year',
        'forms.book.pages': 'Pages',
        'forms.book.loanWeeks': 'Loan weeks',
        'forms.book.copies': 'Copies',
        'forms.loan.book': 'Find book',
        'forms.loan.bookPlaceholder': 'Title or author...',
        'forms.loan.member': 'Find member',
        'forms.loan.memberPlaceholder': 'Member name...',
        'forms.loan.employee': 'Employee',
        'forms.loan.employeePlaceholder': 'Search employee...',
        'forms.loan.loanDate': 'Loan date',
        'forms.loan.dueDate': 'Due date',
        'forms.return.loan': 'Find active loan',
        'forms.return.loanPlaceholder': 'Book or member...',
        'forms.return.returnDate': 'Return date',
        'forms.member.firstName': 'First name',
        'forms.member.lastName': 'Last name',
        'forms.member.email': 'Email',
        'forms.member.address': 'Address',
        'forms.member.phone': 'Phone',
        'forms.employee.position': 'Position',

        'modal.addBook.title': 'Add book',
        'modal.addBook.subtitle': 'Create a title and define copies ready to circulate.',
        'modal.createLoan.title': 'Create loan',
        'modal.createLoan.subtitle': 'Select book, member, and expected return date.',
        'modal.returnBook.title': 'Register return',
        'modal.returnBook.subtitle': 'Find the open loan and mark the copy as received.',
        'modal.addMember.title': 'Register member',
        'modal.addMember.subtitle': 'Add a borrower profile so circulation remains traceable.',
        'modal.addEmployee.title': 'Register employee',
        'modal.addEmployee.subtitle': 'Keep staff records up to date for loan processing.',

        'empty.booksTitle': 'No books',
        'empty.booksCopy': 'Try another search or add a new title.',
        'empty.openLoansTitle': 'No open loans',
        'empty.openLoansCopy': 'Future loans will appear here.',
        'empty.overdueTitle': 'No overdue loans',
        'empty.overdueCopy': 'Everything is on track right now.',
        'empty.members': 'No members yet. Register the first borrower to start circulation.',
        'empty.employees': 'No employees yet. Add staff to keep traceability.',
        'empty.searchBooks': 'No books found',
        'empty.searchMembers': 'No members found',
        'empty.searchEmployees': 'No employees found',
        'empty.searchLoans': 'No active loans found',

        'book.byAuthor': 'by {author}',
        'book.isbn': 'ISBN',
        'book.publisher': 'Publisher',
        'book.year': 'Year',
        'book.pages': 'Pages',
        'book.copies': '{count} copies',
        'book.loanWeeks': '{count}w loan',
        'book.availableCount': '{available} available',
        'availability.label': 'Availability',

        'loan.borrower': 'Borrower',
        'loan.processedBy': 'Processed by',
        'loan.noEmployee': 'No employee',
        'loan.noMember': 'No member',
        'loan.loanDate': 'Loan',
        'loan.dueDate': 'Due',
        'loan.copyStatus': 'Status',
        'loan.circulating': 'Circulating',
        'loan.attentionNeeded': 'Attention',
        'loan.id': 'ID',
        'loan.onSchedule': 'On schedule',
        'loan.priorityFollowUp': 'Follow-up',

        'status.in_progress': 'Active',
        'status.returned': 'Returned',
        'status.overdue': 'Overdue',
        'status.available': 'Available',
        'status.damaged': 'Damaged',
        'status.lost': 'Lost',
        'status.active': 'Active',

        'toast.apiFailed': 'API call failed: {message}',
        'toast.loanRequired': 'Complete the required loan fields.',
        'toast.loanCreated': 'Loan created successfully.',
        'toast.loanCreateFailed': 'Could not create the loan. Please try again.',
        'toast.bookUnavailable': 'That book has no available copies right now.',
        'toast.returnSelectLoan': 'Please select a loan first.',
        'toast.returned': 'Book returned successfully.',
        'toast.returnFailed': 'Could not return the book. Please try again.',
        'toast.bookAdded': 'Book added successfully.',
        'toast.bookAddFailed': 'Failed to add book.',
        'toast.memberAdded': 'Member registered successfully.',
        'toast.memberAddFailed': 'Could not register the member.',
        'toast.employeeAdded': 'Employee registered successfully.',
        'toast.employeeAddFailed': 'Could not register the employee.',
        'toast.themeChanged': '{theme} mode enabled.',
        'toast.languageChanged': 'Language changed to {language}.',
        'toast.showingBooks': 'Showing catalog.',
        'toast.showingOpenLoans': 'Showing open loans.',
        'toast.showingOverdueLoans': 'Showing overdue loans.',
        'theme.light': 'light',
        'theme.dark': 'dark',
        'error.loadBooksTitle': 'Failed to load books',
        'error.loadBooksCopy': 'Refresh the catalog or check whether the backend is available.'
    }
};

let currentLanguage = DEFAULT_LANGUAGE;

function lookup(dictionary, key) {
    return key.split('.').reduce((value, part) => {
        if (value && Object.prototype.hasOwnProperty.call(value, part)) {
            return value[part];
        }
        return undefined;
    }, dictionary);
}

function interpolate(template, params) {
    return String(template).replace(/\{(\w+)\}/g, (_, key) => {
        const value = params[key];
        return value === undefined || value === null ? '' : String(value);
    });
}

export function resolveLanguage(language) {
    const normalized = String(language || '').toLowerCase().split('-')[0];
    return TRANSLATIONS[normalized] ? normalized : DEFAULT_LANGUAGE;
}

export function detectLanguage() {
    return resolveLanguage(window.navigator?.language || DEFAULT_LANGUAGE);
}

export function setCurrentLanguage(language) {
    currentLanguage = resolveLanguage(language);
    return currentLanguage;
}

export function getCurrentLanguage() {
    return currentLanguage;
}

export function getLanguageLabel(language = currentLanguage) {
    const resolved = resolveLanguage(language);
    return SUPPORTED_LANGUAGES[resolved]?.label || resolved;
}

export function t(key, params = {}, language = currentLanguage) {
    const resolved = resolveLanguage(language);
    const value = TRANSLATIONS[resolved]?.[key] ?? TRANSLATIONS[DEFAULT_LANGUAGE]?.[key] ?? key;
    return interpolate(value, params);
}

export function translateStatic(root = document, language = currentLanguage) {
    const resolved = setCurrentLanguage(language);
    document.documentElement.lang = resolved;
    document.title = t('app.documentTitle');

    root.querySelectorAll('[data-i18n]').forEach(element => {
        element.textContent = t(element.dataset.i18n);
    });

    root.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        element.setAttribute('placeholder', t(element.dataset.i18nPlaceholder));
    });

    root.querySelectorAll('[data-i18n-aria-label]').forEach(element => {
        element.setAttribute('aria-label', t(element.dataset.i18nAriaLabel));
    });
}
