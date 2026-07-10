export const WORKSPACE_VIEWS = ['home', 'catalog', 'loans', 'members', 'more'];

export function resolveWorkspaceView(view) {
    return WORKSPACE_VIEWS.includes(view) ? view : 'home';
}

export function getCollectionModeForWorkspaceView(view, currentMode = 'books') {
    if (view === 'home' || view === 'catalog') {
        return 'books';
    }
    if (view === 'loans') {
        return 'active_loans';
    }
    return currentMode;
}

export function renderWorkspaceView(currentView) {
    document.querySelectorAll('[data-view]').forEach(section => {
        const views = section.dataset.view.split(/\s+/).filter(Boolean);
        section.classList.toggle('view-hidden', !views.includes(currentView));
    });

    document.querySelectorAll('[data-nav-target]').forEach(item => {
        item.classList.toggle('active', item.dataset.navTarget === currentView);
    });
    document.body.dataset.workspaceView = currentView;
}

export function scrollWorkspaceToTop({ scroll = true, smooth = true } = {}) {
    if (!scroll) {
        return;
    }
    window.scrollTo({ top: 0, behavior: smooth ? 'smooth' : 'auto' });
}
