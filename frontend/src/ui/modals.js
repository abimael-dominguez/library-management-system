export function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) {
        return;
    }
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';

    const focusTarget = modal.querySelector('input:not([type="hidden"]), textarea, select') || modal.querySelector('button');
    if (focusTarget) {
        setTimeout(() => focusTarget.focus(), 120);
    }
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
