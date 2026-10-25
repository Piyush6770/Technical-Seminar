import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  ShieldAlert, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  ExternalLink, 
  Database, 
  Activity, 
  Layers, 
  Sliders, 
  FileText, 
  Search, 
  RefreshCw,
  Cpu,
  Clock,
  Copy,
  ChevronRight,
  BookOpen
} from 'lucide-react';

const API_BASE = '/api';

export default function App() {
  const queryParams = new URLSearchParams(window.location.search);
  const [activeTab, setActiveTab] = useState(() => queryParams.get('tab') || 'audit'); // audit | batch | benchmarks | cohorts | architecture
  const [systemStatus, setSystemStatus] = useState(null);
  const [presets, setPresets] = useState([]);

  // Audit state
  const [url, setUrl] = useState('http://bmcanesthesiol.biomedcentral.com');
  const [title, setTitle] = useState('BMC Anesthesiology');
  const [issn, setIssn] = useState('1471-2253');
  const [publisher, setPublisher] = useState('BioMed Central');
  const [adaptive, setAdaptive] = useState(true);
  const [liveNetwork, setLiveNetwork] = useState(false);
  const [auditLoading, setAuditLoading] = useState(false);
  const [auditResult, setAuditResult] = useState(null);
  const [auditError, setAuditError] = useState(null);

  // Batch state
  const [batchLoading, setBatchLoading] = useState(false);
  const [batchResult, setBatchResult] = useState(null);
  const [batchFilter, setBatchFilter] = useState('ALL');
  const [batchSearch, setBatchSearch] = useState('');

  // Benchmarks state
  const [benchmarkData, setBenchmarkData] = useState(null);
  const [benchLoading, setBenchLoading] = useState(false);

  // Cohorts state
  const [activeCohort, setActiveCohort] = useState('temporal_test');
  const [cohortPage, setCohortPage] = useState(1);
  const [cohortSearch, setCohortSearch] = useState('');
  const [cohortData, setCohortData] = useState(null);
  const [cohortLoading, setCohortLoading] = useState(false);

  // Load status and presets on mount
  useEffect(() => {
    fetch(`${API_BASE}/status`)
      .then(res => res.json())
      .then(data => setSystemStatus(data))
      .catch(err => console.error('API Status error:', err));

    fetch(`${API_BASE}/presets`)
      .then(res => res.json())
      .then(data => setPresets(data))
      .catch(err => console.error('Presets error:', err));

    if (queryParams.get('autoAudit') === 'true') {
      handleRunAudit();
    }
    if (queryParams.get('autoBatch') === 'true') {
      handleRunBatchSample();
    }
  }, []);

  // Fetch benchmark data when needed
  useEffect(() => {
    if (activeTab === 'benchmarks' && !benchmarkData) {
      setBenchLoading(true);
      fetch(`${API_BASE}/benchmarks`)
        .then(res => res.json())
        .then(data => {
          setBenchmarkData(data);
          setBenchLoading(false);
        })
        .catch(err => {
          console.error(err);
          setBenchLoading(false);
        });
    }
  }, [activeTab, benchmarkData]);

  // Fetch cohort partitions
  useEffect(() => {
    if (activeTab === 'cohorts') {
      setCohortLoading(true);
      const params = new URLSearchParams({
        name: activeCohort,
        page: cohortPage,
        page_size: 15,
        search: cohortSearch
      });
      fetch(`${API_BASE}/cohorts?${params.toString()}`)
        .then(res => res.json())
        .then(data => {
          setCohortData(data);
          setCohortLoading(false);
        })
        .catch(err => {
          console.error(err);
          setCohortLoading(false);
        });
    }
  }, [activeTab, activeCohort, cohortPage, cohortSearch]);

  const applyPreset = (p) => {
    setUrl(p.url);
    setTitle(p.title);
    setIssn(p.issn);
    setPublisher(p.publisher);
  };

  const handleRunAudit = async (e) => {
    if (e) e.preventDefault();
    if (!url.trim()) return;

    setAuditLoading(true);
    setAuditError(null);
    try {
      const res = await fetch(`${API_BASE}/audit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url,
          title,
          issn,
          publisher,
          adaptive,
          live_network: liveNetwork
        })
      });
      if (!res.ok) {
        const errJson = await res.json();
        throw new Error(errJson.detail || 'Audit request failed');
      }
      const data = await res.json();
      setAuditResult(data);
    } catch (err) {
      setAuditError(err.message);
    } finally {
      setAuditLoading(false);
    }
  };

  const handleRunBatchSample = async () => {
    setBatchLoading(true);
    try {
      const res = await fetch(`${API_BASE}/batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          use_sample: true,
          sample_size: 40
        })
      });
      const data = await res.json();
      setBatchResult(data);
    } catch (err) {
      alert('Batch error: ' + err.message);
    } finally {
      setBatchLoading(false);
    }
  };

  const copyReport = () => {
    if (auditResult && auditResult.diagnostic_report) {
      navigator.clipboard.writeText(JSON.stringify(auditResult.diagnostic_report, null, 2));
      alert('Diagnostic report JSON copied to clipboard.');
    }
  };

  return (
    <div className="app-layout">
      {/* Top Header */}
      <header className="site-header">
        <div className="header-inner">
          <div className="site-brand">
            <div className="brand-icon-box">
              <BookOpen size={18} />
            </div>
            <div>
              <div className="brand-text-title">Scholarly Integrity Audit System</div>
              <div className="brand-text-meta">Predatory Journal Detection & Temporal Verification</div>
            </div>
          </div>

          <nav className="site-nav">
            <button 
              className={`nav-item-btn ${activeTab === 'audit' ? 'active' : ''}`}
              onClick={() => setActiveTab('audit')}
            >
              <Activity size={15} />
              Journal Audit
            </button>
            <button 
              className={`nav-item-btn ${activeTab === 'batch' ? 'active' : ''}`}
              onClick={() => setActiveTab('batch')}
            >
              <Layers size={15} />
              Batch Screening
            </button>
            <button 
              className={`nav-item-btn ${activeTab === 'benchmarks' ? 'active' : ''}`}
              onClick={() => setActiveTab('benchmarks')}
            >
              <Sliders size={15} />
              Benchmarks (E1–E6)
            </button>
            <button 
              className={`nav-item-btn ${activeTab === 'cohorts' ? 'active' : ''}`}
              onClick={() => setActiveTab('cohorts')}
            >
              <Database size={15} />
              Dataset Cohorts
            </button>
            <button 
              className={`nav-item-btn ${activeTab === 'architecture' ? 'active' : ''}`}
              onClick={() => setActiveTab('architecture')}
            >
              <Cpu size={15} />
              Model Architecture
            </button>
          </nav>

          <div className="header-status">
            <span className="status-indicator-dot"></span>
            <span>API Online</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {/* =========================================================================
            TAB 1: JOURNAL AUDIT
            ========================================================================= */}
        {activeTab === 'audit' && (
          <div>
            <div className="page-lead">
              <div>
                <h1 className="page-title">Journal Verification & Forensic Audit</h1>
                <p className="page-subtitle">
                  Evaluates academic journals using sequential progressive feature acquisition (URL geometry, static editorial disclosures, dynamic behavior, and scholarly registries) with adaptive early stopping.
                </p>
              </div>
            </div>

            {/* Benchmark Example Presets */}
            <div className="presets-container">
              <div className="presets-label">Load Reference Case</div>
              <div className="presets-list">
                {presets.map(p => (
                  <div 
                    key={p.id}
                    className={`preset-chip ${url === p.url ? 'active' : ''}`}
                    onClick={() => applyPreset(p)}
                  >
                    <div className="preset-chip-header">
                      <span className="preset-chip-title">{p.name}</span>
                      <span className={`pill ${
                        p.badge === 'Legitimate' ? 'pill-legit' :
                        p.badge === 'Predatory' ? 'pill-pred' : 'pill-review'
                      }`}>
                        {p.badge}
                      </span>
                    </div>
                    <div className="preset-chip-desc">{p.tag}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Audit Form Panel */}
            <div className="panel">
              <div className="panel-header">
                <div>
                  <div className="panel-title">Inspection Parameters</div>
                  <div className="panel-subtitle">Provide journal domain and canonical metadata</div>
                </div>
              </div>

              <form onSubmit={handleRunAudit}>
                <div className="form-row">
                  <div className="field" style={{ gridColumn: 'span 2' }}>
                    <label className="field-label">Journal Website URL</label>
                    <input 
                      type="url"
                      className="field-input code-font"
                      placeholder="https://example-journal.org"
                      value={url}
                      onChange={e => setUrl(e.target.value)}
                      required
                    />
                  </div>
                  <div className="field">
                    <label className="field-label">Canonical Journal Title</label>
                    <input 
                      type="text"
                      className="field-input"
                      placeholder="e.g. BMC Anesthesiology"
                      value={title}
                      onChange={e => setTitle(e.target.value)}
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="field">
                    <label className="field-label">ISSN / e-ISSN</label>
                    <input 
                      type="text"
                      className="field-input code-font"
                      placeholder="1471-2253"
                      value={issn}
                      onChange={e => setIssn(e.target.value)}
                    />
                  </div>
                  <div className="field">
                    <label className="field-label">Publisher</label>
                    <input 
                      type="text"
                      className="field-input"
                      placeholder="e.g. BioMed Central"
                      value={publisher}
                      onChange={e => setPublisher(e.target.value)}
                    />
                  </div>
                  <div className="field">
                    <label className="field-label">Acquisition Policy</label>
                    <select 
                      className="field-select"
                      value={adaptive ? 'adaptive' : 'force4'}
                      onChange={e => setAdaptive(e.target.value === 'adaptive')}
                    >
                      <option value="adaptive">Adaptive Stopping (Cost-Optimal)</option>
                      <option value="force4">Force All 4 Stages (Exhaustive)</option>
                    </select>
                  </div>
                  <div className="field" style={{ justifyContent: 'flex-end', paddingBottom: '0.5rem' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', fontSize: '0.8rem', color: 'var(--text-muted)', cursor: 'pointer' }}>
                      <input 
                        type="checkbox"
                        checked={liveNetwork}
                        onChange={e => setLiveNetwork(e.target.checked)}
                      />
                      Enable live HTTP network calls
                    </label>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
                  <button 
                    type="submit" 
                    className="btn btn-dark"
                    disabled={auditLoading || !url}
                  >
                    {auditLoading ? (
                      <>
                        <RefreshCw size={14} className="rotate-spin" />
                        Auditing Serial...
                      </>
                    ) : (
                      <>
                        <ShieldCheck size={14} />
                        Verify Journal
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>

            {/* Error Message */}
            {auditError && (
              <div className="verdict-card danger">
                <div className="verdict-icon-wrap">
                  <AlertTriangle size={20} />
                </div>
                <div>
                  <div className="verdict-heading">Execution Error</div>
                  <div className="verdict-body">{auditError}</div>
                </div>
              </div>
            )}

            {/* Audit Results */}
            {auditResult && (
              <div>
                {/* Verdict Alert */}
                <div className={`verdict-card ${auditResult.verdict_level}`}>
                  <div className="verdict-icon-wrap">
                    {auditResult.verdict_level === 'safe' && <CheckCircle2 size={22} />}
                    {auditResult.verdict_level === 'danger' && <XCircle size={22} />}
                    {auditResult.verdict_level === 'warning' && <AlertTriangle size={22} />}
                  </div>
                  <div>
                    <div className="verdict-heading">{auditResult.verdict_title}</div>
                    <div className="verdict-body">{auditResult.verdict_desc}</div>
                    <div className="verdict-footnote">
                      Decision Trace: {auditResult.halt_reason}
                    </div>
                  </div>
                </div>

                {/* Statistics Row */}
                <div className="stats-grid">
                  <div className="stat-box">
                    <div className="stat-label">Classification Verdict</div>
                    <div className="stat-number">
                      {auditResult.verdict}
                    </div>
                    <div className="stat-desc">Decision triage threshold</div>
                  </div>

                  <div className="stat-box">
                    <div className="stat-label">Predatory Risk Probability</div>
                    <div className="stat-number">
                      {(auditResult.predatory_risk * 100).toFixed(1)}%
                    </div>
                    <div className="stat-desc">Platt-calibrated posterior</div>
                  </div>

                  <div className="stat-box">
                    <div className="stat-label">Halting Stage</div>
                    <div className="stat-number">
                      Stage {auditResult.stopped_stage} of 4
                    </div>
                    <div className="stat-desc">Adaptive early exit</div>
                  </div>

                  <div className="stat-box">
                    <div className="stat-label">Acquisition Latency</div>
                    <div className="stat-number">
                      {auditResult.total_latency_sec < 1 ? 
                        `${(auditResult.total_latency_sec * 1000).toFixed(1)} ms` : 
                        `${auditResult.total_latency_sec.toFixed(2)} s`
                      }
                    </div>
                    <div className="stat-desc">Wall-clock compute cost</div>
                  </div>
                </div>

                {/* Progressive Stage Breakdown */}
                <div className="panel">
                  <div className="panel-header">
                    <div>
                      <div className="panel-title">Four-Stage Feature Timeline</div>
                      <div className="panel-subtitle">Sequential representation and decision progression</div>
                    </div>
                    <div className="code-font" style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                      Total Latency: {auditResult.total_latency_sec.toFixed(3)}s
                    </div>
                  </div>

                  <div className="stage-list">
                    {auditResult.stages.map((stg) => {
                      const isHalted = stg.stage === auditResult.stopped_stage;
                      const isDeferred = stg.status.includes('Deferred');
                      return (
                        <div 
                          key={stg.stage} 
                          className={`stage-card ${isHalted ? 'halted' : ''} ${isDeferred ? 'deferred' : ''}`}
                        >
                          <div className="stage-title-wrap">
                            <span className="stage-badge-num">{stg.stage}</span>
                            <div>
                              <strong style={{ display: 'block', color: 'var(--text-main)' }}>{stg.name}</strong>
                              <span className="pill pill-neutral" style={{ marginTop: '2px' }}>
                                {stg.status}
                              </span>
                            </div>
                          </div>

                          <div className="stage-metrics-row">
                            <div>
                              <span style={{ color: 'var(--text-dim)', marginRight: '4px' }}>Risk:</span>
                              <strong>{stg.p !== null ? `${(stg.p * 100).toFixed(1)}%` : '—'}</strong>
                            </div>
                            <div>
                              <span style={{ color: 'var(--text-dim)', marginRight: '4px' }}>Confidence:</span>
                              <strong>{stg.conf !== null ? `${(stg.conf * 100).toFixed(1)}%` : '—'}</strong>
                            </div>
                            <div>
                              <span style={{ color: 'var(--text-dim)', marginRight: '4px' }}>Cost:</span>
                              <span>{stg.latency !== null ? `${stg.latency.toFixed(2)}s` : '0.00s'}</span>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Evidence Grounding */}
                <div className="panel">
                  <div className="panel-header">
                    <div>
                      <div className="panel-title">Deterministic Evidence Grounding</div>
                      <div className="panel-subtitle">Fact corroboration against official scholarly registries</div>
                    </div>
                  </div>

                  <div className="evidence-grid">
                    <div className="evidence-pane">
                      <div className="evidence-pane-title" style={{ color: 'var(--status-safe-text)' }}>
                        <CheckCircle2 size={16} />
                        Corroborated Scholarly Findings ({auditResult.corroborated_facts?.length || 0})
                      </div>
                      {auditResult.corroborated_facts && auditResult.corroborated_facts.length > 0 ? (
                        auditResult.corroborated_facts.map((fact, idx) => (
                          <div key={idx} className="evidence-line">
                            <CheckCircle2 size={14} style={{ color: 'var(--status-safe-text)', flexShrink: 0, marginTop: '2px' }} />
                            <span>{fact}</span>
                          </div>
                        ))
                      ) : (
                        <div style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>
                          No corroborating registry confirmations identified at current acquisition depth.
                        </div>
                      )}
                    </div>

                    <div className="evidence-pane">
                      <div className="evidence-pane-title" style={{ color: 'var(--status-danger-text)' }}>
                        <AlertTriangle size={16} />
                        Contradictions & Red Flags ({auditResult.contradicted_claims?.length || 0})
                      </div>
                      {auditResult.contradicted_claims && auditResult.contradicted_claims.length > 0 ? (
                        auditResult.contradicted_claims.map((claim, idx) => (
                          <div key={idx} className="evidence-line">
                            <XCircle size={14} style={{ color: 'var(--status-danger-text)', flexShrink: 0, marginTop: '2px' }} />
                            <span>{claim}</span>
                          </div>
                        ))
                      ) : (
                        <div style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>
                          No deceptive heuristics or registry contradictions detected.
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Technical Report JSON */}
                <div className="panel">
                  <div className="panel-header">
                    <div>
                      <div className="panel-title">Diagnostic Record Artifact</div>
                      <div className="panel-subtitle">Audited JSON output conformant with research specification</div>
                    </div>
                    <button className="btn btn-outline" onClick={copyReport} style={{ fontSize: '0.78rem' }}>
                      <Copy size={13} />
                      Copy JSON
                    </button>
                  </div>
                  <pre className="json-box code-font">
                    {JSON.stringify(auditResult.diagnostic_report, null, 2)}
                  </pre>
                </div>
              </div>
            )}
          </div>
        )}

        {/* =========================================================================
            TAB 2: BATCH SCREENING
            ========================================================================= */}
        {activeTab === 'batch' && (
          <div>
            <div className="page-lead">
              <div>
                <h1 className="page-title">Batch Serial Cohort Screening</h1>
                <p className="page-subtitle">
                  High-throughput progressive screening over candidate journal cohorts with adaptive early stopping.
                </p>
              </div>
              <button 
                className="btn btn-dark"
                onClick={handleRunBatchSample}
                disabled={batchLoading}
              >
                {batchLoading ? (
                  <>
                    <RefreshCw size={14} className="rotate-spin" />
                    Auditing 40 Serials...
                  </>
                ) : (
                  <>
                    <Database size={14} />
                    Audit Temporal Cohort Sample (40 Serials)
                  </>
                )}
              </button>
            </div>

            {batchResult && (
              <div>
                <div className="stats-grid">
                  <div className="stat-box">
                    <div className="stat-label">Audited Cohort</div>
                    <div className="stat-number">{batchResult.total_records} Serials</div>
                    <div className="stat-desc">Total wall-clock: {batchResult.total_time_sec}s</div>
                  </div>

                  <div className="stat-box">
                    <div className="stat-label">Mean Latency</div>
                    <div className="stat-number">{batchResult.mean_latency_ms} ms</div>
                    <div className="stat-desc">Per journal inspection</div>
                  </div>

                  <div className="stat-box">
                    <div className="stat-label">Legitimate Venues</div>
                    <div className="stat-number" style={{ color: 'var(--status-safe-text)' }}>
                      {batchResult.counts.legitimate}
                    </div>
                    <div className="stat-desc">Verified academic serials</div>
                  </div>

                  <div className="stat-box">
                    <div className="stat-label">Predatory Flags</div>
                    <div className="stat-number" style={{ color: 'var(--status-danger-text)' }}>
                      {batchResult.counts.predatory}
                    </div>
                    <div className="stat-desc">{batchResult.counts.inconclusive} abstained for human review</div>
                  </div>
                </div>

                <div className="panel">
                  <div className="panel-header">
                    <div>
                      <div className="panel-title">Adaptive Early-Stopping Resolution</div>
                      <div className="panel-subtitle">Percentage of candidates terminated early at each stage</div>
                    </div>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
                    {[1, 2, 3, 4].map((stg) => {
                      const count = batchResult.stage_distribution[stg] || 0;
                      const pct = ((count / batchResult.total_records) * 100).toFixed(1);
                      return (
                        <div key={stg} style={{ background: 'var(--bg-subtle)', padding: '0.85rem 1rem', borderRadius: 'var(--radius-md)' }}>
                          <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', fontWeight: 600 }}>STAGE {stg} EXIT</div>
                          <div className="code-font" style={{ fontSize: '1.25rem', fontWeight: 700, margin: '0.2rem 0' }}>{pct}%</div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>{count} journals</div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Filter and Search */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.85rem' }}>
                  <div style={{ display: 'flex', gap: '0.4rem' }}>
                    {['ALL', 'Legitimate', 'Predatory', 'Inconclusive'].map((f) => (
                      <button
                        key={f}
                        className={`btn btn-outline ${batchFilter === f ? 'active' : ''}`}
                        onClick={() => setBatchFilter(f)}
                        style={{
                          fontSize: '0.78rem',
                          padding: '0.3rem 0.75rem',
                          background: batchFilter === f ? 'var(--primary)' : 'var(--bg-surface)',
                          color: batchFilter === f ? '#fff' : 'var(--text-muted)',
                          borderColor: batchFilter === f ? 'var(--primary)' : 'var(--border-light)'
                        }}
                      >
                        {f}
                      </button>
                    ))}
                  </div>

                  <div style={{ position: 'relative', width: '260px' }}>
                    <Search size={14} style={{ position: 'absolute', left: '10px', top: '10px', color: 'var(--text-dim)' }} />
                    <input 
                      type="text" 
                      className="field-input"
                      placeholder="Search title or domain..." 
                      style={{ paddingLeft: '30px', fontSize: '0.8rem', width: '100%' }}
                      value={batchSearch}
                      onChange={e => setBatchSearch(e.target.value)}
                    />
                  </div>
                </div>

                {/* Table */}
                <div className="table-wrap">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Journal Title</th>
                        <th>Website URL</th>
                        <th>Verdict</th>
                        <th>Risk Score</th>
                        <th>Halt Stage</th>
                        <th>Open Access</th>
                      </tr>
                    </thead>
                    <tbody>
                      {batchResult.results
                        .filter(r => batchFilter === 'ALL' || r.verdict === batchFilter)
                        .filter(r => !batchSearch || r.journal_name.toLowerCase().includes(batchSearch.toLowerCase()) || r.url.toLowerCase().includes(batchSearch.toLowerCase()))
                        .map((row, i) => (
                          <tr key={i}>
                            <td style={{ fontWeight: 600 }}>{row.journal_name}</td>
                            <td className="code-font" style={{ fontSize: '0.78rem' }}>
                              <a href={row.url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary-accent)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                {row.url.replace(/^https?:\/\//, '').slice(0, 32)}...
                                <ExternalLink size={12} />
                              </a>
                            </td>
                            <td>
                              <span className={`pill ${
                                row.verdict === 'Legitimate' ? 'pill-legit' : 
                                row.verdict === 'Predatory' ? 'pill-pred' : 'pill-review'
                              }`}>
                                {row.verdict}
                              </span>
                            </td>
                            <td className="code-font" style={{ fontWeight: 600 }}>
                              {(row.predatory_risk * 100).toFixed(1)}%
                            </td>
                            <td className="code-font">Stage {row.halt_stage}</td>
                            <td style={{ color: 'var(--text-dim)' }}>{row.open_access || 'yes'}</td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* =========================================================================
            TAB 3: BENCHMARKS (E1–E6)
            ========================================================================= */}
        {activeTab === 'benchmarks' && (
          <div>
            <div className="page-lead">
              <div>
                <h1 className="page-title">Empirical Benchmark Evaluations (Experiments E1–E6)</h1>
                <p className="page-subtitle">
                  Longitudinal evaluation on held-out temporal cohorts ($N=1,800$ academic serials established between 2021 and 2026).
                </p>
              </div>
            </div>

            {benchLoading && <div>Loading benchmark telemetry...</div>}

            {benchmarkData && (
              <div>
                {/* Cost-Accuracy Pareto Frontier */}
                <div className="panel">
                  <div className="panel-header">
                    <div>
                      <div className="panel-title">Cost-Accuracy Pareto Frontier (E1 vs. E2 vs. E3)</div>
                      <div className="panel-subtitle">Trade-off between wall-clock acquisition latency and generalization accuracy</div>
                    </div>
                  </div>

                  <div className="table-wrap">
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Experiment Configuration</th>
                          <th>Macro-F1</th>
                          <th>ROC-AUC</th>
                          <th>Mean Latency</th>
                          <th>Latency Reduction</th>
                          <th>Stages Acquired</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td style={{ fontWeight: 600 }}>E1: Group A Only (URL Lexical Geometry)</td>
                          <td className="code-font">0.4842</td>
                          <td className="code-font">0.5721</td>
                          <td className="code-font">10.0 ms</td>
                          <td>Baseline</td>
                          <td className="code-font">1.00 of 4</td>
                        </tr>
                        <tr>
                          <td style={{ fontWeight: 600 }}>E2: Full Acquisition (A + B + C + D Exhaustive)</td>
                          <td className="code-font">0.4560</td>
                          <td className="code-font">0.6326</td>
                          <td className="code-font">9,310.0 ms</td>
                          <td style={{ color: 'var(--status-danger-text)' }}>0.0% (Worst Latency)</td>
                          <td className="code-font">4.00 of 4</td>
                        </tr>
                        <tr style={{ background: '#f8fafc' }}>
                          <td style={{ fontWeight: 700, color: 'var(--primary)' }}>
                            E3: Adaptive Progressive Stopping (Proposed)
                          </td>
                          <td className="code-font" style={{ fontWeight: 700, color: 'var(--status-safe-text)' }}>0.5327</td>
                          <td className="code-font" style={{ fontWeight: 700, color: 'var(--status-safe-text)' }}>0.6771</td>
                          <td className="code-font" style={{ fontWeight: 700 }}>519.0 ms</td>
                          <td className="code-font" style={{ fontWeight: 700, color: 'var(--status-safe-text)' }}>-94.4% Latency</td>
                          <td className="code-font">1.64 of 4</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Model Architecture Comparison */}
                <div className="panel">
                  <div className="panel-header">
                    <div>
                      <div className="panel-title">Model Comparison: Shared Multi-Head vs Independent Baselines (E5)</div>
                      <div className="panel-subtitle">Demonstrates why Deep Learning representations prevent single-class collapse under temporal shift</div>
                    </div>
                  </div>

                  <div className="table-wrap">
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Architecture Type</th>
                          <th>Macro-F1 (Stage 4)</th>
                          <th>ROC-AUC</th>
                          <th>Expected Calibration Error (ECE)</th>
                          <th>Status Under Temporal Shift</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr style={{ background: '#f8fafc' }}>
                          <td style={{ fontWeight: 700 }}>Progressive Shared Multi-Head Neural Net (Proposed)</td>
                          <td className="code-font" style={{ fontWeight: 700, color: 'var(--status-safe-text)' }}>0.4560</td>
                          <td className="code-font">0.6326</td>
                          <td className="code-font">0.4619</td>
                          <td>
                            <span className="pill pill-legit">Balanced Predictions</span>
                          </td>
                        </tr>
                        <tr>
                          <td style={{ fontWeight: 500 }}>Independent XGBoost Baselines</td>
                          <td className="code-font" style={{ color: 'var(--status-danger-text)' }}>0.0904</td>
                          <td className="code-font">0.5860</td>
                          <td className="code-font">0.8906</td>
                          <td>
                            <span className="pill pill-pred">Collapsed to Single Class</span>
                          </td>
                        </tr>
                        <tr>
                          <td style={{ fontWeight: 500 }}>Independent Random Forest Baselines</td>
                          <td className="code-font" style={{ color: 'var(--status-danger-text)' }}>0.1388</td>
                          <td className="code-font">0.5997</td>
                          <td className="code-font">0.1837</td>
                          <td>
                            <span className="pill pill-pred">Collapsed to Single Class</span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Temporal Shift Degradation */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
                  <div className="panel">
                    <div className="panel-title" style={{ marginBottom: '0.85rem' }}>
                      Longitudinal Temporal Distribution Shift (E6)
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid var(--border-light)' }}>
                        <span style={{ color: 'var(--text-muted)' }}>Historical Validation Macro-F1 (Pre-2021)</span>
                        <span className="code-font" style={{ fontWeight: 600 }}>0.9949</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid var(--border-light)' }}>
                        <span style={{ color: 'var(--text-muted)' }}>Temporal Test Macro-F1 (2021–2026)</span>
                        <span className="code-font" style={{ fontWeight: 600, color: 'var(--status-danger-text)' }}>0.5327</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid var(--border-light)' }}>
                        <span style={{ color: 'var(--text-muted)' }}>Temporal Generalization Ratio</span>
                        <span className="code-font" style={{ fontWeight: 600 }}>0.5354 (46.5% degradation)</span>
                      </div>
                    </div>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginTop: '0.85rem', lineHeight: 1.5 }}>
                      Proves that static cross-validation on historical snapshots significantly overestimates deployment accuracy due to adversarial changes in publisher web templates.
                    </p>
                  </div>

                  <div className="panel">
                    <div className="panel-title" style={{ marginBottom: '0.85rem' }}>
                      Adaptive Early-Stopping Breakdown (E3)
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '0.25rem' }}>
                          <span>Stage 1 (URL Lexical Geometry, &lt;10 ms)</span>
                          <span className="code-font" style={{ fontWeight: 600 }}>36.3%</span>
                        </div>
                        <div style={{ height: '7px', background: 'var(--bg-subtle)', borderRadius: '4px', overflow: 'hidden' }}>
                          <div style={{ width: '36.3%', height: '100%', background: 'var(--primary)' }}></div>
                        </div>
                      </div>

                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '0.25rem' }}>
                          <span>Stage 2 (Static HTML Disclosures, ~0.8s)</span>
                          <span className="code-font" style={{ fontWeight: 600 }}>63.7%</span>
                        </div>
                        <div style={{ height: '7px', background: 'var(--bg-subtle)', borderRadius: '4px', overflow: 'hidden' }}>
                          <div style={{ width: '63.7%', height: '100%', background: 'var(--status-safe-text)' }}></div>
                        </div>
                      </div>

                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '0.25rem' }}>
                          <span>Stage 3 & 4 (Escalated on High Uncertainty)</span>
                          <span className="code-font" style={{ fontWeight: 600 }}>0.0%</span>
                        </div>
                        <div style={{ height: '7px', background: 'var(--bg-subtle)', borderRadius: '4px', overflow: 'hidden' }}>
                          <div style={{ width: '0%', height: '100%', background: 'var(--text-dim)' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* =========================================================================
            TAB 4: DATASET COHORTS
            ========================================================================= */}
        {activeTab === 'cohorts' && (
          <div>
            <div className="page-lead">
              <div>
                <h1 className="page-title">Audited Academic Serial Cohorts</h1>
                <p className="page-subtitle">
                  Partition manifest across 5,528 academic serials verified under SHA-256 frozen digest.
                </p>
              </div>
              <div className="code-font" style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                SHA-256: d775c92cbda3...f328
              </div>
            </div>

            {/* Cohort Selector Chips */}
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem' }}>
              {[
                { id: 'temporal_test', label: 'Temporal Test Cohort (N=1,800)' },
                { id: 'historical_train', label: 'Historical Training Cohort (N=1,636)' },
                { id: 'historical_val', label: 'Historical Validation Cohort (N=410)' },
                { id: 'quarantined', label: 'Quarantined Uncertain Pool (N=1,682)' }
              ].map(c => (
                <button
                  key={c.id}
                  className={`btn btn-outline ${activeCohort === c.id ? 'active' : ''}`}
                  onClick={() => {
                    setActiveCohort(c.id);
                    setCohortPage(1);
                  }}
                  style={{
                    background: activeCohort === c.id ? 'var(--primary)' : 'var(--bg-surface)',
                    color: activeCohort === c.id ? '#ffffff' : 'var(--text-muted)',
                    borderColor: activeCohort === c.id ? 'var(--primary)' : 'var(--border-light)'
                  }}
                >
                  {c.label}
                </button>
              ))}
            </div>

            {cohortData && (
              <div>
                <div className="stats-grid">
                  <div className="stat-box">
                    <div className="stat-label">Total Records</div>
                    <div className="stat-number">{cohortData.total_records}</div>
                    <div className="stat-desc">Serials in partition</div>
                  </div>

                  <div className="stat-box">
                    <div className="stat-label">Legitimate Serials</div>
                    <div className="stat-number" style={{ color: 'var(--status-safe-text)' }}>
                      {cohortData.legit_count !== null ? cohortData.legit_count : 'Unlabeled Edge'}
                    </div>
                    <div className="stat-desc">Ground-truth label = 0</div>
                  </div>

                  <div className="stat-box">
                    <div className="stat-label">Predatory Serials</div>
                    <div className="stat-number" style={{ color: 'var(--status-danger-text)' }}>
                      {cohortData.pred_count !== null ? cohortData.pred_count : 'Edge Serials'}
                    </div>
                    <div className="stat-desc">Ground-truth label = 1</div>
                  </div>

                  <div className="stat-box">
                    <div className="stat-label">Pagination</div>
                    <div className="stat-number" style={{ fontSize: '1.15rem' }}>
                      Page {cohortData.page} of {cohortData.total_pages}
                    </div>
                    <div className="stat-desc">15 items per page</div>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.85rem' }}>
                  <div style={{ position: 'relative', width: '300px' }}>
                    <Search size={14} style={{ position: 'absolute', left: '10px', top: '10px', color: 'var(--text-dim)' }} />
                    <input 
                      type="text" 
                      className="field-input" 
                      placeholder="Search title, URL, or ISSN..." 
                      style={{ paddingLeft: '30px', fontSize: '0.8rem', width: '100%' }}
                      value={cohortSearch}
                      onChange={e => {
                        setCohortSearch(e.target.value);
                        setCohortPage(1);
                      }}
                    />
                  </div>

                  <div style={{ display: 'flex', gap: '0.4rem' }}>
                    <button 
                      className="btn btn-outline" 
                      disabled={cohortPage <= 1}
                      onClick={() => setCohortPage(p => Math.max(1, p - 1))}
                      style={{ fontSize: '0.78rem' }}
                    >
                      Previous
                    </button>
                    <button 
                      className="btn btn-outline" 
                      disabled={cohortPage >= cohortData.total_pages}
                      onClick={() => setCohortPage(p => p + 1)}
                      style={{ fontSize: '0.78rem' }}
                    >
                      Next
                    </button>
                  </div>
                </div>

                <div className="table-wrap">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Journal Title</th>
                        <th>Website URL</th>
                        <th>Ground Truth</th>
                        <th>Publisher / Registry</th>
                        <th>ISSN</th>
                        <th>Open Access</th>
                      </tr>
                    </thead>
                    <tbody>
                      {cohortData.records.map((r, i) => (
                        <tr key={i}>
                          <td style={{ fontWeight: 600 }}>{r.journal_name}</td>
                          <td className="code-font" style={{ fontSize: '0.78rem' }}>
                            <a href={r.url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary-accent)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px' }}>
                              {String(r.url).replace(/^https?:\/\//, '').slice(0, 32)}...
                              <ExternalLink size={12} />
                            </a>
                          </td>
                          <td>
                            {r.label === 0 ? (
                              <span className="pill pill-legit">Legitimate</span>
                            ) : r.label === 1 ? (
                              <span className="pill pill-pred">Predatory</span>
                            ) : (
                              <span className="pill pill-review">Quarantined</span>
                            )}
                          </td>
                          <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                            {r.publisher && r.publisher !== '-' ? r.publisher : (r.quartile || '-')}
                          </td>
                          <td className="code-font" style={{ fontSize: '0.78rem' }}>
                            {r.issn_l && r.issn_l !== '-' ? r.issn_l : '-'}
                          </td>
                          <td style={{ color: 'var(--text-dim)' }}>{r.open_access || 'yes'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

              </div>
            )}
          </div>
        )}

        {/* =========================================================================
            TAB 5: ARCHITECTURE
            ========================================================================= */}
        {activeTab === 'architecture' && (
          <div>
            <div className="page-lead">
              <div>
                <h1 className="page-title">Progressive Architecture & Formulation</h1>
                <p className="page-subtitle">
                  Mathematical framework of shared sequential representations and entropy-bounded adaptive stopping.
                </p>
              </div>
            </div>

            {/* Four Stage Panels */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
              <div className="panel" style={{ marginBottom: 0 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <strong style={{ fontSize: '0.9rem' }}>Stage 1: URL Geometry</strong>
                  <span className="pill pill-neutral code-font">&lt;10 ms</span>
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', marginBottom: '0.65rem' }}>Group A (16 features)</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                  Shannon entropy, TLD risk classification, symbol and numeric character densities, path depths, IPv4 pattern matching.
                </div>
              </div>

              <div className="panel" style={{ marginBottom: 0 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <strong style={{ fontSize: '0.9rem' }}>Stage 2: HTML Policies</strong>
                  <span className="pill pill-neutral code-font">~0.80 s</span>
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', marginBottom: '0.65rem' }}>Group B (13 features)</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                  APC cost disclosure, editorial board link depth, peer-review accessibility statements, COPE declarations, institutional email validation.
                </div>
              </div>

              <div className="panel" style={{ marginBottom: 0 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <strong style={{ fontSize: '0.9rem' }}>Stage 3: Dynamic JS</strong>
                  <span className="pill pill-neutral code-font">~3.50 s</span>
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', marginBottom: '0.65rem' }}>Group C (6 features)</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                  Headless DOM render delta, external third-party script ratios, ad networks, cryptocurrency miners, cloaked redirects.
                </div>
              </div>

              <div className="panel" style={{ marginBottom: 0 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <strong style={{ fontSize: '0.9rem' }}>Stage 4: Registries</strong>
                  <span className="pill pill-neutral code-font">~5.00 s</span>
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', marginBottom: '0.65rem' }}>Group D (7 features)</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                  Official ISSN Portal verification, Crossref DOI deposit active status, DOAJ indexing, Scopus/WoS claims corroboration.
                </div>
              </div>
            </div>

            {/* Neural Recurrence Formulation */}
            <div className="panel">
              <div className="panel-header">
                <div>
                  <div className="panel-title">Progressive Latent State Formulation</div>
                  <div className="panel-subtitle">Sequential recurrence sharing across intermediate heads</div>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                <div>
                  <strong style={{ fontSize: '0.84rem', display: 'block', marginBottom: '0.4rem' }}>Latent Accumulation</strong>
                  <pre className="json-box code-font" style={{ background: '#ffffff', color: '#0f172a' }}>
{`h_1 = GELU(LN(W_1 * x_A + b_1))
h_2 = GELU(LN(W_2 * [h_1; x_B] + b_2))
h_3 = GELU(LN(W_3 * [h_2; x_C] + b_3))
h_4 = GELU(LN(W_4 * [h_3; x_D] + b_4))`}
                  </pre>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginTop: '0.5rem', lineHeight: 1.5 }}>
                    Each representation h_k accumulates preceding evidence without discarding prior domain geometry.
                  </p>
                </div>

                <div>
                  <strong style={{ fontSize: '0.84rem', display: 'block', marginBottom: '0.4rem' }}>Stopping Controller Policy</strong>
                  <pre className="json-box code-font" style={{ background: '#ffffff', color: '#0f172a' }}>
{`Confidence: c_k = max(p_k, 1 - p_k)

Halt if:
  c_k >= tau_k  AND
  Delta_cost(k -> k+1) > lambda * (1 - c_k)`}
                  </pre>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginTop: '0.5rem', lineHeight: 1.5 }}>
                    Dynamically determines whether marginal gains in decision certainty justify the wall-clock latency of downstream network calls.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
