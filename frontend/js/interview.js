/**
 * COGNITIVE ASSISTANCE & INTERVIEW PREPARATION BOT
 * Mock Interview Simulator & Socratic Evaluation Controller
 */

const InterviewState = {
  activeSessionId: null,
  turnIndex: 1,
  totalTurns: 3,
  domain: 'Python',
  interviewType: 'technical',
  difficulty: 'intermediate',
  currentQuestion: '',
  hintsUsed: 0,
  hintsRemaining: 3,
  isRecording: false,
  recognition: null,
  timerInterval: null,
  secondsElapsed: 0,
  isCompleted: false
};

document.addEventListener('DOMContentLoaded', () => {
  initDifficultyChips();
  initAnswerInputEvents();
  initSpeechRecognition();
});

// -------------------------------------------------------------
// SETUP & DIFFICULTY SELECTION
// -------------------------------------------------------------
function initDifficultyChips() {
  const chips = document.querySelectorAll('#difficultyChips .chip-btn');
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      chips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      InterviewState.difficulty = chip.getAttribute('data-level');
    });
  });
}

function initAnswerInputEvents() {
  const textarea = document.getElementById('candidateAnswerInput');
  const countEl = document.getElementById('answerWordCount');

  textarea.addEventListener('input', () => {
    const text = textarea.value.trim();
    const words = text ? text.split(/\s+/).length : 0;
    countEl.innerText = `${words} words`;
  });
}

// -------------------------------------------------------------
// SPEECH-TO-TEXT VOICE DICTATION
// -------------------------------------------------------------
function initSpeechRecognition() {
  window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (window.SpeechRecognition) {
    InterviewState.recognition = new window.SpeechRecognition();
    InterviewState.recognition.continuous = true;
    InterviewState.recognition.interimResults = true;

    InterviewState.recognition.onresult = (event) => {
      let finalTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript + ' ';
        }
      }
      if (finalTranscript) {
        const textarea = document.getElementById('candidateAnswerInput');
        textarea.value += (textarea.value ? ' ' : '') + finalTranscript;
        textarea.dispatchEvent(new Event('input'));
      }
    };

    InterviewState.recognition.onerror = (event) => {
      console.warn('Speech recognition error:', event.error);
      stopSpeechRecognition();
    };

    InterviewState.recognition.onend = () => {
      stopSpeechRecognition();
    };
  }
}

function toggleSpeechRecognition() {
  if (!InterviewState.recognition) {
    showToast('Speech recognition not supported in this browser. Please type your response.', 'warning');
    return;
  }

  if (InterviewState.isRecording) {
    stopSpeechRecognition();
  } else {
    try {
      InterviewState.recognition.start();
      InterviewState.isRecording = true;
      const btn = document.getElementById('speechDictateBtn');
      btn.innerHTML = '<i class="fa-solid fa-microphone-slash text-rose"></i> Stop Dictation';
      btn.style.borderColor = 'var(--accent-rose)';
      showToast('Voice dictation active. Speak clearly into your mic...', 'info');
    } catch (e) {
      console.error(e);
    }
  }
}

function stopSpeechRecognition() {
  if (InterviewState.recognition && InterviewState.isRecording) {
    InterviewState.recognition.stop();
  }
  InterviewState.isRecording = false;
  const btn = document.getElementById('speechDictateBtn');
  if (btn) {
    btn.innerHTML = '<i class="fa-solid fa-microphone"></i> Dictate Answer';
    btn.style.borderColor = 'var(--border-glass)';
  }
}

// -------------------------------------------------------------
// TIMER HUD
// -------------------------------------------------------------
function startSessionTimer() {
  clearInterval(InterviewState.timerInterval);
  InterviewState.secondsElapsed = 0;
  updateTimerDisplay();

  InterviewState.timerInterval = setInterval(() => {
    InterviewState.secondsElapsed++;
    updateTimerDisplay();
  }, 1000);
}

function stopSessionTimer() {
  clearInterval(InterviewState.timerInterval);
}

function updateTimerDisplay() {
  const mins = String(Math.floor(InterviewState.secondsElapsed / 60)).padStart(2, '0');
  const secs = String(InterviewState.secondsElapsed % 60).padStart(2, '0');
  const el = document.getElementById('hudTimerText');
  if (el) el.innerHTML = `<i class="fa-regular fa-clock"></i> ${mins}:${secs}`;
}

