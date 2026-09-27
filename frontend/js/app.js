/**
 * Policy Compliance Intelligence Platform - Frontend Application Script
 */

const API_BASE = "";

// Global State
let currentResponse = null;
let kbClauses = [];

// DOM Ready Initialization
document.addEventListener("DOMContentLoaded", () => {
  loadKnowledgeBase();
});

// Tab Switching Handler
function switchTab(tabId) {
  document.querySelectorAll(".tab-content").forEach(el => el.classList.remove("active"));
  document.querySelectorAll(".tab-btn").forEach(el => el.classList.remove("active"));

  document.getElementById(tabId).classList.add("active");
  const activeBtn = Array.from(document.querySelectorAll(".tab-btn")).find(btn => btn.getAttribute("onclick").includes(tabId));
  if (activeBtn) activeBtn.classList.add("active");
}

// Quick Preset Scenario Loader
function loadPreset(key) {
  const input = document.getElementById("scenario-input");
  const categorySelect = document.getElementById("category-filter");

  const presets = {
    pep: {
      text: "A new institutional client account is being onboarded for a senior foreign government minister (Politically Exposed Person). The account executive wants to activate the account immediately without completing an Enhanced Due Diligence (EDD) report or securing formal written sign-off from the Money Laundering Reporting Officer (MLRO).",
      category: "KYC / AML"
    },
    hipaa: {
      text: "The health operations team plans to upload 5,000 patient electronic health records (ePHI) to a third-party cloud analytics SaaS vendor to optimize clinical workflow scheduling. No Business Associate Agreement (BAA) has been executed with the vendor.",
      category: "Data Privacy & Healthcare"
    },
    sec: {
      text: "A software engineer pasted 1,500 lines of proprietary payment processing source code into a public web-based generative AI tool to debug an algorithm error.",
      category: "Information Security"
    },
    wire: {
      text: "Treasury initiated an outbound wire transfer of $250,000 USD to a corporate supplier in Eastern Europe without running real-time OFAC SDN sanctions screening or obtaining dual Treasury authorization.",
      category: "Financial Operations"
    },
    fcpa: {
      text: "A sales executive hosted a $500 luxury dinner for a foreign government regulatory inspector to discuss upcoming license approvals, without obtaining prior compliance pre-clearance.",
      category: "Corporate Governance"
    },
    crypto: {
      text: "A business unit attempted to pay an overseas contractor using an unhosted Monero cryptocurrency wallet via an anonymous decentralized privacy protocol.",
      category: "Financial Operations"
    }
  };

  if (presets[key]) {
    input.value = presets[key].text;
    categorySelect.value = presets[key].category;
  }
}

// Run Multi-Agent Compliance Analysis
async function runComplianceAnalysis() {
  const scenarioText = document.getElementById("scenario-input").value.trim();
  const category = document.getElementById("category-filter").value;
  const btn = document.getElementById("btn-analyze");

  if (!scenarioText) {
    alert("Please enter a business scenario or select a preset scenario.");
    return;
  }

  btn.disabled = true;
  btn.innerHTML = `<span>⏳ Analyzing via 5 Agents...</span>`;

  try {
    const res = await fetch(`${API_BASE}/api/analyze-compliance`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        scenario_text: scenarioText,
        policy_category: category || null,
        include_agent_trace: true
      })
    });

    if (!res.ok) {
      throw new Error(`API Error: ${res.statusText}`);
    }

    const data = await res.json();
    currentResponse = data;

    renderResults(data);
    renderA2ATrace(data.agent_execution_trace);
    renderAuditReport(data);

    document.getElementById("results-container").style.display = "block";

  } catch (err) {
    alert(`Error executing compliance analysis: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<span>⚡ Run Multi-Agent Analysis</span>`;
  }
}

