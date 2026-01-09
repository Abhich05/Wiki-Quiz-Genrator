// API Configuration
const API_BASE_URL = 'https://wiki-quiz-genrator-btjx.onrender.com';
// For local development, use: const API_BASE_URL = 'http://localhost:8000';

// Global state
let currentQuizData = null;
let currentQuizId = null;
let userAnswers = {};
let quizStartTime = null;

// ======================
// TAB MANAGEMENT
// ======================

function switchTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Add active class to selected button
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Load history if switching to history tab
    if (tabName === 'history') {
        loadHistory();
    }
}

// ======================
// GENERATE QUIZ (TAB 1)
// ======================

async function generateQuiz() {
    const urlInput = document.getElementById('wiki-url');
    const url = urlInput.value.trim();
    
    if (!url) {
        showError('Please enter a Wikipedia URL');
        return;
    }
    
    if (!url.includes('wikipedia.org/wiki/')) {
        showError('Please enter a valid Wikipedia URL');
        return;
    }
    
    // Show loading state
    showLoading();
    hideError();
    hideQuizDisplay();
    
    const generateBtn = document.getElementById('generate-btn');
    const btnText = generateBtn.querySelector('.btn-text');
    const btnSpinner = generateBtn.querySelector('.btn-spinner');
    
    generateBtn.disabled = true;
    btnText.style.display = 'none';
    btnSpinner.style.display = 'inline';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/generate-quiz`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to generate quiz');
        }
        
        const data = await response.json();
        currentQuizData = data;
        currentQuizId = data.id;
        
        displayQuiz(data);
        hideLoading();
        
    } catch (error) {
        console.error('Error generating quiz:', error);
        showError(error.message || 'Failed to generate quiz. Please try again.');
        hideLoading();
    } finally {
        generateBtn.disabled = false;
        btnText.style.display = 'inline';
        btnSpinner.style.display = 'none';
    }
}

function displayQuiz(data) {
    // Show quiz display section
    const quizDisplay = document.getElementById('quiz-display');
    quizDisplay.style.display = 'block';
    
    // Scroll to quiz display
    quizDisplay.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Article Header
    document.getElementById('article-title').textContent = data.title;
    document.getElementById('article-summary').textContent = data.summary;
    document.getElementById('article-url').href = data.url;
    document.getElementById('question-count').textContent = `${data.quiz.length} questions`;
    
    // Key Entities
    displayEntities('people-entities', data.key_entities.people);
    displayEntities('org-entities', data.key_entities.organizations);
    displayEntities('location-entities', data.key_entities.locations);
    
    // Sections
    displaySections(data.sections);
    
    // Related Topics
    displayRelatedTopics(data.related_topics);
}

function displayEntities(containerId, entities) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    
    if (!entities || entities.length === 0) {
        container.innerHTML = '<span class="entity-tag empty">None found</span>';
        return;
    }
    
    entities.forEach(entity => {
        const tag = document.createElement('span');
        tag.className = 'entity-tag';
        tag.textContent = entity;
        container.appendChild(tag);
    });
}

function displaySections(sections) {
    const container = document.getElementById('sections-container');
    container.innerHTML = '';
    
    if (!sections || sections.length === 0) {
        container.innerHTML = '<p class="empty-message">No sections found</p>';
        return;
    }
    
    sections.forEach(section => {
        const sectionCard = document.createElement('div');
        sectionCard.className = 'section-card';
        sectionCard.innerHTML = `
            <h4 class="section-name">${escapeHtml(section.title)}</h4>
            <p class="section-level">Level ${section.level}</p>
        `;
        container.appendChild(sectionCard);
    });
}

function displayRelatedTopics(topics) {
    const container = document.getElementById('related-topics');
    container.innerHTML = '';
    
    if (!topics || topics.length === 0) {
        container.innerHTML = '<p class="empty-message">No related topics found</p>';
        return;
    }
    
    topics.forEach(topic => {
        const topicCard = document.createElement('a');
        topicCard.className = 'related-card';
        topicCard.href = '#';
        topicCard.onclick = (e) => {
            e.preventDefault();
            loadRelatedTopic(topic);
        };
        topicCard.innerHTML = `
            <span class="related-icon">🔗</span>
            <span class="related-title">${escapeHtml(topic)}</span>
            <span class="related-arrow">→</span>
        `;
        container.appendChild(topicCard);
    });
}

function loadRelatedTopic(topic) {
    const url = `https://en.wikipedia.org/wiki/${topic.replace(/ /g, '_')}`;
    document.getElementById('wiki-url').value = url;
    generateQuiz();
}

