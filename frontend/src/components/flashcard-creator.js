/**
 * FlashcardCreator component for creating new flashcards.
 * Implements User Story 1: Create Flashcards functionality.
 */

import { apiClient, ApiError } from '../services/api-client.js';

export class FlashcardCreator {
    constructor(container) {
        this.container = container;
        this.form = null;
        this.frontInput = null;
        this.backInput = null;
        this.submitButton = null;
        this.cancelButton = null;
        this.feedbackElement = null;
        this.frontError = null;
        this.backError = null;
        
        this.isSubmitting = false;
        this.onSuccess = null;
        this.onCancel = null;
        
        this.init();
    }

    /**
     * Initialize the flashcard creator component
     */
    init() {
        this.render();
        this.setupEventListeners();
        this.setupValidation();
    }

    /**
     * Render the flashcard creation form
     */
    render() {
        this.container.innerHTML = `
            <div class="container-sm">
                <h2>Create New Flashcard</h2>
                <p>Add a new flashcard to your learning collection.</p>
                
                <form id="flashcard-form" class="card">
                    <div class="form-group">
                        <label for="front-input" class="form-label">
                            Front (Question/Prompt) <span aria-label="required">*</span>
                        </label>
                        <input 
                            type="text" 
                            id="front-input" 
                            class="form-input" 
                            maxlength="500" 
                            required
                            placeholder="Enter the question or prompt..."
                            aria-describedby="front-error front-help"
                        >
                        <div id="front-help" class="form-help">
                            <small>What you want to be prompted with during study.</small>
                        </div>
                        <div id="front-error" class="form-error" style="display: none;" role="alert"></div>
                    </div>
                    
                    <div class="form-group">
                        <label for="back-input" class="form-label">
                            Back (Answer/Translation) <span aria-label="required">*</span>
                        </label>
                        <textarea 
                            id="back-input" 
                            class="form-textarea" 
                            maxlength="500" 
                            required
                            placeholder="Enter the answer or translation..."
                            rows="4"
                            aria-describedby="back-error back-help"
                        ></textarea>
                        <div id="back-help" class="form-help">
                            <small>The correct answer or translation to be revealed.</small>
                        </div>
                        <div id="back-error" class="form-error" style="display: none;" role="alert"></div>
                    </div>
                    
                    <div class="form-group">
                        <button type="submit" id="create-btn" class="btn btn-primary">
                            <span class="btn-text">Create Flashcard</span>
                            <span class="btn-loading" style="display: none;">Creating...</span>
                        </button>
                        <button type="button" id="cancel-btn" class="btn btn-secondary">
                            Cancel
                        </button>
                    </div>
                    
                    <div id="creation-feedback" class="alert" style="display: none;" role="alert"></div>
                </form>
                
                <div class="form-tips">
                    <h3>Tips for Effective Flashcards</h3>
                    <ul>
                        <li>Keep questions clear and specific</li>
                        <li>Use simple, memorable answers</li>
                        <li>Include context when helpful</li>
                        <li>Test one concept per card</li>
                    </ul>
                </div>
            </div>
        `;

        // Get references to form elements
        this.form = document.getElementById('flashcard-form');
        this.frontInput = document.getElementById('front-input');
        this.backInput = document.getElementById('back-input');
        this.submitButton = document.getElementById('create-btn');
        this.cancelButton = document.getElementById('cancel-btn');
        this.feedbackElement = document.getElementById('creation-feedback');
        this.frontError = document.getElementById('front-error');
        this.backError = document.getElementById('back-error');
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        }

        if (this.cancelButton) {
            this.cancelButton.addEventListener('click', () => this.handleCancel());
        }

        // Clear errors on input
        if (this.frontInput) {
            this.frontInput.addEventListener('input', () => this.clearFieldError('front'));
            this.frontInput.addEventListener('blur', () => this.validateField('front'));
        }

