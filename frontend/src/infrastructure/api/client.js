export function getApiBaseUrl() {
    if (window.LMS_API_BASE_URL) {
        return window.LMS_API_BASE_URL.replace(/\/$/, '');
    }

    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:8000';
    }

    return 'http://localhost:8000';
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
                    message = payload.detail || payload.error || message;
                } catch (error) {
                    // Preserve fallback message when body is not JSON.
                }
                throw new Error(message);
            }

            return response.json();
        }
    };
}