// -------------------------------------------------------------
// START INTERVIEW SESSION
// -------------------------------------------------------------
async function startInterviewSession() {
  const domain = document.getElementById('interviewDomainSelect').value;
  const interviewType = document.getElementById('interviewTypeSelect').value;

  InterviewState.domain = domain;
  InterviewState.interviewType = interviewType;
  InterviewState.hintsUsed = 0;
  InterviewState.hintsRemaining = 3;
  InterviewState.isCompleted = false;

  const btn = document.getElementById('startInterviewBtn');
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Preparing Interview...';
  btn.disabled = true;

  try {
    const res = await apiRequest('/interview/start', 'POST', {
      domain,
      interview_type: interviewType,
      difficulty: InterviewState.difficulty
    });

    InterviewState.activeSessionId = res.session_id;
    InterviewState.turnIndex = res.turn_index;
    InterviewState.currentQuestion = res.question;

    // Update UI
    document.getElementById('hudDomainText').innerText = res.domain;
    document.getElementById('hudDifficultyText').innerText = res.difficulty.charAt(0).toUpperCase() + res.difficulty.slice(1);
    document.getElementById('hudTurnText').innerText = `Question ${res.turn_index} of ${InterviewState.totalTurns}`;
    document.getElementById('sessionStateBadge').innerText = 'Active';
    document.getElementById('sessionStateBadge').className = 'badge badge-emerald';

    document.getElementById('questionDomainBadge').innerText = `${res.domain} Question`;
    document.getElementById('interviewQuestionText').innerText = res.question;

    // Reset Hints Drawer & Inputs
    document.getElementById('hintsRemainingCount').innerText = '3';
    document.getElementById('hintsDrawer').classList.remove('show');
    document.getElementById('hintsListContainer').innerHTML = '';
    document.getElementById('candidateAnswerInput').value = '';
    document.getElementById('answerWordCount').innerText = '0 words';

    // Hide previous evaluation
    document.getElementById('turnEvaluationCard').classList.remove('show');

    startSessionTimer();
    showToast(`Started ${domain} mock interview! Answer thoughtfully.`, 'success');
  } catch (err) {
    showToast('Failed to start interview: ' + err.message, 'error');
  } finally {
    btn.innerHTML = '<i class="fa-solid fa-rotate"></i> Restart Session';
    btn.disabled = false;
  }
}

// -------------------------------------------------------------
// REQUEST PROGRESSIVE HINTS
// -------------------------------------------------------------
async function requestNextHint() {
  if (!InterviewState.activeSessionId) {
    showToast('Please start an interview session first.', 'warning');
    return;
  }

  if (InterviewState.hintsRemaining <= 0) {
    showToast('No more hints available for this question.', 'info');
    return;
  }

  const nextLevel = InterviewState.hintsUsed + 1;
  const hintBtn = document.getElementById('requestHintBtn');
  hintBtn.disabled = true;

  try {
    const res = await apiRequest('/interview/hint', 'POST', {
      session_id: InterviewState.activeSessionId,
      hint_level: nextLevel
    });

    InterviewState.hintsUsed = res.hint_level;
    InterviewState.hintsRemaining = res.hints_remaining;
    document.getElementById('hintsRemainingCount').innerText = res.hints_remaining;

    // Reveal in drawer
    const drawer = document.getElementById('hintsDrawer');
    drawer.classList.add('show');

    const container = document.getElementById('hintsListContainer');
    const item = document.createElement('div');
    item.className = 'hint-item';
    item.innerHTML = `
      <i class="fa-solid fa-lightbulb text-amber" style="margin-top: 2px;"></i>
      <div>
        <strong style="color: #fde68a;">${res.hint_type}:</strong> ${res.hint}
      </div>
    `;
    container.appendChild(item);

    showToast(`Unlocked ${res.hint_type}`, 'info');
  } catch (err) {
    showToast('Could not fetch hint: ' + err.message, 'error');
  } finally {
    hintBtn.disabled = false;
  }
}

// -------------------------------------------------------------
// SUBMIT ANSWER & EVALUATION
// -------------------------------------------------------------
async function submitCandidateAnswer() {
  if (!InterviewState.activeSessionId) {
    showToast('Please start an interview session first.', 'warning');
    return;
  }

  const answer = document.getElementById('candidateAnswerInput').value.trim();
  if (!answer) {
    showToast('Please write or dictate an answer before submitting.', 'warning');
    return;
  }

  stopSpeechRecognition();

  const submitBtn = document.getElementById('submitAnswerBtn');
  submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Evaluating Response...';
  submitBtn.disabled = true;

  try {
    const evalData = await apiRequest('/interview/evaluate', 'POST', {
      session_id: InterviewState.activeSessionId,
      answer: answer
    });

    renderEvaluationCard(evalData);
    InterviewState.isCompleted = evalData.is_session_completed;

    if (evalData.is_session_completed) {
      stopSessionTimer();
      document.getElementById('sessionStateBadge').innerText = 'Completed';
      document.getElementById('sessionStateBadge').className = 'badge badge-purple';
      showToast('Interview session complete! Your final report is ready.', 'success');
    }
  } catch (err) {
    showToast('Evaluation error: ' + err.message, 'error');
  } finally {
    submitBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Submit Answer for Evaluation';
    submitBtn.disabled = false;
  }
}

