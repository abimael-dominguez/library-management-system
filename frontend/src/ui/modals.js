export function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) {
        return;
    }
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

export function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) {
        return;
    }

    modal.classList.remove('active');
    document.body.style.overflow = '';

    const form = modal.querySelector('form');
    if (form) {
        form.reset();
    }
}

export function toggleMobileMenu() {
    const drawer = document.getElementById('mobileMenu');
    const overlay = document.getElementById('mobileMenuOverlay');
    if (!drawer || !overlay) {
        return false;
    }

    const isOpen = drawer.classList.toggle('open');
    overlay.classList.toggle('active', isOpen);
    document.body.classList.toggle('menu-open', isOpen);
    return isOpen;
}

export function closeMobileMenu() {
    const drawer = document.getElementById('mobileMenu');
    const overlay = document.getElementById('mobileMenuOverlay');
    if (!drawer || !overlay) {
        return;
    }
    drawer.classList.remove('open');
    overlay.classList.remove('active');
    document.body.classList.remove('menu-open');
}

export function isMobileMenuOpen() {
    const drawer = document.getElementById('mobileMenu');
    return drawer ? drawer.classList.contains('open') : false;
}

export function toggleFabSheet() {
    const sheet = document.getElementById('fabSheet');
    const overlay = document.getElementById('fabOverlay');
    if (!sheet || !overlay) {
        return false;
    }

    const isOpen = sheet.classList.toggle('open');
    overlay.classList.toggle('active', isOpen);
    document.body.classList.toggle('menu-open', isOpen);
    return isOpen;
}

export function closeFabSheet() {
    const sheet = document.getElementById('fabSheet');
    const overlay = document.getElementById('fabOverlay');
    if (!sheet || !overlay) {
        return;
    }
    sheet.classList.remove('open');
    overlay.classList.remove('active');
    document.body.classList.remove('menu-open');
}

export function isFabSheetOpen() {
    const sheet = document.getElementById('fabSheet');
    return sheet ? sheet.classList.contains('open') : false;
}