// Render Compliance Results to UI
function renderResults(data) {
  // 1. Executive Summary & Badges
  const badgeStatus = document.getElementById("badge-status");
  badgeStatus.textContent = data.overall_compliance_status;
  badgeStatus.className = `badge badge-${data.overall_compliance_status.toLowerCase().replace(" ", "-")}`;

  const badgeRisk = document.getElementById("badge-risk");
  badgeRisk.textContent = `${data.overall_risk_level} RISK`;
  badgeRisk.className = `badge badge-${data.overall_risk_level.toLowerCase()}`;

  document.getElementById("text-latency").textContent = `Latency: ${data.execution_time_ms} ms`;
  document.getElementById("exec-summary-text").textContent = data.executive_summary;

  // 2. Retrieved Policy Evidence Clauses
  const clausesList = document.getElementById("evidence-clauses-list");
  clausesList.innerHTML = data.retrieved_clauses.map(item => `
    <div style="background: rgba(11, 15, 25, 0.6); padding: 0.9rem; border-radius: var(--radius-sm); border: 1px solid var(--border-color); margin-bottom: 0.8rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
        <span style="font-weight: 700; color: #818cf8;">${item.clause.clause_id} - ${item.clause.policy_name}</span>
        <span class="badge" style="background: rgba(99, 102, 241, 0.2); color: #a5b4fc;">Score: ${(item.relevance_score * 100).toFixed(0)}%</span>
      </div>
      <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.4rem;">
        📍 Section ${item.clause.section_number} (${item.clause.section_title}) | Source: 📄 ${item.clause.source_document}
      </div>
      <div style="font-size: 0.85rem; color: #e5e7eb; background: rgba(0,0,0,0.3); padding: 0.6rem; border-radius: 4px;">
        "${item.clause.clause_text}"
      </div>
    </div>
  `).join("");

  // 3. Clause Findings
  const findingsList = document.getElementById("clause-findings-list");
  findingsList.innerHTML = data.clause_analyses.map(a => `
    <div style="margin-bottom: 0.8rem; padding: 0.8rem; border-radius: var(--radius-sm); background: rgba(255,255,255,0.03); border-left: 3px solid ${a.status === 'Compliant' ? '#10b981' : '#ef4444'};">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span style="font-weight: 600;">Clause ${a.clause_id}</span>
        <span class="badge badge-${a.status.toLowerCase().replace(' ', '-')}">${a.status}</span>
      </div>
      <p style="font-size: 0.88rem; color: #d1d5db; margin-top: 0.4rem;">${a.findings}</p>
    </div>
  `).join("");

  // 4. Identified Risk Items
  const riskList = document.getElementById("risk-items-list");
  if (data.risk_assessment.length === 0) {
    riskList.innerHTML = `<p style="color: #34d399; font-size: 0.88rem;">No compliance risks or gaps identified.</p>`;
  } else {
    riskList.innerHTML = data.risk_assessment.map(r => `
      <div style="background: rgba(220, 38, 38, 0.08); border: 1px solid rgba(220, 38, 38, 0.2); padding: 0.9rem; border-radius: var(--radius-sm); margin-bottom: 0.8rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
          <span style="font-weight: 700; color: #fca5a5;">${r.title}</span>
          <span class="badge badge-${r.severity.toLowerCase()}">${r.severity}</span>
        </div>
        <p style="font-size: 0.85rem; color: #e5e7eb;">${r.description}</p>
        <div style="font-size: 0.78rem; color: #f87171; margin-top: 0.4rem; font-weight: 500;">
          ⚖️ Penalty Exposure: ${r.potential_penalty}
        </div>
      </div>
    `).join("");
  }

  // 5. Remediation Plan
  const remediationList = document.getElementById("remediation-list");
  remediationList.innerHTML = data.remediation_actions.map(act => `
    <div style="background: rgba(16, 185, 129, 0.06); border: 1px solid rgba(16, 185, 129, 0.2); padding: 0.9rem; border-radius: var(--radius-sm); margin-bottom: 0.8rem;">
      <div style="font-weight: 700; color: #6ee7b7; margin-bottom: 0.3rem;">${act.title}</div>
      <p style="font-size: 0.85rem; color: #d1d5db;">${act.description}</p>
      <div style="font-size: 0.78rem; color: #9ca3af; margin-top: 0.4rem;">
        👤 Responsible: <b>${act.responsible_party}</b> | Approvals: <b>${act.required_approvals.join(', ')}</b>
      </div>
    </div>
  `).join("");

  // 6. Validation Proof
  const proofBox = document.getElementById("validation-proof-box");
  const p = data.validation_proof;
  proofBox.innerHTML = `
    <div style="font-size: 0.88rem;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.4rem;">
        <span>Grounding Confidence Score:</span>
        <b style="color: #38bdf8;">${(p.grounding_confidence_score * 100).toFixed(0)}%</b>
      </div>
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.4rem;">
        <span>Hallucinations Flagged:</span>
        <b style="color: ${p.hallucination_detected ? '#ef4444' : '#34d399'};">${p.hallucination_detected ? 'YES' : 'NONE'}</b>
      </div>
      <p style="color: var(--text-muted); font-size: 0.82rem; margin-top: 0.5rem;">${p.explanation}</p>
    </div>
  `;
}

