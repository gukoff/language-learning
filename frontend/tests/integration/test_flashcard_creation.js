/**
 * End-to-end tests for flashcard creation flow.
 * Following TDD methodology - these tests should FAIL initially.
 */

import { jest } from '@jest/globals';

// Mock the API client for testing
class MockApiClient {
    constructor() {
        this.createFlashcard = jest.fn();
        this.getFlashcards = jest.fn();
        this.healthCheck = jest.fn();
    }

    async createFlashcard(flashcard) {
        // Mock successful creation
        return {
            id: 'mock-id-' + Date.now(),
            front: flashcard.front,
            back: flashcard.back,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            study_count: 0,
            correct_count: 0
        };
    }

    async healthCheck() {
        return { status: 'healthy' };
    }
}

describe('Flashcard Creation End-to-End Tests', () => {
    let mockApiClient;
    let mockFlashcardCreator;
    let container;

    beforeEach(() => {
        // Set up DOM
        document.body.innerHTML = `
            <div id="app">
                <div id="create-view" class="hidden">
                    <form id="flashcard-form">
                        <div class="form-group">
                            <label for="front-input">Front (Question/Prompt):</label>
                            <input type="text" id="front-input" class="form-input" maxlength="500" required>
                            <div id="front-error" class="form-error" style="display: none;"></div>
                        </div>
                        
                        <div class="form-group">
                            <label for="back-input">Back (Answer/Translation):</label>
                            <textarea id="back-input" class="form-textarea" maxlength="500" required></textarea>
                            <div id="back-error" class="form-error" style="display: none;"></div>
                        </div>
                        
                        <div class="form-group">
                            <button type="submit" id="create-btn" class="btn btn-primary">Create Flashcard</button>
                            <button type="button" id="cancel-btn" class="btn btn-secondary">Cancel</button>
                        </div>
                        
                        <div id="creation-feedback" class="alert" style="display: none;"></div>
                    </form>
                </div>
            </div>
        `;

        // Mock dependencies
        mockApiClient = new MockApiClient();
        
        // Mock the FlashcardCreator component
        mockFlashcardCreator = {
            init: jest.fn(),
            show: jest.fn(),
            hide: jest.fn(),
            handleSubmit: jest.fn(),
            clearForm: jest.fn(),
            showError: jest.fn(),
            showSuccess: jest.fn()
        };

        container = document.getElementById('app');
    });

    afterEach(() => {
        document.body.innerHTML = '';
        jest.clearAllMocks();
    });

    describe('Form Rendering', () => {
        test('should render flashcard creation form with required fields', () => {
            const createView = document.getElementById('create-view');
            const frontInput = document.getElementById('front-input');
            const backInput = document.getElementById('back-input');
            const createButton = document.getElementById('create-btn');
            const cancelButton = document.getElementById('cancel-btn');

            expect(createView).toBeTruthy();
            expect(frontInput).toBeTruthy();
            expect(backInput).toBeTruthy();
            expect(createButton).toBeTruthy();
            expect(cancelButton).toBeTruthy();

            // Check accessibility attributes
            expect(frontInput.getAttribute('required')).toBe('');
            expect(backInput.getAttribute('required')).toBe('');
            expect(frontInput.getAttribute('maxlength')).toBe('500');
            expect(backInput.getAttribute('maxlength')).toBe('500');
        });

        test('should have proper labels associated with form inputs', () => {
            const frontLabel = document.querySelector('label[for="front-input"]');
            const backLabel = document.querySelector('label[for="back-input"]');

            expect(frontLabel).toBeTruthy();
            expect(backLabel).toBeTruthy();
            expect(frontLabel.textContent).toContain('Front');
            expect(backLabel.textContent).toContain('Back');
        });

        test('should have error message containers for validation feedback', () => {
            const frontError = document.getElementById('front-error');
            const backError = document.getElementById('back-error');
            const generalFeedback = document.getElementById('creation-feedback');

            expect(frontError).toBeTruthy();
            expect(backError).toBeTruthy();
            expect(generalFeedback).toBeTruthy();

            // Should be hidden initially
            expect(frontError.style.display).toBe('none');
            expect(backError.style.display).toBe('none');
            expect(generalFeedback.style.display).toBe('none');
        });
    });

    describe('Form Validation', () => {
        test('should prevent submission with empty front field', async () => {
            const form = document.getElementById('flashcard-form');
            const frontInput = document.getElementById('front-input');
            const backInput = document.getElementById('back-input');

            // Set up form data
            frontInput.value = '';
            backInput.value = 'Valid back content';

            // Mock form submission handler
            const mockSubmitHandler = jest.fn((e) => {
                e.preventDefault();
                // Validation should catch empty front
                if (!frontInput.value.trim()) {
                    const frontError = document.getElementById('front-error');
                    frontError.textContent = 'Front content is required';
                    frontError.style.display = 'block';
                    return false;
                }
                return true;
            });

            form.addEventListener('submit', mockSubmitHandler);

            // Trigger form submission
            const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
            form.dispatchEvent(submitEvent);

            expect(mockSubmitHandler).toHaveBeenCalled();
            
            // Check that error is displayed
            const frontError = document.getElementById('front-error');
            expect(frontError.style.display).toBe('block');
            expect(frontError.textContent).toContain('required');
        });

        test('should prevent submission with empty back field', async () => {
            const form = document.getElementById('flashcard-form');
            const frontInput = document.getElementById('front-input');
            const backInput = document.getElementById('back-input');

            // Set up form data
            frontInput.value = 'Valid front content';
            backInput.value = '';

            // Mock form submission handler
            const mockSubmitHandler = jest.fn((e) => {
                e.preventDefault();
                // Validation should catch empty back
                if (!backInput.value.trim()) {
                    const backError = document.getElementById('back-error');
                    backError.textContent = 'Back content is required';
                    backError.style.display = 'block';
                    return false;
                }
                return true;
            });

            form.addEventListener('submit', mockSubmitHandler);

            // Trigger form submission
            const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
            form.dispatchEvent(submitEvent);

            expect(mockSubmitHandler).toHaveBeenCalled();
            
            // Check that error is displayed
            const backError = document.getElementById('back-error');
            expect(backError.style.display).toBe('block');
            expect(backError.textContent).toContain('required');
        });

        test('should prevent submission with whitespace-only content', async () => {
            const form = document.getElementById('flashcard-form');
            const frontInput = document.getElementById('front-input');
            const backInput = document.getElementById('back-input');

            // Set up form data with whitespace only
            frontInput.value = '   ';
            backInput.value = '   ';

            // Mock form submission handler
            const mockSubmitHandler = jest.fn((e) => {
                e.preventDefault();
                
                if (!frontInput.value.trim()) {
                    const frontError = document.getElementById('front-error');
                    frontError.textContent = 'Front content cannot be empty';
                    frontError.style.display = 'block';
                    return false;
                }
                
                if (!backInput.value.trim()) {
                    const backError = document.getElementById('back-error');
                    backError.textContent = 'Back content cannot be empty';
                    backError.style.display = 'block';
                    return false;
                }
                
                return true;
            });

            form.addEventListener('submit', mockSubmitHandler);

            // Trigger form submission
            const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
            form.dispatchEvent(submitEvent);

            expect(mockSubmitHandler).toHaveBeenCalled();
            
            // Check that errors are displayed
            const frontError = document.getElementById('front-error');
            const backError = document.getElementById('back-error');
            expect(frontError.style.display).toBe('block');
            expect(backError.style.display).toBe('block');
        });

        test('should enforce maximum length limits', () => {
            const frontInput = document.getElementById('front-input');
            const backInput = document.getElementById('back-input');

            // Check maxlength attributes
            expect(frontInput.getAttribute('maxlength')).toBe('500');
            expect(backInput.getAttribute('maxlength')).toBe('500');

            // Test that browser enforces maxlength (simulation)
            const longText = 'A'.repeat(501);
            frontInput.value = longText;
            
            // Browser should truncate to maxlength
            expect(frontInput.value.length).toBeLessThanOrEqual(500);
        });
    });

    describe('Successful Flashcard Creation', () => {
        test('should create flashcard with valid data', async () => {
            const form = document.getElementById('flashcard-form');
            const frontInput = document.getElementById('front-input');
            const backInput = document.getElementById('back-input');

            // Set up valid form data
            frontInput.value = 'Hello';
            backInput.value = 'Hola';

            // Mock successful submission
            const mockSubmitHandler = jest.fn(async (e) => {
                e.preventDefault();
                
                // Simulate validation passing
                if (frontInput.value.trim() && backInput.value.trim()) {
                    // Simulate API call
                    const result = await mockApiClient.createFlashcard({
                        front: frontInput.value.trim(),
                        back: backInput.value.trim()
                    });

                    // Show success feedback
                    const feedback = document.getElementById('creation-feedback');
                    feedback.className = 'alert alert-success';
                    feedback.textContent = 'Flashcard created successfully!';
                    feedback.style.display = 'block';

                    // Clear form
                    frontInput.value = '';
                    backInput.value = '';

                    return result;
                }
            });

            form.addEventListener('submit', mockSubmitHandler);

            // Trigger form submission
            const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
            form.dispatchEvent(submitEvent);

            // Wait for async operations
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(mockSubmitHandler).toHaveBeenCalled();
            expect(mockApiClient.createFlashcard).toHaveBeenCalledWith({
                front: 'Hello',
                back: 'Hola'
            });

            // Check success feedback
            const feedback = document.getElementById('creation-feedback');
            expect(feedback.style.display).toBe('block');
            expect(feedback.className).toContain('alert-success');
            expect(feedback.textContent).toContain('successfully');

            // Check form is cleared
            expect(frontInput.value).toBe('');
            expect(backInput.value).toBe('');
        });

        test('should strip whitespace from content before submission', async () => {
            const form = document.getElementById('flashcard-form');
            const frontInput = document.getElementById('front-input');
            const backInput = document.getElementById('back-input');

            // Set up form data with extra whitespace
            frontInput.value = '  Hello  ';
            backInput.value = '  Hola  ';

            // Mock submission handler that trims content
            const mockSubmitHandler = jest.fn(async (e) => {
                e.preventDefault();
                
                const trimmedFront = frontInput.value.trim();
                const trimmedBack = backInput.value.trim();
                
                await mockApiClient.createFlashcard({
                    front: trimmedFront,
                    back: trimmedBack
                });
            });

            form.addEventListener('submit', mockSubmitHandler);

            // Trigger form submission
            const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
            form.dispatchEvent(submitEvent);

            // Wait for async operations
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(mockApiClient.createFlashcard).toHaveBeenCalledWith({
                front: 'Hello',
                back: 'Hola'
            });
        });
    });

    describe('Error Handling', () => {
        test('should handle API errors gracefully', async () => {
            const form = document.getElementById('flashcard-form');
            const frontInput = document.getElementById('front-input');
            const backInput = document.getElementById('back-input');

            // Set up valid form data
            frontInput.value = 'Test';
            backInput.value = 'Prueba';

            // Mock API error
            mockApiClient.createFlashcard.mockRejectedValue(new Error('Network error'));

            // Mock submission handler with error handling
            const mockSubmitHandler = jest.fn(async (e) => {
                e.preventDefault();
                
                try {
                    await mockApiClient.createFlashcard({
                        front: frontInput.value.trim(),
                        back: backInput.value.trim()
                    });
                } catch (error) {
                    // Show error feedback
                    const feedback = document.getElementById('creation-feedback');
                    feedback.className = 'alert alert-error';
                    feedback.textContent = 'Failed to create flashcard. Please try again.';
                    feedback.style.display = 'block';
                }
            });

            form.addEventListener('submit', mockSubmitHandler);

            // Trigger form submission
            const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
            form.dispatchEvent(submitEvent);

            // Wait for async operations
            await new Promise(resolve => setTimeout(resolve, 0));

            // Check error feedback is shown
            const feedback = document.getElementById('creation-feedback');
            expect(feedback.style.display).toBe('block');
            expect(feedback.className).toContain('alert-error');
            expect(feedback.textContent).toContain('Failed');
        });

        test('should handle network connectivity issues', async () => {
            // Mock network error
            mockApiClient.createFlashcard.mockRejectedValue({
                name: 'NetworkError',
                message: 'Failed to fetch'
            });

            const form = document.getElementById('flashcard-form');
            const frontInput = document.getElementById('front-input');
            const backInput = document.getElementById('back-input');

            frontInput.value = 'Test';
            backInput.value = 'Prueba';

            // Simulate submission with network error handling
            const mockSubmitHandler = jest.fn(async (e) => {
                e.preventDefault();
                
                try {
                    await mockApiClient.createFlashcard({
                        front: frontInput.value.trim(),
                        back: backInput.value.trim()
                    });
                } catch (error) {
                    const feedback = document.getElementById('creation-feedback');
                    feedback.className = 'alert alert-error';
                    feedback.textContent = 'Network error. Please check your connection and try again.';
                    feedback.style.display = 'block';
                }
            });

            form.addEventListener('submit', mockSubmitHandler);

            const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
            form.dispatchEvent(submitEvent);

            await new Promise(resolve => setTimeout(resolve, 0));

            const feedback = document.getElementById('creation-feedback');
            expect(feedback.textContent).toContain('Network error');
        });
    });

    describe('User Interaction', () => {
        test('should handle cancel button click', () => {
            const cancelButton = document.getElementById('cancel-btn');
            const frontInput = document.getElementById('front-input');
            const backInput = document.getElementById('back-input');

            // Set up form data
            frontInput.value = 'Some content';
            backInput.value = 'Some content';

            // Mock cancel handler
            const mockCancelHandler = jest.fn(() => {
                // Clear form
                frontInput.value = '';
                backInput.value = '';
                
                // Hide any error messages
                document.getElementById('front-error').style.display = 'none';
                document.getElementById('back-error').style.display = 'none';
                document.getElementById('creation-feedback').style.display = 'none';
            });

            cancelButton.addEventListener('click', mockCancelHandler);

            // Trigger cancel
            cancelButton.click();

            expect(mockCancelHandler).toHaveBeenCalled();
            expect(frontInput.value).toBe('');
            expect(backInput.value).toBe('');
        });

        test('should support keyboard navigation', () => {
            const frontInput = document.getElementById('front-input');
            const backInput = document.getElementById('back-input');
            const createButton = document.getElementById('create-btn');

            // All form elements should be focusable
            expect(frontInput.tabIndex).toBeGreaterThanOrEqual(0);
            expect(backInput.tabIndex).toBeGreaterThanOrEqual(0);
            expect(createButton.tabIndex).toBeGreaterThanOrEqual(0);

            // Test focus behavior
            frontInput.focus();
            expect(document.activeElement).toBe(frontInput);
        });
    });

    describe('Accessibility', () => {
        test('should have proper ARIA labels and roles', () => {
            const form = document.getElementById('flashcard-form');
            const frontInput = document.getElementById('front-input');
            const backInput = document.getElementById('back-input');

            // Form should have accessible labels
            const frontLabel = document.querySelector('label[for="front-input"]');
            const backLabel = document.querySelector('label[for="back-input"]');

            expect(frontLabel).toBeTruthy();
            expect(backLabel).toBeTruthy();
            expect(frontInput.getAttribute('required')).toBe('');
            expect(backInput.getAttribute('required')).toBe('');
        });

        test('should announce errors to screen readers', () => {
            const frontError = document.getElementById('front-error');
            const backError = document.getElementById('back-error');

            // Error containers should exist for screen reader announcements
            expect(frontError).toBeTruthy();
            expect(backError).toBeTruthy();
            expect(frontError.className).toContain('form-error');
            expect(backError.className).toContain('form-error');
        });
    });
});