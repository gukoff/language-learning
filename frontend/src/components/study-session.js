/**
 * StudySession component for flashcard study functionality.
 */

import { apiClient } from '../services/api-client.js';

export class StudySession {
    constructor(container) {
        this.container = container;
        this.sessionId = null;
        this.currentFlashcard = null;
        this.sessionData = null;
        this.isRevealed = false;
        this.startTime = null;
        
        this.init();
    }

    /**
     * Initialize the study session component
     */
    init() {
        this.render();
        this.setupEventListeners();
    }

    /**
     * Render the study session interface
     */
    render() {
        this.container.innerHTML = `
            <div class="study-session">
                <div class="study-header">
                    <h2>Study Session</h2>
                    <button id="study-back-btn" aria-label="Back to main menu">← Back</button>
                </div>
                
                <div id="study-content">
                    <div id="study-start-screen" class="study-screen">
                        <h3>Ready to Study?</h3>
                        <p>Start a study session to review your flashcards.</p>
                        <button id="start-study-btn" class="btn-primary">Start Study Session</button>
                    </div>
                    
                    <div id="study-session-screen" class="study-screen hidden">
                        <div class="study-progress">
                            <div id="progress-info"></div>
                            <div class="progress-bar">
                                <div id="progress-fill" class="progress-fill"></div>
                            </div>
                        </div>
                        
                        <div class="flashcard-display">
                            <div class="flashcard" id="study-flashcard">
                                <div class="flashcard-content">
                                    <div id="flashcard-side" class="flashcard-side">
                                        <span id="side-label">Front:</span>
                                        <p id="flashcard-text"></p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="study-controls">
                            <button id="show-answer-btn" class="btn-secondary">Show Answer</button>
                            <div id="response-controls" class="response-controls hidden">
                                <p>How did you do?</p>
                                <button id="incorrect-btn" class="btn-incorrect">Incorrect</button>
                                <button id="correct-btn" class="btn-correct">Correct</button>
                            </div>
                        </div>
                    </div>
                    
                    <div id="study-complete-screen" class="study-screen hidden">
                        <h3>Study Session Complete!</h3>
                        <div id="final-stats"></div>
                        <button id="new-study-btn" class="btn-primary">Start New Session</button>
                    </div>
                    
                    <div id="study-error-screen" class="study-screen hidden">
                        <h3>No Flashcards Available</h3>
                        <p>Create some flashcards first before starting a study session.</p>
                        <button id="create-flashcards-btn" class="btn-primary">Create Flashcards</button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Set up event listeners for study session controls
     */
    setupEventListeners() {
        // Back button
        const backBtn = document.getElementById('study-back-btn');
        backBtn?.addEventListener('click', () => this.handleBack());

        // Start study session
        const startBtn = document.getElementById('start-study-btn');
        startBtn?.addEventListener('click', () => this.startStudySession());

        // Show answer
        const showAnswerBtn = document.getElementById('show-answer-btn');
        showAnswerBtn?.addEventListener('click', () => this.showAnswer());

        // Response buttons
        const correctBtn = document.getElementById('correct-btn');
        const incorrectBtn = document.getElementById('incorrect-btn');
        correctBtn?.addEventListener('click', () => this.submitResponse(true));
        incorrectBtn?.addEventListener('click', () => this.submitResponse(false));

        // New study session
        const newStudyBtn = document.getElementById('new-study-btn');
        newStudyBtn?.addEventListener('click', () => this.startStudySession());

        // Create flashcards (from error screen)
        const createBtn = document.getElementById('create-flashcards-btn');
        createBtn?.addEventListener('click', () => this.handleCreateFlashcards());
    }

    /**
     * Start a new study session
     */
    async startStudySession() {
        try {
            this.showLoading();
            
            // Start session via API
            const response = await apiClient.post('/api/study/start');
            this.sessionId = response.session_id;
            this.sessionData = response;
            
            // Load first flashcard
            await this.loadCurrentFlashcard();
            
            this.showStudyScreen();
            
        } catch (error) {
            console.error('Failed to start study session:', error);
            if (error.message?.includes('No flashcards available')) {
                this.showErrorScreen();
            } else {
                this.showError('Failed to start study session. Please try again.');
            }
        }
    }

    /**
     * Load the current flashcard for the session
     */
    async loadCurrentFlashcard() {
        try {
            this.currentFlashcard = await apiClient.get(`/api/study/${this.sessionId}/current`);
            this.sessionData = await apiClient.get(`/api/study/${this.sessionId}/progress`);
            
            this.displayFlashcard();
            this.updateProgress();
            this.startTime = Date.now();
            
        } catch (error) {
            if (error.message?.includes('Study session is complete')) {
                await this.completeSession();
            } else {
                throw error;
            }
        }
    }

    /**
     * Display the current flashcard
     */
    displayFlashcard() {
        const sideLabel = document.getElementById('side-label');
        const flashcardText = document.getElementById('flashcard-text');
        const showAnswerBtn = document.getElementById('show-answer-btn');
        const responseControls = document.getElementById('response-controls');

        if (!this.currentFlashcard) return;

        // Show front side
        sideLabel.textContent = 'Front:';
        flashcardText.textContent = this.currentFlashcard.front;
        
        // Reset state
        this.isRevealed = false;
        showAnswerBtn.classList.remove('hidden');
        responseControls.classList.add('hidden');
        
        // Update flashcard styling
        const flashcard = document.getElementById('study-flashcard');
        flashcard.classList.remove('revealed');
    }

    /**
     * Show the answer (back side) of the flashcard
     */
    showAnswer() {
        const sideLabel = document.getElementById('side-label');
        const flashcardText = document.getElementById('flashcard-text');
        const showAnswerBtn = document.getElementById('show-answer-btn');
        const responseControls = document.getElementById('response-controls');

        // Show back side
        sideLabel.textContent = 'Back:';
        flashcardText.textContent = this.currentFlashcard.back;
        
        // Update UI
        this.isRevealed = true;
        showAnswerBtn.classList.add('hidden');
        responseControls.classList.remove('hidden');
        
        // Update flashcard styling
        const flashcard = document.getElementById('study-flashcard');
        flashcard.classList.add('revealed');
    }

    /**
     * Submit user response (correct/incorrect)
     */
    async submitResponse(isCorrect) {
        try {
            const responseTime = (Date.now() - this.startTime) / 1000;
            
            await apiClient.post(`/api/study/${this.sessionId}/respond`, {
                is_correct: isCorrect,
                response_time_seconds: responseTime
            });
            
            // Load next flashcard or complete session
            await this.loadCurrentFlashcard();
            
        } catch (error) {
            console.error('Failed to submit response:', error);
            this.showError('Failed to submit response. Please try again.');
        }
    }

    /**
     * Complete the study session
     */
    async completeSession() {
        try {
            await apiClient.post(`/api/study/${this.sessionId}/complete`);
            this.showCompleteScreen();
        } catch (error) {
            console.error('Failed to complete session:', error);
            this.showCompleteScreen(); // Show completion even if API call fails
        }
    }

    /**
     * Update progress display
     */
    updateProgress() {
        const progressInfo = document.getElementById('progress-info');
        const progressFill = document.getElementById('progress-fill');

        if (!this.sessionData?.progress) return;

        const { current_card, total_cards, cards_completed, correct_responses, accuracy_percentage } = this.sessionData.progress;
        
        progressInfo.innerHTML = `
            Card ${current_card} of ${total_cards} | 
            Completed: ${cards_completed} | 
            Correct: ${correct_responses} | 
            Accuracy: ${accuracy_percentage.toFixed(1)}%
        `;
        
        const progressPercent = (cards_completed / total_cards) * 100;
        progressFill.style.width = `${progressPercent}%`;
    }

    /**
     * Show different screens
     */
    showStudyScreen() {
        this.hideAllScreens();
        document.getElementById('study-session-screen')?.classList.remove('hidden');
    }

    showCompleteScreen() {
        this.hideAllScreens();
        
        const completeScreen = document.getElementById('study-complete-screen');
        const finalStats = document.getElementById('final-stats');
        
        if (this.sessionData?.progress) {
            const { cards_completed, correct_responses, incorrect_responses, accuracy_percentage } = this.sessionData.progress;
            finalStats.innerHTML = `
                <div class="final-stats">
                    <h4>Session Results</h4>
                    <p><strong>Cards Studied:</strong> ${cards_completed}</p>
                    <p><strong>Correct Answers:</strong> ${correct_responses}</p>
                    <p><strong>Incorrect Answers:</strong> ${incorrect_responses}</p>
                    <p><strong>Final Accuracy:</strong> ${accuracy_percentage.toFixed(1)}%</p>
                </div>
            `;
        }
        
        completeScreen?.classList.remove('hidden');
    }

    showErrorScreen() {
        this.hideAllScreens();
        document.getElementById('study-error-screen')?.classList.remove('hidden');
    }

    showStartScreen() {
        this.hideAllScreens();
        document.getElementById('study-start-screen')?.classList.remove('hidden');
    }

    hideAllScreens() {
        const screens = document.querySelectorAll('.study-screen');
        screens.forEach(screen => screen.classList.add('hidden'));
    }

    showLoading() {
        // Could add a loading indicator here
        this.showStartScreen();
    }

    showError(message) {
        // Simple error display - could be enhanced
        alert(message);
    }

    /**
     * Handle navigation back to main menu
     */
    handleBack() {
        if (this.onBack) {
            this.onBack();
        }
    }

    /**
     * Handle navigation to create flashcards
     */
    handleCreateFlashcards() {
        if (this.onCreateFlashcards) {
            this.onCreateFlashcards();
        }
    }

    /**
     * Set callback for back navigation
     */
    setBackCallback(callback) {
        this.onBack = callback;
    }

    /**
     * Set callback for create flashcards navigation
     */
    setCreateFlashcardsCallback(callback) {
        this.onCreateFlashcards = callback;
    }

    /**
     * Reset the study session component
     */
    reset() {
        this.sessionId = null;
        this.currentFlashcard = null;
        this.sessionData = null;
        this.isRevealed = false;
        this.startTime = null;
        this.showStartScreen();
    }
}