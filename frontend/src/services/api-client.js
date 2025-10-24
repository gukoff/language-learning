/**
 * API client for communicating with the flashcard backend.
 */

class ApiClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }

    /**
     * Make a HTTP request to the API.
     * @param {string} endpoint - API endpoint path
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response data
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new ApiError(
                    response.status,
                    errorData.detail || response.statusText,
                    errorData
                );
            }

            return await response.json();
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            
            // Network or other errors
            throw new ApiError(
                0,
                'Network error or server unavailable',
                { originalError: error.message }
            );
        }
    }

    /**
     * GET request
     * @param {string} endpoint - API endpoint
     * @returns {Promise<Object>} Response data
     */
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    /**
     * POST request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request body data
     * @returns {Promise<Object>} Response data
     */
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    /**
     * PUT request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request body data
     * @returns {Promise<Object>} Response data
     */
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    /**
     * DELETE request
     * @param {string} endpoint - API endpoint
     * @returns {Promise<Object>} Response data
     */
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    // Flashcard API methods

    /**
     * Create a new flashcard
     * @param {Object} flashcard - Flashcard data {front, back}
     * @returns {Promise<Object>} Created flashcard
     */
    async createFlashcard(flashcard) {
        return this.post('/api/flashcards', flashcard);
    }

    /**
     * Get all flashcards
     * @returns {Promise<Array>} List of flashcards
     */
    async getFlashcards() {
        return this.get('/api/flashcards');
    }

    /**
     * Get a specific flashcard by ID
     * @param {string} id - Flashcard ID
     * @returns {Promise<Object>} Flashcard data
     */
    async getFlashcard(id) {
        return this.get(`/api/flashcards/${id}`);
    }

    /**
     * Update a flashcard
     * @param {string} id - Flashcard ID
     * @param {Object} updates - Updated flashcard data
     * @returns {Promise<Object>} Updated flashcard
     */
    async updateFlashcard(id, updates) {
        return this.put(`/api/flashcards/${id}`, updates);
    }

    /**
     * Delete a flashcard
     * @param {string} id - Flashcard ID
     * @returns {Promise<void>}
     */
    async deleteFlashcard(id) {
        return this.delete(`/api/flashcards/${id}`);
    }

    // Study session API methods

    /**
     * Start a new study session
     * @param {Array<string>} flashcardIds - List of flashcard IDs to study
     * @returns {Promise<Object>} Study session data
     */
    async startStudySession(flashcardIds) {
        return this.post('/api/study/session', { flashcard_ids: flashcardIds });
    }

    /**
     * Get current study session
     * @param {string} sessionId - Session ID
     * @returns {Promise<Object>} Session data
     */
    async getStudySession(sessionId) {
        return this.get(`/api/study/session/${sessionId}`);
    }

    /**
     * Record study result for current flashcard
     * @param {string} sessionId - Session ID
     * @param {string} flashcardId - Flashcard ID
     * @param {boolean} correct - Whether answer was correct
     * @param {number} responseTimeMs - Response time in milliseconds
     * @returns {Promise<Object>} Updated session data
     */
    async recordStudyResult(sessionId, flashcardId, correct, responseTimeMs = null) {
        return this.post(`/api/study/session/${sessionId}/result`, {
            flashcard_id: flashcardId,
            correct,
            response_time_ms: responseTimeMs
        });
    }

    /**
     * Complete study session
     * @param {string} sessionId - Session ID
     * @returns {Promise<Object>} Session summary
     */
    async completeStudySession(sessionId) {
        return this.post(`/api/study/session/${sessionId}/complete`);
    }

    // Health check

    /**
     * Check API health
     * @returns {Promise<Object>} Health status
     */
    async healthCheck() {
        return this.get('/health');
    }
}

/**
 * API Error class for structured error handling
 */
class ApiError extends Error {
    constructor(status, message, details = {}) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.details = details;
    }

    /**
     * Check if error is a network error
     * @returns {boolean}
     */
    isNetworkError() {
        return this.status === 0;
    }

    /**
     * Check if error is a client error (4xx)
     * @returns {boolean}
     */
    isClientError() {
        return this.status >= 400 && this.status < 500;
    }

    /**
     * Check if error is a server error (5xx)
     * @returns {boolean}
     */
    isServerError() {
        return this.status >= 500;
    }
}

// Create and export a default instance
const apiClient = new ApiClient();

export { ApiClient, ApiError, apiClient };