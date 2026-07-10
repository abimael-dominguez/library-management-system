export function getApiBaseUrl() {
    if (window.LMS_API_BASE_URL) {
        return window.LMS_API_BASE_URL.replace(/\/$/, '');
    }

    const configuredBaseUrl = document.querySelector('meta[name="lms-api-base-url"]')?.content;
    if (configuredBaseUrl) {
        return configuredBaseUrl.replace(/\/$/, '');
    }

    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:8000';
    }

    return window.location.origin.replace(/\/$/, '');
}

export function buildQuery(params = {}) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
            query.set(key, String(value));
        }
    });
    const serialized = query.toString();
    return serialized ? `?${serialized}` : '';
}

function getErrorMessage(payload, fallback) {
    if (payload?.error?.message) {
        return payload.error.message;
    }
    if (payload?.detail) {
        return payload.detail;
    }
    if (payload?.error) {
        return payload.error;
    }
    return fallback;
}

export function createApiClient(baseUrl = getApiBaseUrl()) {
    return {
        async request(endpoint, options = {}) {
            const response = await fetch(`${baseUrl}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                let message = `HTTP error! status: ${response.status}`;
                try {
                    const payload = await response.json();
                    message = getErrorMessage(payload, message);
                } catch (error) {
                    // Preserve fallback message when body is not JSON.
                }
                throw new Error(message);
            }

            return response.json();
        }
    };
}
