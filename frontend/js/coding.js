/**
 * COGNITIVE ASSISTANCE & INTERVIEW PREPARATION BOT
 * Coding Lab & Progressive Socratic Hints Controller
 */

let currentCodingProblem = null;
let codingProblemsCache = [];

async function loadCodingProblems() {
  const container = document.getElementById('problemsListContainer');
  if (!container) return;

  try {
    const problems = await apiRequest('/coding/problems');
    codingProblemsCache = problems;
    renderCodingProblemsList(problems);

    if (problems.length > 0 && !currentCodingProblem) {
      selectCodingProblem(problems[0].id);
    }
  } catch (err) {
    console.error('Failed to load coding problems:', err);
  }
}

function renderCodingProblemsList(problems) {
  const container = document.getElementById('problemsListContainer');
  container.innerHTML = '';

  problems.forEach(prob => {
    const item = document.createElement('div');
    item.className = `problem-card-item ${currentCodingProblem && currentCodingProblem.id === prob.id ? 'active' : ''}`;
    item.id = `probItem_${prob.id}`;
    item.onclick = () => selectCodingProblem(prob.id);

    const diffBadge = prob.difficulty === 'Easy' ? 'badge-emerald' : (prob.difficulty === 'Medium' ? 'badge-amber' : 'badge-purple');

    item.innerHTML = `
      <h4>
        <span>${prob.title}</span>
        <span class="badge ${diffBadge}">${prob.difficulty}</span>
      </h4>
      <div style="font-size: 0.75rem; color: var(--text-dim); display: flex; justify-content: space-between;">
        <span>${prob.category}</span>
        <span>4-Step Hints</span>
      </div>
    `;
    container.appendChild(item);
  });
}

async function selectCodingProblem(problemId) {
  try {
    const problem = await apiRequest(`/coding/problem/${problemId}`);
    currentCodingProblem = problem;

    // Highlight sidebar
    document.querySelectorAll('.problem-card-item').forEach(el => el.classList.remove('active'));
    const activeEl = document.getElementById(`probItem_${problemId}`);
    if (activeEl) activeEl.classList.add('active');

    // Update Header & Details
    document.getElementById('codingProblemTitle').innerText = problem.title;
    document.getElementById('codingProblemDifficulty').innerText = problem.difficulty;
    document.getElementById('codingProblemCategory').innerText = problem.category;

    // Render formatted description & examples
    let descHtml = `<p>${problem.description}</p>`;
    if (problem.examples && problem.examples.length > 0) {
      descHtml += `<div style="margin-top: 0.75rem; font-weight: 600; color: #fff;">Examples:</div>`;
      problem.examples.forEach((ex, idx) => {
        descHtml += `
          <div style="background: rgba(0,0,0,0.3); border-radius: var(--radius-sm); padding: 0.5rem 0.75rem; margin-top: 0.35rem; font-family: var(--font-code); font-size: 0.8rem; border-left: 2px solid var(--accent-cyan);">
            <div><strong>Input:</strong> ${ex.input}</div>
            <div><strong>Output:</strong> ${ex.output}</div>
            ${ex.explanation ? `<div style="color: var(--text-muted); font-size: 0.75rem;">${ex.explanation}</div>` : ''}
          </div>
        `;
      });
    }

    if (problem.constraints && problem.constraints.length > 0) {
      descHtml += `<div style="margin-top: 0.75rem; font-weight: 600; color: #fff;">Constraints:</div><ul style="margin-left: 1.25rem; font-size: 0.8rem; color: var(--text-muted);">`;
      problem.constraints.forEach(c => {
        descHtml += `<li><code>${c}</code></li>`;
      });
      descHtml += `</ul>`;
    }

    document.getElementById('codingProblemDescription').innerHTML = descHtml;

    // Populate Starter Code in Scratchpad
    const starter = problem.starter_code?.python || '# Write your solution here\n';
    document.getElementById('codingScratchpad').value = starter;

    // Reset hints accordion
    for (let i = 1; i <= 4; i++) {
      const content = document.getElementById(`hintContent${i}`);
      content.classList.remove('active');
      content.innerHTML = '<span style="color: var(--text-dim);"><i class="fa-solid fa-spinner fa-spin"></i> Loading guidance...</span>';
      const icon = document.getElementById(`hintIcon${i}`);
      if (icon) icon.className = 'fa-solid fa-chevron-down';
    }

  } catch (err) {
    showToast('Failed to load problem details: ' + err.message, 'error');
  }
}

function resetCodingProblemCode() {
  if (currentCodingProblem && currentCodingProblem.starter_code?.python) {
    document.getElementById('codingScratchpad').value = currentCodingProblem.starter_code.python;
    showToast('Code reset to starter template.', 'info');
  }
}

async function toggleCodingHintStep(stepNumber) {
  if (!currentCodingProblem) return;

  const contentEl = document.getElementById(`hintContent${stepNumber}`);
  const iconEl = document.getElementById(`hintIcon${stepNumber}`);
  const isCurrentlyOpen = contentEl.classList.contains('active');

  if (isCurrentlyOpen) {
    contentEl.classList.remove('active');
    iconEl.className = 'fa-solid fa-chevron-down';
    return;
  }

  // Fetch hint details
  try {
    const hintData = await apiRequest('/coding/hint', 'POST', {
      problem_id: currentCodingProblem.id,
      hint_level: stepNumber
    });

    let html = '';
    if (hintData.code) {
      // Step 4: Code Solution + Line-by-Line Breakdown
      html += `
        <div style="margin-bottom: 0.75rem;">
          <div style="font-weight: 600; color: var(--accent-emerald); margin-bottom: 0.35rem;"><i class="fa-solid fa-check"></i> Optimal Implementation:</div>
          <pre style="background: #080d16; padding: 0.85rem; border-radius: var(--radius-sm); font-family: var(--font-code); font-size: 0.82rem; color: #a5f3fc; overflow-x: auto;"><code>${escapeHtml(hintData.code)}</code></pre>
        </div>
      `;

      if (hintData.breakdown && hintData.breakdown.length > 0) {
        html += `<div style="font-weight: 600; color: #fff; margin-bottom: 0.35rem;"><i class="fa-solid fa-list-check text-cyan"></i> Line-by-Line Architectural Explanation:</div><ul style="margin-left: 1.25rem; font-size: 0.82rem; color: #e5e7eb; line-height: 1.6;">`;
        hintData.breakdown.forEach(b => {
          html += `<li style="margin-bottom: 0.3rem;">${b}</li>`;
        });
        html += `</ul>`;
      }
    } else {
      // Steps 1 - 3: Narrative hints & pseudocode
      html = `<div style="white-space: pre-line;">${hintData.content}</div>`;
    }

    contentEl.innerHTML = html;
    contentEl.classList.add('active');
    iconEl.className = 'fa-solid fa-chevron-up';
  } catch (err) {
    contentEl.innerHTML = `<span style="color: var(--accent-rose);">Failed to retrieve hint.</span>`;
  }
}

function escapeHtml(string) {
  return String(string)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