// Render Agent-to-Agent (A2A) Trace
function renderA2ATrace(trace) {
  const consoleBox = document.getElementById("a2a-console");
  if (!trace || trace.length === 0) return;

  consoleBox.innerHTML = trace.map(msg => `
    <div class="console-entry">
      <span class="timestamp">[${msg.timestamp}]</span>
      <span class="sender">${msg.sender_agent}</span>
      <span class="arrow">➔</span>
      <span class="receiver">${msg.receiver_agent}</span>: 
      <span style="color: #e5e7eb;">${msg.content}</span>
    </div>
  `).join("");
}

// Load Policy Knowledge Base
async function loadKnowledgeBase() {
  try {
    const res = await fetch(`${API_BASE}/api/policies`);
    const data = await res.json();
    kbClauses = data.clauses;
    renderKBTable(kbClauses);
  } catch (err) {
    console.error("Failed to load knowledge base:", err);
  }
}

function renderKBTable(clauses) {
  const tbody = document.getElementById("kb-table-body");
  tbody.innerHTML = clauses.map(c => `
    <tr>
      <td><b style="color: #818cf8;">${c.clause_id}</b></td>
      <td>${c.policy_name}</td>
      <td><span class="badge" style="background: rgba(99,102,241,0.15); color: #a5b4fc;">${c.policy_category}</span></td>
      <td>Sec ${c.section_number}</td>
      <td><b style="color: ${c.mandatory_level === 'MUST' ? '#ef4444' : '#f59e0b'};">${c.mandatory_level}</b></td>
      <td style="font-size: 0.82rem; color: #d1d5db;">${c.clause_text}</td>
    </tr>
  `).join("");
}

function searchKB() {
  const q = document.getElementById("kb-search-input").value.toLowerCase();
  const filtered = kbClauses.filter(c => 
    c.clause_id.toLowerCase().includes(q) ||
    c.policy_name.toLowerCase().includes(q) ||
    c.policy_category.toLowerCase().includes(q) ||
    c.clause_text.toLowerCase().includes(q)
  );
  renderKBTable(filtered);
}

// Run Benchmark Evaluation
async function runBenchmarkEvaluation() {
  const tableBody = document.getElementById("eval-table-body");
  tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted);">Running evaluation harness over 10 benchmark scenarios...</td></tr>`;

  try {
    const res = await fetch(`${API_BASE}/api/evaluate`);
    const data = await res.json();

    document.getElementById("metric-precision").textContent = `${(data.precision_at_k * 100).toFixed(1)}%`;
    document.getElementById("metric-recall").textContent = `${(data.recall_at_k * 100).toFixed(1)}%`;
    document.getElementById("metric-grounding").textContent = `${(data.evidence_grounding_score * 100).toFixed(1)}%`;
    document.getElementById("metric-status-acc").textContent = `${(data.status_classification_accuracy * 100).toFixed(1)}%`;
    document.getElementById("metric-risk-prec").textContent = `${(data.risk_classification_precision * 100).toFixed(1)}%`;
    document.getElementById("metric-latency").textContent = `${data.average_latency_ms} ms`;

    tableBody.innerHTML = data.details.map(d => `
      <tr>
        <td><b>${d.benchmark_id}</b></td>
        <td>${d.title}</td>
        <td><span class="badge" style="background: rgba(99,102,241,0.15); color: #a5b4fc;">${d.category}</span></td>
        <td><span class="badge badge-${d.expected_status.toLowerCase().replace(' ', '-')}">${d.expected_status}</span></td>
        <td><span class="badge badge-${d.predicted_status.toLowerCase().replace(' ', '-')}">${d.predicted_status}</span></td>
        <td>${(d.grounding_score * 100).toFixed(0)}%</td>
        <td>${d.latency_ms} ms</td>
      </tr>
    `).join("");

  } catch (err) {
    alert(`Failed to run evaluation: ${err.message}`);
  }
}

