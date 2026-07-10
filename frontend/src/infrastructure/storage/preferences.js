const THEME_KEY = 'theme';
const PALETTE_KEY = 'palette';
const LANGUAGE_KEY = 'language';

export function loadThemePreference() {
    return localStorage.getItem(THEME_KEY) || 'light';
}

export function saveThemePreference(theme) {
    localStorage.setItem(THEME_KEY, theme);
}

export function loadPalettePreference() {
    return localStorage.getItem(PALETTE_KEY) || 'indigo';
}

export function savePalettePreference(name) {
    localStorage.setItem(PALETTE_KEY, name);
}

export function loadLanguagePreference() {
    return localStorage.getItem(LANGUAGE_KEY);
}

export function saveLanguagePreference(language) {
    localStorage.setItem(LANGUAGE_KEY, language);
}
