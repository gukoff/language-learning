/**
 * Main application entry point for flashcard learning system.
 */

import { apiClient } from './services/api-client.js';
import { FlashcardCreator } from './components/flashcard-creator.js';
import { StudySession } from './components/study-session.js';

/**
 * Application state and navigation
 */
class FlashcardApp {
    constructor() {
        this.currentView = 'welcome';
        this.currentComponent = null;
        this.init();
    }

    /**
     * Initialize the application
     */
    init() {
        this.setupEventListeners();
        this.showWelcomeScreen();
        this.checkApiHealth();
    }

    /**
     * Set up event listeners for navigation
     */
    setupEventListeners() {
        const createBtn = document.getElementById('create-btn');
        const studyBtn = document.getElementById('study-btn');
        const manageBtn = document.getElementById('manage-btn');

        if (createBtn) {
            createBtn.addEventListener('click', () => this.showCreateView());
        }
        
        if (studyBtn) {
            studyBtn.addEventListener('click', () => this.showStudyView());
        }
        
        if (manageBtn) {
            manageBtn.addEventListener('click', () => this.showManageView());
        }
    }

    /**
     * Show welcome screen
     */
    showWelcomeScreen() {
        this.destroyCurrentComponent();
        
        const appContainer = document.getElementById('app');
        appContainer.innerHTML = `
            <div id="welcome-screen" class="container-sm text-center">
                <h2>Welcome to your flashcard learning system!</h2>
                <p>Get started by creating your first flashcard or start studying existing ones.</p>
                
                <div class="welcome-actions" style="margin: var(--space-8) 0;">
                    <button class="btn btn-primary" onclick="app.showCreateView()" style="margin: var(--space-2);">
                        📝 Create Your First Flashcard
                    </button>
                    <button class="btn btn-secondary" onclick="app.showStudyView()" style="margin: var(--space-2);">
                        📚 Start Studying
                    </button>
                    <button class="btn btn-secondary" onclick="app.showManageView()" style="margin: var(--space-2);">
                        📋 Manage Collection
                    </button>
                </div>
                
                <div id="api-status" class="alert" style="display: none;"></div>
            </div>
        `;
        this.currentView = 'welcome';
    }

    /**
     * Show create flashcard view
     */
    showCreateView() {
        this.destroyCurrentComponent();
        
        const appContainer = document.getElementById('app');
        appContainer.innerHTML = '<div id="create-container"></div>';
        
        const container = document.getElementById('create-container');
        this.currentComponent = new FlashcardCreator(container);
        
        // Set up callbacks
        this.currentComponent.setOnSuccess((flashcard) => {
            this.showSuccess(`Flashcard "${flashcard.front}" created successfully!`);
            // Could redirect to manage view or stay here for more creation
        });
        
        this.currentComponent.setOnCancel(() => {
            this.showWelcomeScreen();
        });
        
        // Focus the first input
        setTimeout(() => {
            this.currentComponent.focus();
        }, 100);
        
        this.currentView = 'create';
    }

    /**
     * Show study view with study session component
     */
    showStudyView() {
        this.destroyCurrentComponent();
        this.currentView = 'study';
        
        const appContainer = document.getElementById('app');
        appContainer.innerHTML = '<div id="study-container"></div>';
        
        // Create and initialize study session component
        const studyContainer = document.getElementById('study-container');
        this.currentComponent = new StudySession(studyContainer);
        
        // Set up navigation callbacks
        this.currentComponent.setBackCallback(() => this.showWelcomeScreen());
        this.currentComponent.setCreateFlashcardsCallback(() => this.showCreateView());
        
        this.updateNavigation();
    }

    /**
     * Show manage collection view (placeholder)
     */
    showManageView() {
        this.destroyCurrentComponent();
        
        const appContainer = document.getElementById('app');
        appContainer.innerHTML = `
            <div class="container-sm">
                <h2>Manage Collection</h2>
                <div class="card">
                    <p>Collection management component will be implemented in User Story 3.</p>
                    <p>This feature will allow you to:</p>
                    <ul>
                        <li>View all your flashcards</li>
                        <li>Edit existing flashcards</li>
                        <li>Delete unwanted flashcards</li>
                        <li>Search and filter your collection</li>
                    </ul>
                    <button class="btn btn-secondary" onclick="app.showWelcomeScreen()">Back to Home</button>
                </div>
            </div>
        `;
        this.currentView = 'manage';
    }

    /**
     * Destroy current component if it exists
     */
    destroyCurrentComponent() {
        if (this.currentComponent && typeof this.currentComponent.destroy === 'function') {
            this.currentComponent.destroy();
            this.currentComponent = null;
        }
    }

    /**
     * Check API health and display status
     */
    async checkApiHealth() {
        const statusElement = document.getElementById('api-status');
        if (!statusElement) return;

        try {
            const health = await apiClient.healthCheck();
            statusElement.className = 'alert alert-success';
            statusElement.innerHTML = `
                <strong>API Status:</strong> Connected ✓
                <br><small>Backend is running and ready</small>
            `;
            statusElement.style.display = 'block';
        } catch (error) {
            statusElement.className = 'alert alert-error';
            statusElement.innerHTML = `
                <strong>API Status:</strong> Disconnected ✗
                <br><small>Backend server is not running. Please start the backend to use the application.</small>
            `;
            statusElement.style.display = 'block';
        }
    }

    /**
     * Show error message to user
     */
    showError(message) {
        const appContainer = document.getElementById('app');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-error';
        errorDiv.textContent = message;
        appContainer.prepend(errorDiv);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    /**
     * Show success message to user
     */
    showSuccess(message) {
        const appContainer = document.getElementById('app');
        const successDiv = document.createElement('div');
        successDiv.className = 'alert alert-success';
        successDiv.textContent = message;
        appContainer.prepend(successDiv);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            successDiv.remove();
        }, 3000);
    }

    /**
     * Navigate to a specific view
     */
    navigateTo(view) {
        switch (view) {
            case 'welcome':
                this.showWelcomeScreen();
                break;
            case 'create':
                this.showCreateView();
                break;
            case 'study':
                this.showStudyView();
                break;
            case 'manage':
                this.showManageView();
                break;
            default:
                this.showWelcomeScreen();
        }
    }

    /**
     * Get current view name
     */
    getCurrentView() {
        return this.currentView;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new FlashcardApp();
});

export { FlashcardApp };