// ======================
// STUDY GUIDE MODE
// ======================

function viewAsStudyGuide() {
    const studyGuide = document.getElementById('study-guide');
    const studyQuestions = document.getElementById('study-questions');
    
    if (!currentQuizData || !currentQuizData.quiz) {
        return;
    }
    
    studyGuide.style.display = 'block';
    studyQuestions.innerHTML = '';
    
    currentQuizData.quiz.forEach((q, index) => {
        const questionCard = document.createElement('div');
        questionCard.className = 'study-question-card';
        questionCard.innerHTML = `
            <div class="question-header">
                <span class="question-number">Question ${index + 1}</span>
                <span class="difficulty-badge difficulty-${q.difficulty.toLowerCase()}">${q.difficulty}</span>
            </div>
            <h4 class="question-text">${escapeHtml(q.question)}</h4>
            <div class="options-list">
                <div class="option ${q.correct_answer === 'A' ? 'correct-option' : ''}">
                    <span class="option-letter">A)</span>
                    <span>${escapeHtml(q.option_a)}</span>
                    ${q.correct_answer === 'A' ? '<span class="check-icon">✓</span>' : ''}
                </div>
                <div class="option ${q.correct_answer === 'B' ? 'correct-option' : ''}">
                    <span class="option-letter">B)</span>
                    <span>${escapeHtml(q.option_b)}</span>
                    ${q.correct_answer === 'B' ? '<span class="check-icon">✓</span>' : ''}
                </div>
                <div class="option ${q.correct_answer === 'C' ? 'correct-option' : ''}">
                    <span class="option-letter">C)</span>
                    <span>${escapeHtml(q.option_c)}</span>
                    ${q.correct_answer === 'C' ? '<span class="check-icon">✓</span>' : ''}
                </div>
                <div class="option ${q.correct_answer === 'D' ? 'correct-option' : ''}">
                    <span class="option-letter">D)</span>
                    <span>${escapeHtml(q.option_d)}</span>
                    ${q.correct_answer === 'D' ? '<span class="check-icon">✓</span>' : ''}
                </div>
            </div>
            <div class="explanation-box">
                <strong>Explanation:</strong> ${escapeHtml(q.explanation)}
                ${q.section_reference ? `<br><em>Section: ${escapeHtml(q.section_reference)}</em>` : ''}
            </div>
        `;
        studyQuestions.appendChild(questionCard);
    });
    
    studyGuide.scrollIntoView({ behavior: 'smooth' });
}

// ======================
// QUIZ TAKING MODE
// ======================

