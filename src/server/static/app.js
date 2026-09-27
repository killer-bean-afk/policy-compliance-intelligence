// Policy Compliance Intelligence - Client Application
document.addEventListener('DOMContentLoaded', () => {
  let activeDossier = null;
  let presetScenarios = [];

  // --- 1. Tab Navigation ---
  const navTabs = document.querySelectorAll('.nav-tab');
  const tabContents = document.querySelectorAll('.tab-content');

  navTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      navTabs.forEach(t => t.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active-content'));

      tab.classList.add('active');
      const targetId = tab.getAttribute('data-tab');
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add('active-content');
      }

      // Lazy load tab data
      if (targetId === 'policiesTab') loadPolicies();
      if (targetId === 'evalTab') loadEvaluations();
      if (targetId === 'archTab') renderArchitectureDiagram();
    });
  });

  // Dossier Subtabs
  const subtabBtns = document.querySelectorAll('.subtab-btn');
  const subtabContents = document.querySelectorAll('.subtab-content');
  subtabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      subtabBtns.forEach(b => b.classList.remove('active'));
      subtabContents.forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      const targetSub = document.getElementById(btn.getAttribute('data-subtab'));
      if (targetSub) targetSub.classList.add('active');
    });
  });

  // --- 2. Load Preset Scenarios ---
  async function loadPresetScenarios() {
    try {
      const res = await fetch('/api/scenarios');
      if (!res.ok) return;
      presetScenarios = await res.json();
      const select = document.getElementById('scenarioPresetSelect');
      select.innerHTML = '<option value="">-- Choose a realistic scenario --</option>';

      presetScenarios.forEach((s, idx) => {
        const opt = document.createElement('option');
        opt.value = idx;
        opt.textContent = `[${s.domain}] ${s.title}`;
        select.appendChild(opt);
      });

      select.addEventListener('change', (e) => {
        const val = e.target.value;
        if (val !== "") {
          const scn = presetScenarios[parseInt(val)];
          document.getElementById('scenarioInput').value = scn.text;
        }
      });
    } catch (err) {
      console.warn("Could not load preset scenarios:", err);
    }
  }

  // Quick Chips
  document.querySelectorAll('.chip-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const hint = btn.getAttribute('data-hint');
      let targetScn = null;
      if (hint === 'kyc') targetScn = presetScenarios.find(s => s.scenario_id === 'SCN-KYC-01');
      if (hint === 'dpa') targetScn = presetScenarios.find(s => s.scenario_id === 'SCN-PRV-01');
      if (hint === 'root') targetScn = presetScenarios.find(s => s.scenario_id === 'SCN-SEC-01');
      if (hint === 'ai') targetScn = presetScenarios.find(s => s.scenario_id === 'SCN-GOV-01');
      if (hint === 'insider') targetScn = presetScenarios.find(s => s.scenario_id === 'SCN-FIN-01');
      if (hint === 'phi') targetScn = presetScenarios.find(s => s.scenario_id === 'SCN-BIO-01');

      if (targetScn) {
        document.getElementById('scenarioInput').value = targetScn.text;
      }
    });
  });

  // --- 3. Multi-Agent Analysis Execution ---
  const runBtn = document.getElementById('runAnalysisBtn');
  const agentLogOutput = document.getElementById('agentLogOutput');
  const workflowStatusBadge = document.getElementById('workflowStatusBadge');
  const executionTimer = document.getElementById('executionTimer');

  const nodes = {
    RETRIEVAL: document.getElementById('agentNodeRetrieval'),
    ANALYSIS: document.getElementById('agentNodeAnalysis'),
    RISK_ASSESSMENT: document.getElementById('agentNodeRisk'),
    VALIDATION: document.getElementById('agentNodeValidation'),
    RECOMMENDATION: document.getElementById('agentNodeRecommend')
  };

  function resetAgentNodes() {
    Object.values(nodes).forEach(n => {
      if (n) {
        n.classList.remove('active-node', 'completed-node');
      }
    });
  }

  function appendLog(lineHtml, cssClass = '') {
    const div = document.createElement('div');
    div.className = `log-line ${cssClass}`;
    div.innerHTML = lineHtml;
    agentLogOutput.appendChild(div);
    agentLogOutput.scrollTop = agentLogOutput.scrollHeight;
  }

  runBtn.addEventListener('click', async () => {
    const text = document.getElementById('scenarioInput').value.trim();
    if (!text) {
      alert("Please enter a business scenario or select a pre-loaded template.");
      return;
    }

    runBtn.disabled = true;
    runBtn.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="spin">
        <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-linecap="round" />
      </svg>
      <span>Analyzing...</span>
    `;

    resetAgentNodes();
    agentLogOutput.innerHTML = '';
    workflowStatusBadge.textContent = "Multi-Agent Workflow Running...";
    workflowStatusBadge.style.color = "var(--accent-blue)";
    document.getElementById('dossierResultsContainer').style.display = 'none';

    const tStart = performance.now();
    const timerInterval = setInterval(() => {
      const elapsed = Math.round(performance.now() - tStart);
      executionTimer.textContent = `${elapsed} ms`;
    }, 50);

    appendLog(`[ORCHESTRATOR] Initializing Multi-Agent Compliance Pipeline for scenario...`, 'text-muted');

    try {
      // Step-by-step visual progression
      nodes.RETRIEVAL.classList.add('active-node');
      appendLog(`[A2A BUS] Dispatching intent vector to <b>Policy Retrieval Agent</b>...`, 'agent-retrieval');

      const response = await fetch('/api/compliance/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario: text })
      });

      if (!response.ok) {
        throw new Error(`Server returned error ${response.status}`);
      }

      const dossier = await response.json();
      activeDossier = dossier;

      // Animate traces sequentially
      const stageMap = {
        'RETRIEVAL': nodes.RETRIEVAL,
        'ANALYSIS': nodes.ANALYSIS,
        'RISK_ASSESSMENT': nodes.RISK_ASSESSMENT,
        'VALIDATION': nodes.VALIDATION,
        'RECOMMENDATION': nodes.RECOMMENDATION
      };

      for (const trace of dossier.agent_trace) {
        const node = stageMap[trace.stage];
        if (node) {
          node.classList.remove('active-node');
          node.classList.add('completed-node');
        }
        let cssClass = 'text-muted';
        if (trace.stage === 'RETRIEVAL') cssClass = 'agent-retrieval';
        if (trace.stage === 'ANALYSIS') cssClass = 'agent-analysis';
        if (trace.stage === 'RISK_ASSESSMENT') cssClass = 'agent-risk';
        if (trace.stage === 'VALIDATION') cssClass = 'agent-validation';
        if (trace.stage === 'RECOMMENDATION') cssClass = 'agent-recommend';

        appendLog(`[${trace.agent_name.toUpperCase()}] ${trace.action}: ${trace.output_summary} (${trace.execution_time_ms}ms, Conf: ${(trace.confidence*100).toFixed(0)}%)`, cssClass);
      }

      // Display A2A handoffs
      for (const msg of dossier.a2a_messages) {
        if (msg.handoff_reason) {
          appendLog(`[HANDOFF] <b>${msg.sender}</b> &rarr; <b>${msg.receiver}</b>: <i>"${msg.handoff_reason}"</i>`, 'handoff-line');
        }
      }

      clearInterval(timerInterval);
      const totalElapsed = Math.round(performance.now() - tStart);
      executionTimer.textContent = `${totalElapsed} ms`;
      workflowStatusBadge.textContent = "Workflow Complete";
      workflowStatusBadge.style.color = "var(--status-success)";
      appendLog(`[ORCHESTRATOR] Compliance Dossier generated successfully (${totalElapsed} ms).`, 'text-success');

      // Render Dossier
      renderDossier(dossier);

    } catch (err) {
      clearInterval(timerInterval);
      appendLog(`[ERROR] Multi-Agent Workflow failed: ${err.message}`, 'log-line text-danger');
      workflowStatusBadge.textContent = "Execution Error";
      workflowStatusBadge.style.color = "var(--status-danger)";
    } finally {
      runBtn.disabled = false;
      runBtn.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"/></svg>
        <span>Run Multi-Agent Analysis</span>
      `;
    }
  });

  // --- 4. Render Dossier Function ---
  function renderDossier(dossier) {
    const container = document.getElementById('dossierResultsContainer');
    container.style.display = 'flex';

    // Verdict Badge
    const badge = document.getElementById('verdictBadge');
    badge.className = 'verdict-badge-large';
    badge.textContent = dossier.verdict;

    if (dossier.verdict === 'COMPLIANT') {
      badge.classList.add('compliant');
    } else if (dossier.verdict === 'NON_COMPLIANT') {
      badge.classList.add('non-compliant');
    } else {
      badge.classList.add('conditional');
    }

    document.getElementById('verdictTitle').textContent = `Dossier Ref: ${dossier.analysis_id}`;
    document.getElementById('verdictSummary').textContent = dossier.executive_summary;

    // Policies pills
    const policiesRow = document.getElementById('applicablePoliciesTags');
    policiesRow.innerHTML = '';
    dossier.applicable_policies.forEach(p => {
      const span = document.createElement('span');
      span.className = 'policy-pill';
      span.textContent = p;
      policiesRow.appendChild(span);
    });

    // KPI values
    const riskElem = document.getElementById('kpiRiskScore');
    riskElem.textContent = `${dossier.risk_score}/100`;
    if (dossier.risk_score >= 70) riskElem.style.color = 'var(--status-danger)';
    else if (dossier.risk_score >= 40) riskElem.style.color = 'var(--status-warn)';
    else riskElem.style.color = 'var(--status-success)';

    document.getElementById('kpiRiskLevel').textContent = `${dossier.risk_level} Exposure`;
    document.getElementById('kpiFaithfulness').textContent = `${(dossier.validation.grounding_faithfulness_score * 100).toFixed(1)}%`;
    document.getElementById('kpiAuditStatus').textContent = dossier.validation.is_valid ? 'Grounding Certified' : 'Review Required';

    // Counts on badges
    document.getElementById('clauseCountBadge').textContent = dossier.clause_assessments.length;
    document.getElementById('gapCountBadge').textContent = dossier.identified_gaps.length;
    document.getElementById('remedCountBadge').textContent = dossier.recommendations.length;

    // Subtab 1: Clauses Table
    const tbody = document.getElementById('clausesTableBody');
    tbody.innerHTML = '';
    dossier.clause_assessments.forEach(ca => {
      const tr = document.createElement('tr');
      const vClass = ca.verdict === 'COMPLIANT' ? 'compliant' : (ca.verdict === 'NON_COMPLIANT' ? 'non-compliant' : 'conditional');
      tr.innerHTML = `
        <td>
          <span class="citation-badge">${ca.citation}</span><br/>
          <span style="font-size:0.75rem; color:var(--text-dim);">${ca.clause_id}</span>
        </td>
        <td>
          <strong style="color:var(--text-main);">${ca.policy_name}</strong><br/>
          <span style="font-size:0.78rem; color:var(--text-muted);">${ca.section}</span>
        </td>
        <td>
          <span class="status-badge ${vClass}">${ca.verdict}</span>
        </td>
        <td>
          <div>${ca.reasoning}</div>
          <div class="evidence-quote-box"><b>Evidence:</b> <i>"${ca.evidence_quote}"</i></div>
        </td>
      `;
      tbody.appendChild(tr);
    });

    // Subtab 2: Gaps & Risk Factors
    const gapsUl = document.getElementById('gapsList');
    gapsUl.innerHTML = '';
    if (dossier.identified_gaps.length === 0) {
      gapsUl.innerHTML = '<li class="text-muted text-sm">No critical compliance gaps identified. Standard procedural controls apply.</li>';
    } else {
      dossier.identified_gaps.forEach(g => {
        const li = document.createElement('li');
        li.className = 'gap-item';
        li.innerHTML = `
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          <span>${g}</span>
        `;
        gapsUl.appendChild(li);
      });
    }

    const rfContainer = document.getElementById('riskFactorsList');
    rfContainer.innerHTML = '';
    if (dossier.risk_factors.length === 0) {
      rfContainer.innerHTML = '<div class="text-muted text-sm">Zero critical risk exposure factors logged.</div>';
    } else {
      dossier.risk_factors.forEach(rf => {
        const card = document.createElement('div');
        card.className = 'risk-factor-card';
        card.innerHTML = `
          <div class="risk-factor-header">
            <span class="risk-factor-title">${rf.risk_title}</span>
            <span class="badge" style="background:rgba(239,68,68,0.15); color:#F87171; border:1px solid rgba(239,68,68,0.3);">${rf.severity}</span>
          </div>
          <div style="font-size:0.75rem; color:var(--text-dim);">
            Ref: <span class="citation-badge">${rf.clause_reference}</span> &nbsp;|&nbsp; 
            Reg: <b>${rf.regulatory_frameworks.join(', ')}</b> &nbsp;|&nbsp;
            Impact: <b>${rf.impact}</b> &nbsp;|&nbsp; Likelihood: <b>${rf.likelihood}</b>
          </div>
          <div class="risk-penalties-text">${rf.potential_penalties}</div>
        `;
        rfContainer.appendChild(card);
      });
    }

    // Subtab 3: Remediation Grid
    const remGrid = document.getElementById('remediationGrid');
    remGrid.innerHTML = '';
    dossier.recommendations.forEach(r => {
      const card = document.createElement('div');
      card.className = 'remediation-card';
      card.innerHTML = `
        <div class="rem-top-row">
          <span class="rem-action-id">${r.action_id}</span>
          <span class="badge" style="background:rgba(56,189,248,0.15); color:var(--accent-blue);">${r.priority} PRIORITY</span>
        </div>
        <label class="rem-checkbox-label">
          <input type="checkbox" class="rem-checkbox" />
          <span class="rem-title">${r.title}</span>
        </label>
        <p class="rem-desc">${r.description}</p>
        <div class="rem-meta-bar">
          <span>Owner: <b>${r.responsible_party}</b></span>
          <span>Approval: <b>${r.approval_required}</b></span>
          <span>SLA: <b>${r.deadline_days}d</b></span>
        </div>
      `;
      remGrid.appendChild(card);
    });

    // Subtab 4: Validation Certificate
    const certBox = document.getElementById('certificateBox');
    certBox.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <h3 style="color:var(--accent-purple);">Evidentiary Grounding & Hallucination Audit Certificate</h3>
        <span class="badge" style="background:rgba(168,85,247,0.2); color:#C084FC; border:1px solid rgba(168,85,247,0.4);">
          ${dossier.validation.is_valid ? 'VERIFIED & CERTIFIED' : 'REVIEW REQUIRED'}
        </span>
      </div>
      <p style="font-size:0.9rem; line-height:1.6; color:var(--text-main); margin-bottom:14px;">
        ${dossier.validation.validator_notes}
      </p>
      <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:12px; font-size:0.8rem; background:rgba(30,41,59,0.5); padding:12px; border-radius:8px;">
        <div><b>Grounding Faithfulness:</b> <span class="text-accent">${(dossier.validation.grounding_faithfulness_score * 100).toFixed(1)}%</span></div>
        <div><b>Evidence Coverage:</b> <span class="text-success">${(dossier.validation.evidence_coverage_ratio * 100).toFixed(1)}%</span></div>
        <div><b>Unsupported Claims:</b> <span class="text-cyan">${dossier.validation.unsupported_claims.length}</span></div>
      </div>
    `;

    // Smooth scroll down to dossier
    container.scrollIntoView({ behavior: 'smooth' });
  }

  // PDF Export
  document.getElementById('exportPdfBtn').addEventListener('click', async () => {
    if (!activeDossier) return;
    try {
      const btn = document.getElementById('exportPdfBtn');
      btn.textContent = "Generating PDF...";
      const res = await fetch('/api/reports/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(activeDossier)
      });
      const data = await res.json();
      btn.textContent = "Export PDF Audit Report";
      if (data.download_url) {
        window.open(data.download_url, '_blank');
      }
    } catch (err) {
      alert("Failed to export PDF: " + err.message);
    }
  });

  // Copy JSON
  document.getElementById('copyJsonBtn').addEventListener('click', () => {
    if (!activeDossier) return;
    navigator.clipboard.writeText(JSON.stringify(activeDossier, null, 2));
    const btn = document.getElementById('copyJsonBtn');
    const old = btn.innerHTML;
    btn.innerHTML = `<span>Copied to Clipboard!</span>`;
    setTimeout(() => { btn.innerHTML = old; }, 2000);
  });

  // --- 5. Natural Language Evidence Search (Task 2) ---
  const nlSearchBtn = document.getElementById('nlSearchBtn');
  const nlSearchInput = document.getElementById('nlSearchInput');
  const searchResultsStats = document.getElementById('searchResultsStats');
  const evidenceResultsList = document.getElementById('evidenceResultsList');

  async function executeSearch() {
    const q = nlSearchInput.value.trim();
    if (!q) return;

    evidenceResultsList.innerHTML = '<div class="text-muted text-sm">Searching knowledge base...</div>';
    searchResultsStats.style.display = 'none';

    try {
      const cat = document.getElementById('filterCategory').value;
      const topK = parseInt(document.getElementById('filterTopK').value) || 5;

      const res = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q, category: cat || null, top_k: topK })
      });

      const data = await res.json();
      searchResultsStats.style.display = 'flex';
      document.getElementById('searchResultCount').textContent = `${data.total_found} relevant clauses found`;
      document.getElementById('searchResultTime').textContent = `in ${data.retrieval_time_ms} ms (Hybrid Dense/BM25)`;

      evidenceResultsList.innerHTML = '';
      if (data.results.length === 0) {
        evidenceResultsList.innerHTML = '<div class="text-muted text-sm">No policy clauses matched your search query.</div>';
        return;
      }

      data.results.forEach(ev => {
        const card = document.createElement('div');
        card.className = 'evidence-card';
        card.innerHTML = `
          <div class="evidence-top">
            <div>
              <span class="citation-badge">${ev.citation_tag}</span>
              <strong style="margin-left:8px; font-size:0.95rem;">${ev.clause.policy_name}</strong>
            </div>
            <div style="display:flex; gap:6px;">
              <span class="score-tag">Score: ${(ev.score*100).toFixed(0)}%</span>
              <span class="score-tag" style="background:rgba(99,102,241,0.12); color:var(--accent-indigo);">Dense: ${(ev.dense_score*100).toFixed(0)}%</span>
            </div>
          </div>
          <div style="font-size:0.84rem; font-weight:600; color:var(--accent-blue); margin-bottom:4px;">
            Section ${ev.clause.section_number}: ${ev.clause.section_title}
          </div>
          <p style="font-size:0.86rem; color:var(--text-main); line-height:1.5;">${ev.clause.clause_text}</p>
          <div style="display:flex; justify-content:space-between; align-items:center; margin-top:10px; font-size:0.75rem; color:var(--text-dim);">
            <span>Regulatory Standard: <b>${ev.clause.regulatory_framework}</b></span>
            <span>Category: <b>${ev.clause.category}</b></span>
            <span>Severity: <b>${ev.clause.penalty_severity}</b></span>
          </div>
        `;
        evidenceResultsList.appendChild(card);
      });

    } catch (err) {
      evidenceResultsList.innerHTML = `<div class="text-danger text-sm">Search failed: ${err.message}</div>`;
    }
  }

  nlSearchBtn.addEventListener('click', executeSearch);
  nlSearchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') executeSearch();
  });

  // --- 6. Policy Explorer (Task 1) ---
  let policiesLoaded = false;
  async function loadPolicies() {
    if (policiesLoaded) return;
    const grid = document.getElementById('policiesGrid');
    grid.innerHTML = '<div class="text-muted text-sm">Loading policy directives...</div>';

    try {
      const res = await fetch('/api/policies');
      const data = await res.json();
      grid.innerHTML = '';

      // Populate Category filter in Search Tab
      const catSelect = document.getElementById('filterCategory');
      const cats = Array.from(new Set(data.policies.map(p => p.category)));
      catSelect.innerHTML = '<option value="">All Categories</option>';
      cats.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c;
        opt.textContent = c;
        catSelect.appendChild(opt);
      });

      data.policies.forEach(p => {
        const card = document.createElement('div');
        card.className = 'glass-card policy-doc-card';
        card.innerHTML = `
          <div class="policy-doc-header">
            <div>
              <span class="policy-code">${p.policy_id}</span>
              <h3 style="font-size:1.05rem; font-weight:700; margin-top:2px;">${p.policy_name}</h3>
            </div>
            <a href="/api/policies/${p.policy_id}/pdf" target="_blank" class="btn btn-secondary" style="padding:6px 12px; font-size:0.75rem;">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/></svg>
              PDF
            </a>
          </div>
          <div class="policy-meta-row">
            <span>Category: <b>${p.category}</b></span>
            <span>Area: <b>${p.business_area}</b></span>
          </div>
          <p style="font-size:0.82rem; color:var(--text-muted); line-height:1.4;">${p.description}</p>
          <div style="margin-top:auto; padding-top:8px; border-top:1px solid rgba(255,255,255,0.06); display:flex; justify-content:space-between; font-size:0.75rem; color:var(--text-dim);">
            <span>Owner: <b>${p.owner}</b></span>
            <span><b>${p.clause_count} clauses</b> (v${p.version})</span>
          </div>
        `;
        grid.appendChild(card);
      });

      policiesLoaded = true;
    } catch (err) {
      grid.innerHTML = `<div class="text-danger text-sm">Failed to load policies: ${err.message}</div>`;
    }
  }

  // --- 7. Benchmark Suite Runner (Task 4) ---
  const runEvalSuiteBtn = document.getElementById('runEvalSuiteBtn');
  async function loadEvaluations() {
    // If not executed yet, auto-run or display cached results
    runBenchmark();
  }

  async function runBenchmark() {
    runEvalSuiteBtn.disabled = true;
    runEvalSuiteBtn.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="spin">
        <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-linecap="round" />
      </svg>
      <span>Evaluating Scenarios...</span>
    `;

    try {
      const res = await fetch('/api/evaluation/run', { method: 'POST' });
      const summary = await res.json();

      document.getElementById('metricMrr').textContent = `${(summary.retrieval_mrr * 100).toFixed(1)}%`;
      document.getElementById('metricRecall').textContent = `${(summary.retrieval_recall_at_5 * 100).toFixed(1)}%`;
      document.getElementById('metricAccuracy').textContent = `${(summary.verdict_accuracy * 100).toFixed(1)}%`;
      document.getElementById('metricRiskCalib').textContent = `${(summary.risk_calibration_score * 100).toFixed(1)}%`;
      document.getElementById('metricFaithfulness').textContent = `${(summary.average_faithfulness_score * 100).toFixed(1)}%`;
      document.getElementById('metricLatency').textContent = `~${summary.average_latency_ms.toFixed(0)} ms`;

      const tbody = document.getElementById('evalTableBody');
      tbody.innerHTML = '';

      summary.scenario_results.forEach(sr => {
        const tr = document.createElement('tr');
        const pass = sr.verdict_match && sr.risk_match;
        tr.innerHTML = `
          <td><strong style="color:var(--accent-blue);">${sr.scenario_id}</strong></td>
          <td>
            <strong>${sr.title}</strong><br/>
            <span style="font-size:0.75rem; color:var(--text-dim);">${sr.domain}</span>
          </td>
          <td><span class="status-badge ${sr.expected_verdict.toLowerCase()}">${sr.expected_verdict}</span></td>
          <td><span class="status-badge ${sr.actual_verdict.toLowerCase()}">${sr.actual_verdict}</span></td>
          <td>
            <span class="badge" style="background:${pass ? 'rgba(16,185,129,0.15)' : 'rgba(245,158,11,0.15)'}; color:${pass ? 'var(--status-success)' : 'var(--status-warn)'};">
              ${pass ? 'PASS' : 'WARN'}
            </span>
          </td>
          <td>${(sr.retrieval_mrr * 100).toFixed(0)}%</td>
          <td>${(sr.grounding_faithfulness * 100).toFixed(1)}%</td>
          <td>${sr.latency_ms.toFixed(0)} ms</td>
        `;
        tbody.appendChild(tr);
      });

    } catch (err) {
      console.error("Evaluation run failed:", err);
    } finally {
      runEvalSuiteBtn.disabled = false;
      runEvalSuiteBtn.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"/></svg>
        <span>Run Live Benchmark Suite</span>
      `;
    }
  }

  runEvalSuiteBtn.addEventListener('click', runBenchmark);

  // --- 8. Architecture Diagram SVG Renderer (Task 5) ---
  function renderArchitectureDiagram() {
    const container = document.getElementById('architectureDiagramContainer');
    container.innerHTML = `
      <svg width="1000" height="420" viewBox="0 0 1000 420" fill="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="gradBlue" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#0284C7"/><stop offset="100%" stop-color="#2563EB"/></linearGradient>
          <linearGradient id="gradPurple" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#7C3AED"/><stop offset="100%" stop-color="#9333EA"/></linearGradient>
          <linearGradient id="gradGreen" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#059669"/><stop offset="100%" stop-color="#10B981"/></linearGradient>
          <linearGradient id="gradCard" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#1E293B"/><stop offset="100%" stop-color="#0F172A"/></linearGradient>
          <filter id="shadow" x="-5" y="-5" width="110%" height="115%"><feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000" flood-opacity="0.4"/></filter>
        </defs>

        <!-- Stage 1: Ingestion & Knowledge Base -->
        <rect x="20" y="40" width="220" height="340" rx="14" fill="url(#gradCard)" stroke="#334155" stroke-width="1.5" filter="url(#shadow)"/>
        <text x="40" y="70" fill="#38BDF8" font-family="'Outfit', sans-serif" font-weight="700" font-size="14">STAGE 1: KNOWLEDGE BASE</text>
        <text x="40" y="90" fill="#94A3B8" font-size="10">Policy Data Prep & Indexing (Task 1)</text>

        <rect x="36" y="110" width="188" height="50" rx="8" fill="#111827" stroke="#475569"/>
        <text x="48" y="132" fill="#F8FAFC" font-weight="600" font-size="11">PDF Policy Library</text>
        <text x="48" y="148" fill="#94A3B8" font-size="9">7 Directives • 34 Structured Clauses</text>

        <rect x="36" y="175" width="188" height="50" rx="8" fill="#111827" stroke="#475569"/>
        <text x="48" y="197" fill="#F8FAFC" font-weight="600" font-size="11">Dense Vector Embeddings</text>
        <text x="48" y="213" fill="#94A3B8" font-size="9">all-MiniLM-L6-v2 (384-d, Offline)</text>

        <rect x="36" y="240" width="188" height="50" rx="8" fill="#111827" stroke="#475569"/>
        <text x="48" y="262" fill="#F8FAFC" font-weight="600" font-size="11">Sparse Lexical BM25</text>
        <text x="48" y="278" fill="#94A3B8" font-size="9">Exact Sublinear Term Frequencies</text>

        <rect x="36" y="305" width="188" height="50" rx="8" fill="#111827" stroke="#475569"/>
        <text x="48" y="327" fill="#F8FAFC" font-weight="600" font-size="11">SQLite Metadata Store</text>
        <text x="48" y="343" fill="#94A3B8" font-size="9">Categories, Owners, Severity Weights</text>

        <!-- Arrow 1 to 2 -->
        <path d="M 240 210 L 290 210" stroke="#38BDF8" stroke-width="2" stroke-dasharray="4" marker-end="url(#arrow)"/>
        <polygon points="290,210 282,205 282,215" fill="#38BDF8"/>

        <!-- Stage 2: Hybrid Retrieval -->
        <rect x="290" y="40" width="220" height="340" rx="14" fill="url(#gradCard)" stroke="#334155" stroke-width="1.5" filter="url(#shadow)"/>
        <text x="310" y="70" fill="#818CF8" font-family="'Outfit', sans-serif" font-weight="700" font-size="14">STAGE 2: EVIDENCE RETRIEVAL</text>
        <text x="310" y="90" fill="#94A3B8" font-size="10">Hybrid Search & Grounding (Task 2)</text>

        <rect x="306" y="115" width="188" height="60" rx="8" fill="#111827" stroke="#475569"/>
        <text x="318" y="138" fill="#F8FAFC" font-weight="600" font-size="11">Reciprocal Rank Fusion</text>
        <text x="318" y="154" fill="#94A3B8" font-size="9">RRF(d) = Σ w / (k + rank_i)</text>
        <text x="318" y="168" fill="#38BDF8" font-size="8">Combines Dense Semantic + BM25</text>

        <rect x="306" y="195" width="188" height="60" rx="8" fill="#111827" stroke="#475569"/>
        <text x="318" y="218" fill="#F8FAFC" font-weight="600" font-size="11">Citation Engine</text>
        <text x="318" y="234" fill="#94A3B8" font-size="9">Extracts [POL-XXX §X.X] Tags</text>
        <text x="318" y="248" fill="#34D399" font-size="8">Traceable Verbatim Excerpts</text>

        <rect x="306" y="275" width="188" height="70" rx="8" fill="#111827" stroke="#475569"/>
        <text x="318" y="298" fill="#F8FAFC" font-weight="600" font-size="11">Candidate Filtering</text>
        <text x="318" y="314" fill="#94A3B8" font-size="9">Domain Metadata Filtering</text>
        <text x="318" y="328" fill="#FCD34D" font-size="8">Relevance Thresholding (&gt;0.28)</text>

        <!-- Arrow 2 to 3 -->
        <path d="M 510 210 L 560 210" stroke="#818CF8" stroke-width="2" stroke-dasharray="4"/>
        <polygon points="560,210 552,205 552,215" fill="#818CF8"/>

        <!-- Stage 3: Multi-Agent Workflow -->
        <rect x="560" y="40" width="420" height="340" rx="14" fill="url(#gradCard)" stroke="#334155" stroke-width="1.5" filter="url(#shadow)"/>
        <text x="580" y="70" fill="#34D399" font-family="'Outfit', sans-serif" font-weight="700" font-size="14">STAGE 3: MULTI-AGENT WORKFLOW & A2A BUS</text>
        <text x="580" y="90" fill="#94A3B8" font-size="10">Specialist Agents, Risk Scoring & Validation (Task 3)</text>

        <!-- 5 Agent Nodes -->
        <rect x="576" y="110" width="185" height="42" rx="7" fill="#111827" stroke="#0284C7"/>
        <text x="588" y="128" fill="#38BDF8" font-weight="700" font-size="10">1. Policy Retrieval Agent</text>
        <text x="588" y="142" fill="#94A3B8" font-size="8">Intent decomposition & candidate search</text>

        <rect x="780" y="110" width="185" height="42" rx="7" fill="#111827" stroke="#EAB308"/>
        <text x="792" y="128" fill="#FCD34D" font-weight="700" font-size="10">2. Compliance Analysis Agent</text>
        <text x="792" y="142" fill="#94A3B8" font-size="8">Clause condition & gap evaluation</text>

        <rect x="576" y="165" width="185" height="42" rx="7" fill="#111827" stroke="#EF4444"/>
        <text x="588" y="183" fill="#F87171" font-weight="700" font-size="10">3. Risk Assessment Agent</text>
        <text x="588" y="197" fill="#94A3B8" font-size="8">Penalty matrix (GDPR, FinCEN, SEC)</text>

        <rect x="780" y="165" width="185" height="42" rx="7" fill="#111827" stroke="#A855F7"/>
        <text x="792" y="183" fill="#C084FC" font-weight="700" font-size="10">4. Validation Agent</text>
        <text x="792" y="197" fill="#94A3B8" font-size="8">Grounding verification (98% faith)</text>

        <rect x="678" y="220" width="185" height="42" rx="7" fill="#111827" stroke="#10B981"/>
        <text x="690" y="238" fill="#34D399" font-weight="700" font-size="10">5. Recommendation Agent</text>
        <text x="690" y="252" fill="#94A3B8" font-size="8">Remediation checklist & executive report</text>

        <!-- A2A Message Bus Bar -->
        <rect x="576" y="280" width="388" height="85" rx="8" fill="#070A10" stroke="#334155"/>
        <text x="590" y="300" fill="#38BDF8" font-family="'JetBrains Mono', monospace" font-size="9" font-weight="700">A2A Message Bus & Dynamic Escalation Protocol</text>
        <text x="590" y="318" fill="#64748B" font-family="'JetBrains Mono', monospace" font-size="8">Payload: {sender, receiver, stage, citations, gaps, risk_score}</text>
        <text x="590" y="332" fill="#64748B" font-family="'JetBrains Mono', monospace" font-size="8">Handoffs: Dynamic routing on High/Critical regulatory exposure</text>
        <text x="590" y="348" fill="#10B981" font-family="'JetBrains Mono', monospace" font-size="8">Output: Comprehensive Audit Dossier & PDF Export (Task 4)</text>
      </svg>
    `;
  }

  // --- Initial Boot ---
  loadPresetScenarios();
  loadPolicies();
});