        if (this.backInput) {
            this.backInput.addEventListener('input', () => this.clearFieldError('back'));
            this.backInput.addEventListener('blur', () => this.validateField('back'));
        }
    }

    /**
     * Set up form validation
     */
    setupValidation() {
        // Add character counters
        this.addCharacterCounter(this.frontInput, 'front-counter');
        this.addCharacterCounter(this.backInput, 'back-counter');
    }

    /**
     * Add character counter to input field
     */
    addCharacterCounter(inputElement, counterId) {
        if (!inputElement) return;

        const counter = document.createElement('div');
        counter.id = counterId;
        counter.className = 'character-counter';
        counter.innerHTML = `<small>0/500 characters</small>`;
        
        inputElement.parentNode.appendChild(counter);

        inputElement.addEventListener('input', () => {
            const length = inputElement.value.length;
            counter.innerHTML = `<small>${length}/500 characters</small>`;
            
            if (length > 450) {
                counter.style.color = 'var(--warning-color)';
            } else {
                counter.style.color = 'var(--gray-500)';
            }
        });
    }

    /**
     * Handle form submission
     */
    async handleSubmit(event) {
        event.preventDefault();
        
        if (this.isSubmitting) return;
        
        // Validate form
        if (!this.validateForm()) {
            return;
        }

        this.setSubmitting(true);
        this.clearAllErrors();

        const frontText = this.frontInput.value.trim();
        const backText = this.backInput.value.trim();

        try {
            const flashcard = await apiClient.createFlashcard({
                front: frontText,
                back: backText
            });

            this.showSuccess('Flashcard created successfully!');
            this.clearForm();
            
            // Notify parent component of success
            if (this.onSuccess) {
                this.onSuccess(flashcard);
            }

        } catch (error) {
            this.handleError(error);
        } finally {
            this.setSubmitting(false);
        }
    }

    /**
     * Handle cancel action
     */
    handleCancel() {
        this.clearForm();
        this.clearAllErrors();
        
        if (this.onCancel) {
            this.onCancel();
        }
    }

    /**
     * Validate the entire form
     */
    validateForm() {
        let isValid = true;

        // Validate front content
        if (!this.validateField('front')) {
            isValid = false;
        }

        // Validate back content
        if (!this.validateField('back')) {
            isValid = false;
        }

        return isValid;
    }

    /**
     * Validate individual field
     */
    validateField(fieldName) {
        const input = fieldName === 'front' ? this.frontInput : this.backInput;
        const errorElement = fieldName === 'front' ? this.frontError : this.backError;
        
        if (!input || !errorElement) return true;

        const value = input.value.trim();
        let errorMessage = '';

        if (!value) {
            errorMessage = `${fieldName === 'front' ? 'Front' : 'Back'} content is required`;
        } else if (value.length > 500) {
            errorMessage = `${fieldName === 'front' ? 'Front' : 'Back'} content is too long (max 500 characters)`;
        }

        if (errorMessage) {
            this.showFieldError(fieldName, errorMessage);
            return false;
        } else {
            this.clearFieldError(fieldName);
            return true;
        }
    }

    /**
     * Show field-specific error
     */
    showFieldError(fieldName, message) {
        const errorElement = fieldName === 'front' ? this.frontError : this.backError;
        const inputElement = fieldName === 'front' ? this.frontInput : this.backInput;
        
        if (errorElement && inputElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
            inputElement.setAttribute('aria-invalid', 'true');
            inputElement.classList.add('error');
        }
    }

    /**
     * Clear field-specific error
     */
    clearFieldError(fieldName) {
        const errorElement = fieldName === 'front' ? this.frontError : this.backError;
        const inputElement = fieldName === 'front' ? this.frontInput : this.backInput;
        
        if (errorElement && inputElement) {
            errorElement.style.display = 'none';
            inputElement.setAttribute('aria-invalid', 'false');
            inputElement.classList.remove('error');
        }
    }

    /**
     * Clear all errors
     */
    clearAllErrors() {
        this.clearFieldError('front');
        this.clearFieldError('back');
        this.hideFeedback();
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        if (this.feedbackElement) {
            this.feedbackElement.className = 'alert alert-success';
            this.feedbackElement.textContent = message;
            this.feedbackElement.style.display = 'block';
            
            // Auto-hide after 3 seconds
            setTimeout(() => {
                this.hideFeedback();
            }, 3000);
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        if (this.feedbackElement) {
            this.feedbackElement.className = 'alert alert-error';
            this.feedbackElement.textContent = message;
            this.feedbackElement.style.display = 'block';
        }
    }

    /**
     * Hide feedback message
     */
    hideFeedback() {
        if (this.feedbackElement) {
            this.feedbackElement.style.display = 'none';
        }
    }

    /**
     * Handle API errors
     */
    handleError(error) {
        let message = 'Failed to create flashcard. Please try again.';

        if (error instanceof ApiError) {
            if (error.isNetworkError()) {
                message = 'Network error. Please check your connection and try again.';
            } else if (error.isClientError()) {
                message = error.message || 'Invalid flashcard data. Please check your input.';
            } else if (error.isServerError()) {
                message = 'Server error. Please try again later.';
            }
        }

        this.showError(message);
    }

    /**
     * Set submitting state
     */
    setSubmitting(submitting) {
        this.isSubmitting = submitting;
        
        if (this.submitButton) {
            const btnText = this.submitButton.querySelector('.btn-text');
            const btnLoading = this.submitButton.querySelector('.btn-loading');
            
            if (submitting) {
                this.submitButton.disabled = true;
                if (btnText) btnText.style.display = 'none';
                if (btnLoading) btnLoading.style.display = 'inline';
            } else {
                this.submitButton.disabled = false;
                if (btnText) btnText.style.display = 'inline';
                if (btnLoading) btnLoading.style.display = 'none';
            }
        }
    }

    /**
     * Clear the form
     */
    clearForm() {
        if (this.frontInput) this.frontInput.value = '';
        if (this.backInput) this.backInput.value = '';
        
        // Update character counters
        const frontCounter = document.getElementById('front-counter');
        const backCounter = document.getElementById('back-counter');
        if (frontCounter) frontCounter.innerHTML = '<small>0/500 characters</small>';
        if (backCounter) backCounter.innerHTML = '<small>0/500 characters</small>';
    }

    /**
     * Set success callback
     */
    setOnSuccess(callback) {
        this.onSuccess = callback;
    }

    /**
     * Set cancel callback
     */
    setOnCancel(callback) {
        this.onCancel = callback;
    }

    /**
     * Focus the first input field
     */
    focus() {
        if (this.frontInput) {
            this.frontInput.focus();
        }
    }

    /**
     * Destroy the component
     */
    destroy() {
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}