function renderEvaluationCard(data) {
  const card = document.getElementById('turnEvaluationCard');
  card.classList.add('show');

  // Metrics
  document.getElementById('metricCorrectness').innerText = `${Math.round(data.score_correctness)}%`;
  document.getElementById('metricClarity').innerText = `${Math.round(data.score_clarity)}%`;
  document.getElementById('metricDepth').innerText = `${Math.round(data.score_depth)}%`;
  document.getElementById('metricOverall').innerText = `${Math.round(data.overall_turn_score)}%`;
  document.getElementById('turnScoreBadge').innerText = `Turn Score: ${Math.round(data.overall_turn_score)}%`;

  // Feedback
  document.getElementById('evalFeedbackText').innerText = data.feedback;

  // Missing Concepts
  const missingContainer = document.getElementById('missingKeywordsPills');
  missingContainer.innerHTML = '';
  if (data.missing_concepts && data.missing_concepts.length > 0) {
    document.getElementById('missingConceptsContainer').style.display = 'block';
    data.missing_concepts.forEach(concept => {
      const pill = document.createElement('span');
      pill.className = 'badge badge-amber';
      pill.innerText = concept.trim();
      missingContainer.appendChild(pill);
    });
  } else {
    document.getElementById('missingConceptsContainer').style.display = 'none';
  }

  // Follow-up
  document.getElementById('evalFollowUpText').innerText = data.follow_up_question || 'Consider how this scales under concurrent write load.';

  // Buttons
  const nextBtn = document.getElementById('nextQuestionBtn');
  const reportBtn = document.getElementById('viewReportBtn');

  if (data.is_session_completed) {
    nextBtn.style.display = 'none';
    reportBtn.style.display = 'inline-flex';
  } else {
    nextBtn.style.display = 'inline-flex';
    reportBtn.style.display = 'none';
    InterviewState.nextQuestionCache = data.next_question;
  }

  // Scroll smoothly to evaluation
  card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// -------------------------------------------------------------
// PROCEED TO NEXT QUESTION
// -------------------------------------------------------------
function proceedToNextQuestion() {
  InterviewState.turnIndex++;
  InterviewState.hintsUsed = 0;
  InterviewState.hintsRemaining = 3;

  document.getElementById('hudTurnText').innerText = `Question ${InterviewState.turnIndex} of ${InterviewState.totalTurns}`;
  document.getElementById('interviewQuestionText').innerText = InterviewState.nextQuestionCache;

  // Reset answer & hints
  document.getElementById('hintsRemainingCount').innerText = '3';
  document.getElementById('hintsDrawer').classList.remove('show');
  document.getElementById('hintsListContainer').innerHTML = '';
  document.getElementById('candidateAnswerInput').value = '';
  document.getElementById('answerWordCount').innerText = '0 words';

  // Hide evaluation card
  document.getElementById('turnEvaluationCard').classList.remove('show');

  // Scroll to question
  document.getElementById('questionBox').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// -------------------------------------------------------------
// PREPARATION REPORT MODAL
// -------------------------------------------------------------
async function viewSessionReport(sessionId = null) {
  const sid = sessionId || InterviewState.activeSessionId;
  if (!sid) {
    showToast('No active interview session to generate report for.', 'warning');
    return;
  }

  try {
    const report = await apiRequest(`/interview/report/${sid}`);
    renderReportModal(report);
  } catch (err) {
    showToast('Failed to load preparation report: ' + err.message, 'error');
  }
}

function renderReportModal(report) {
  document.getElementById('reportReadinessBadge').innerText = report.readiness_level;
  document.getElementById('reportDomainTitle').innerText = `${report.domain} ${report.interview_type.toUpperCase()} Mock Interview`;
  document.getElementById('reportDateSubtitle').innerText = `Completed • Candidate: ${report.user_email}`;
  document.getElementById('reportOverallScore').innerText = `${Math.round(report.overall_score)}%`;
  document.getElementById('reportGrade').innerText = report.grade;

  document.getElementById('reportMetricCorrectness').innerText = `${Math.round(report.metric_averages.correctness || 0)}%`;
  document.getElementById('reportMetricClarity').innerText = `${Math.round(report.metric_averages.clarity || 0)}%`;
  document.getElementById('reportMetricDepth').innerText = `${Math.round(report.metric_averages.depth || 0)}%`;
  document.getElementById('reportMetricTurns').innerText = report.turns_evaluated;

  document.getElementById('reportSummaryText').innerText = report.summary_feedback;

  // Strengths
  const strengthsEl = document.getElementById('reportStrengthsList');
  strengthsEl.innerHTML = '';
  report.key_strengths.forEach(s => {
    const li = document.createElement('li');
    li.innerText = s;
    strengthsEl.appendChild(li);
  });

  // Recommended Topics
  const topicsEl = document.getElementById('reportTopicsList');
  topicsEl.innerHTML = '';
  report.recommended_topics.forEach(t => {
    const li = document.createElement('li');
    li.innerText = t;
    topicsEl.appendChild(li);
  });

  document.getElementById('reportModal').classList.add('active');
}

function closeReportModal() {
  document.getElementById('reportModal').classList.remove('active');
}