function startTakingQuiz() {
    if (!currentQuizData || !currentQuizData.quiz) {
        return;
    }
    
    // Hide quiz display, show quiz taking mode
    document.getElementById('quiz-display').style.display = 'none';
    document.getElementById('quiz-taking').style.display = 'block';
    document.getElementById('quiz-results').style.display = 'none';
    
    // Reset state
    userAnswers = {};
    quizStartTime = Date.now();
    
    // Render questions
    renderQuizQuestions();
    
    // Scroll to top
    document.getElementById('quiz-taking').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderQuizQuestions() {
    const container = document.getElementById('quiz-questions-container');
    container.innerHTML = '';
    
    currentQuizData.quiz.forEach((q, index) => {
        const questionCard = document.createElement('div');
        questionCard.className = 'quiz-question-card';
        questionCard.id = `question-${index}`;
        questionCard.innerHTML = `
            <div class="question-header">
                <span class="question-number">Question ${index + 1} of ${currentQuizData.quiz.length}</span>
                <span class="difficulty-badge difficulty-${q.difficulty.toLowerCase()}">${q.difficulty}</span>
            </div>
            <h4 class="question-text">${escapeHtml(q.question)}</h4>
            <div class="options-list">
                <label class="option-label">
                    <input type="radio" name="question-${index}" value="A" onchange="selectAnswer(${index}, 'A')">
                    <span class="option-content">
                        <span class="option-letter">A)</span>
                        <span>${escapeHtml(q.option_a)}</span>
                    </span>
                </label>
                <label class="option-label">
                    <input type="radio" name="question-${index}" value="B" onchange="selectAnswer(${index}, 'B')">
                    <span class="option-content">
                        <span class="option-letter">B)</span>
                        <span>${escapeHtml(q.option_b)}</span>
                    </span>
                </label>
                <label class="option-label">
                    <input type="radio" name="question-${index}" value="C" onchange="selectAnswer(${index}, 'C')">
                    <span class="option-content">
                        <span class="option-letter">C)</span>
                        <span>${escapeHtml(q.option_c)}</span>
                    </span>
                </label>
                <label class="option-label">
                    <input type="radio" name="question-${index}" value="D" onchange="selectAnswer(${index}, 'D')">
                    <span class="option-content">
                        <span class="option-letter">D)</span>
                        <span>${escapeHtml(q.option_d)}</span>
                    </span>
                </label>
            </div>
        `;
        container.appendChild(questionCard);
    });
    
    updateProgress();
}

function selectAnswer(questionIndex, answer) {
    userAnswers[questionIndex] = answer;
    updateProgress();
}

function updateProgress() {
    const totalQuestions = currentQuizData.quiz.length;
    const answeredQuestions = Object.keys(userAnswers).length;
    const percentage = (answeredQuestions / totalQuestions) * 100;
    
    document.getElementById('progress-text').textContent = 
        `${answeredQuestions} of ${totalQuestions} questions answered`;
    document.getElementById('progress-fill').style.width = `${percentage}%`;
}

async function submitQuizAnswers() {
    const totalQuestions = currentQuizData.quiz.length;
    const answeredQuestions = Object.keys(userAnswers).length;
    
    if (answeredQuestions < totalQuestions) {
        if (!confirm(`You've only answered ${answeredQuestions} out of ${totalQuestions} questions. Submit anyway?`)) {
            return;
        }
    }
    
    const timeSpent = Math.floor((Date.now() - quizStartTime) / 1000); // seconds
    
    // Prepare answers array
    const answers = {};
    currentQuizData.quiz.forEach((q, index) => {
        answers[index.toString()] = userAnswers[index] || '';
    });
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/quiz/attempt`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                quiz_id: currentQuizId,
                answers: answers,
                time_taken: timeSpent
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to submit quiz');
        }
        
        const result = await response.json();
        displayQuizResults(result, answers);
        
    } catch (error) {
        console.error('Error submitting quiz:', error);
        alert('Failed to submit quiz. Please try again.');
    }
}

function displayQuizResults(result, submittedAnswers) {
    // Hide quiz taking, show results
    document.getElementById('quiz-taking').style.display = 'none';
    document.getElementById('quiz-results').style.display = 'block';
    
    // Display score
    const percentage = result.percentage;
    document.getElementById('result-percentage').textContent = `${percentage}%`;
    document.getElementById('result-fraction').textContent = `${result.score}/${result.total_questions}`;
    
    // Animate score ring
    const circumference = 2 * Math.PI * 90;
    const offset = circumference - (percentage / 100) * circumference;
    const ring = document.getElementById('score-ring-fill');
    ring.style.strokeDasharray = circumference;
    ring.style.strokeDashoffset = offset;
    
    // Display detailed results
    const detailsContainer = document.getElementById('results-details');
    detailsContainer.innerHTML = '<h3>Detailed Results</h3>';
    
    currentQuizData.quiz.forEach((q, index) => {
        const userAnswer = submittedAnswers[index.toString()] || 'No answer';
        const isCorrect = userAnswer === q.correct_answer;
        
        const resultCard = document.createElement('div');
        resultCard.className = `result-item ${isCorrect ? 'correct' : 'incorrect'}`;
        resultCard.innerHTML = `
            <div class="result-header">
                <span class="result-icon">${isCorrect ? '✅' : '❌'}</span>
                <span class="result-question-num">Question ${index + 1}</span>
            </div>
            <p class="result-question">${escapeHtml(q.question)}</p>
            <div class="result-answers">
                <p><strong>Your answer:</strong> ${userAnswer} - ${escapeHtml(getOptionText(q, userAnswer))}</p>
                ${!isCorrect ? `<p><strong>Correct answer:</strong> ${q.correct_answer} - ${escapeHtml(getOptionText(q, q.correct_answer))}</p>` : ''}
            </div>
            <div class="result-explanation">
                <strong>Explanation:</strong> ${escapeHtml(q.explanation)}
            </div>
        `;
        detailsContainer.appendChild(resultCard);
    });
    
    // Scroll to results
    document.getElementById('quiz-results').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function getOptionText(question, answer) {
    const optionMap = {
        'A': question.option_a,
        'B': question.option_b,
        'C': question.option_c,
        'D': question.option_d
    };
    return optionMap[answer] || 'No answer';
}

function retakeQuiz() {
    startTakingQuiz();
}

function exitQuiz() {
    if (Object.keys(userAnswers).length > 0) {
        if (!confirm('Are you sure you want to exit? Your progress will be lost.')) {
            return;
        }
    }
    backToArticle();
}

function backToArticle() {
    document.getElementById('quiz-taking').style.display = 'none';
    document.getElementById('quiz-results').style.display = 'none';
    document.getElementById('quiz-display').style.display = 'block';
    document.getElementById('quiz-display').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ======================
// HISTORY TAB
// ======================

async function loadHistory() {
    const loadingEl = document.getElementById('history-loading');
    const emptyEl = document.getElementById('history-empty');
    const tableEl = document.getElementById('history-table-wrapper');
    
    loadingEl.style.display = 'block';
    emptyEl.style.display = 'none';
    tableEl.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/quizzes`);
        
        if (!response.ok) {
            throw new Error('Failed to load history');
        }
        
        const quizzes = await response.json();
        
        loadingEl.style.display = 'none';
        
        if (!quizzes || quizzes.length === 0) {
            emptyEl.style.display = 'block';
            return;
        }
        
        displayHistory(quizzes);
        tableEl.style.display = 'block';
        
    } catch (error) {
        console.error('Error loading history:', error);
        loadingEl.style.display = 'none';
        emptyEl.style.display = 'block';
    }
}