// Render Formatted Compliance Audit Report
function renderAuditReport(data) {
  const container = document.getElementById("audit-report-content");
  const now = new Date().toLocaleString();

  container.innerHTML = `
    <div style="font-family: 'Inter', sans-serif; color: #ffffff;">
      <div style="display: flex; justify-content: space-between; border-bottom: 2px solid var(--primary); padding-bottom: 1rem; margin-bottom: 1.5rem;">
        <div>
          <h1 style="font-size: 1.5rem; color: #ffffff;">OFFICIAL COMPLIANCE ASSESSMENT REPORT</h1>
          <p style="font-size: 0.85rem; color: var(--text-muted);">Policy Compliance Intelligence Platform | Ref ID: ${data.scenario_id}</p>
        </div>
        <div style="text-align: right; font-size: 0.8rem; color: var(--text-dim);">
          Date Generated: ${now}<br>
          Assessor: Multi-Agent Intelligence Engine
        </div>
      </div>

      <div style="margin-bottom: 1.5rem;">
        <h3 style="color: #818cf8; font-size: 1rem; margin-bottom: 0.4rem;">1. SUBMITTED BUSINESS SCENARIO</h3>
        <p style="background: rgba(255,255,255,0.04); padding: 1rem; border-radius: 6px; font-size: 0.9rem;">${data.scenario_text}</p>
      </div>

      <div style="margin-bottom: 1.5rem;">
        <h3 style="color: #818cf8; font-size: 1rem; margin-bottom: 0.4rem;">2. EXECUTIVE FINDINGS & RISK LEVEL</h3>
        <div style="display: flex; gap: 1rem; margin-bottom: 0.5rem;">
          <span class="badge badge-${data.overall_compliance_status.toLowerCase().replace(' ', '-')}">${data.overall_compliance_status}</span>
          <span class="badge badge-${data.overall_risk_level.toLowerCase()}">${data.overall_risk_level} RISK LEVEL</span>
        </div>
        <p style="font-size: 0.9rem; color: #d1d5db;">${data.executive_summary}</p>
      </div>

      <div style="margin-bottom: 1.5rem;">
        <h3 style="color: #818cf8; font-size: 1rem; margin-bottom: 0.4rem;">3. EVIDENCE TRACEABILITY MATRIX</h3>
        <table class="table">
          <thead>
            <tr>
              <th>Clause ID</th>
              <th>Policy Name & Section</th>
              <th>Status</th>
              <th>Policy Finding</th>
            </tr>
          </thead>
          <tbody>
            ${data.evidence_matrix.map(e => `
              <tr>
                <td><b>${e.clause_id}</b></td>
                <td>${e.policy_name} (Sec ${e.section})</td>
                <td><span class="badge badge-${e.compliance_status.toLowerCase().replace(' ', '-')}">${e.compliance_status}</span></td>
                <td style="font-size: 0.82rem;">${e.finding}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>

      <div style="margin-bottom: 1.5rem;">
        <h3 style="color: #818cf8; font-size: 1rem; margin-bottom: 0.4rem;">4. MANDATORY REMEDIATION ACTION PLAN</h3>
        ${data.remediation_actions.map(act => `
          <div style="margin-bottom: 0.6rem; padding: 0.8rem; background: rgba(16,185,129,0.06); border: 1px solid rgba(16,185,129,0.2); border-radius: 6px;">
            <b>${act.title}</b> [Priority: ${act.priority}]<br>
            <span style="font-size: 0.85rem; color: #d1d5db;">${act.description}</span><br>
            <span style="font-size: 0.78rem; color: #9ca3af;">Approvals Required: ${act.required_approvals.join(', ')}</span>
          </div>
        `).join("")}
      </div>
    </div>
  `;
}
