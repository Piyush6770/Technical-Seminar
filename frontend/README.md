# Journal Screener — Frontend

Web application for the **Cost-Aware Progressive Predatory Journal Detection** framework. Built with React 19 and Vite.

---

## Overview

The interface provides an interactive, real-time audit console for evaluating academic journals across a 4-stage progressive feature hierarchy. It communicates with the FastAPI backend on port 8000 and includes offline simulation fallbacks for standalone demonstration.

### Key Capabilities

1. **Journal Audit**
   - Single-journal screening by URL, title, ISSN, and publisher.
   - Adaptive Early Exit controller (skips downstream crawling once confidence exceeds threshold).
   - Real-time verdict banner (`Verified Legitimate`, `High Predatory Risk`, or `Manual Review Required`).
   - Calibrated risk score (Platt scaling), wall-clock latency, and time saved vs. monolithic scraping.
   - 4-stage acquisition trace showing feature group evaluations and skipped stages.
   - Corroborated signals and contradicted claim checks (Crossref, DOAJ, ISSN records).
   - Exportable JSON diagnostic audit record.

2. **Benchmark Results (E1–E6)**
   - Empirical evaluation on the untouched contemporary cohort ($N=1,800$, established 2021–2026).
   - Latency vs. accuracy Pareto frontier (E1 single-stage vs. E2 full crawl vs. E3 adaptive exit).
   - Model comparisons showing how shared neural representations prevent collapse under temporal drift (Macro-$F_1 = 0.4560$ vs. XGBoost $F_1 = 0.0904$).
   - Longitudinal degradation metrics ($F_1 = 0.9949 \to 0.5327$, Temporal Generalization Ratio $= 0.5354$).
   - Early exit distribution: 36.3% resolved at Stage 1 (<10 ms), 63.7% at Stage 2 (~810 ms).

3. **System Architecture**
   - 4-stage acquisition breakdown: Group A (URL Structure, 16 features), Group B (Web Policies, 13 features), Group C (Page Scripts, 6 features), Group D (Registry Check, 7 features).
   - Recurrent latent state equations: $\mathbf{h}_k = \text{GELU}(\text{LN}(\mathbf{W}_k [\mathbf{h}_{k-1}; \mathbf{x}_k] + \mathbf{b}_k))$.
   - Cost-aware stopping controller decision rule: halts when posterior confidence exceeds downstream acquisition cost.

---

## Tech Stack

- **Framework**: React 19 (`react`, `react-dom`)
- **Bundler & Dev Server**: Vite 8
- **Icons**: Lucide React
- **Styling**: Vanilla CSS design tokens (`index.css`)
- **Backend API**: FastAPI (`src/api_server.py`) on `http://127.0.0.1:8000`

---

## Quick Start

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Run Development Server
```bash
npm run dev
```
The app runs at `http://localhost:5173/`. Requests to `/api/*` are automatically proxied to the backend at `http://127.0.0.1:8000`.

### 3. Build for Production
```bash
npm run build
```
Builds the optimized production assets into `frontend/dist/`. The FastAPI backend automatically mounts and serves these static assets directly at `http://127.0.0.1:8000`.

---

## 1-Click Launcher

To start both the FastAPI backend and frontend together on Windows, run from the repository root:
```bat
start_app.bat
```

---

## Proxy Configuration

The Vite development server is configured in `vite.config.js` to proxy API requests:
```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
});
```
If the backend server is temporarily unavailable, the frontend gracefully falls back to client-side heuristics so the user interface remains interactive.