function displayHistory(quizzes) {
    const tbody = document.getElementById('history-tbody');
    tbody.innerHTML = '';
    
    quizzes.forEach(quiz => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="title-cell">${escapeHtml(quiz.title)}</td>
            <td class="url-cell">
                <a href="${escapeHtml(quiz.url)}" target="_blank" class="url-link">
                    ${truncateUrl(quiz.url)}
                </a>
            </td>
            <td class="count-cell">${quiz.total_questions}</td>
            <td class="date-cell">${formatDate(quiz.created_at)}</td>
            <td class="actions-cell">
                <button onclick="viewQuizDetails(${quiz.id})" class="btn-view">
                    👁️ View
                </button>
                <button onclick="deleteQuiz(${quiz.id})" class="btn-delete">
                    🗑️ Delete
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

async function viewQuizDetails(quizId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/quiz/${quizId}`);
        
        if (!response.ok) {
            throw new Error('Failed to load quiz details');
        }
        
        const quiz = await response.json();
        showQuizModal(quiz);
        
    } catch (error) {
        console.error('Error loading quiz details:', error);
        alert('Failed to load quiz details');
    }
}

function showQuizModal(quiz) {
    const modal = document.getElementById('quiz-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    
    modalTitle.textContent = quiz.title;
    
    modalBody.innerHTML = `
        <div class="modal-section">
            <h3>Article Information</h3>
            <p><strong>URL:</strong> <a href="${escapeHtml(quiz.url)}" target="_blank">${escapeHtml(quiz.url)}</a></p>
            <p><strong>Summary:</strong> ${escapeHtml(quiz.summary)}</p>
        </div>
        
        <div class="modal-section">
            <h3>Key Entities</h3>
            <div class="entities-modal">
                <div><strong>People:</strong> ${quiz.key_entities.people.join(', ') || 'None'}</div>
                <div><strong>Organizations:</strong> ${quiz.key_entities.organizations.join(', ') || 'None'}</div>
                <div><strong>Locations:</strong> ${quiz.key_entities.locations.join(', ') || 'None'}</div>
            </div>
        </div>
        
        <div class="modal-section">
            <h3>Quiz Questions (${quiz.quiz.length})</h3>
            ${quiz.quiz.map((q, i) => `
                <div class="modal-question">
                    <h4>Question ${i + 1}</h4>
                    <p>${escapeHtml(q.question)}</p>
                    <ul class="modal-options">
                        <li class="${q.correct_answer === 'A' ? 'correct' : ''}">A) ${escapeHtml(q.option_a)}</li>
                        <li class="${q.correct_answer === 'B' ? 'correct' : ''}">B) ${escapeHtml(q.option_b)}</li>
                        <li class="${q.correct_answer === 'C' ? 'correct' : ''}">C) ${escapeHtml(q.option_c)}</li>
                        <li class="${q.correct_answer === 'D' ? 'correct' : ''}">D) ${escapeHtml(q.option_d)}</li>
                    </ul>
                    <p class="modal-explanation"><strong>Explanation:</strong> ${escapeHtml(q.explanation)}</p>
                </div>
            `).join('')}
        </div>
        
        <div class="modal-section">
            <h3>Related Topics</h3>
            <p>${quiz.related_topics.join(', ')}</p>
        </div>
    `;
    
    modal.style.display = 'block';
}

function closeQuizModal() {
    document.getElementById('quiz-modal').style.display = 'none';
}

async function deleteQuiz(quizId) {
    if (!confirm('Are you sure you want to delete this quiz?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/quiz/${quizId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete quiz');
        }
        
        // Reload history
        await loadHistory();
        
    } catch (error) {
        console.error('Error deleting quiz:', error);
        alert('Failed to delete quiz');
    }
}

function refreshHistory() {
    loadHistory();
}

// ======================
// UTILITY FUNCTIONS
// ======================

function showLoading() {
    document.getElementById('loading-state').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loading-state').style.display = 'none';
}

function showError(message) {
    const errorEl = document.getElementById('error-state');
    const messageEl = document.getElementById('error-message');
    messageEl.textContent = message;
    errorEl.style.display = 'block';
}

function hideError() {
    document.getElementById('error-state').style.display = 'none';
}

function clearError() {
    hideError();
    hideQuizDisplay();
}

function hideQuizDisplay() {
    document.getElementById('quiz-display').style.display = 'none';
    document.getElementById('quiz-taking').style.display = 'none';
    document.getElementById('quiz-results').style.display = 'none';
    document.getElementById('study-guide').style.display = 'none';
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function truncateUrl(url) {
    if (url.length <= 50) return url;
    return url.substring(0, 47) + '...';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 60) return `${diffMins} min${diffMins !== 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
    
    return date.toLocaleDateString();
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('quiz-modal');
    if (event.target === modal) {
        closeQuizModal();
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('Wikipedia Quiz Generator Enhanced - Ready');
});
