### GROUP ID: GB11

### A TECHNICAL SEMINAR REPORT ON

COST-AWARE PROGRESSIVE PREDATORY JOURNAL DETECTION

SUBMITTED TO THE PCET'S PIMPRI CHINCHWAD COLLEGE OF ENGINEERING AN AUTONOMOUS INSTITUTE, PUNE

IN THE PARTIAL FULFILLMENT OF THE REQUIREMENTS FOR

THIRD YEAR (SEMESTER V) OF

# BACHELOR OF TECHNOLOGY (COMPUTER ENGINEERING)

### SUBMITTED BY

Under the guidance of

# Prof. Dr. Swati V. Shinde

# DEPARTMENT OF COMPUTER ENGINEERING

### PCET'S PIMPRI CHINCHWAD COLLEGE OF ENGINEERING

Sector No. 26, Pradhikaran, Nigdi, Pimpri-Chinchwad, PUNE 411044 An Autonomous Institute Approved by AICTE and Affiliated to SPPU, Pune Academic Year 2026-27

### PCET'S PIMPRI CHINCHWAD COLLEGE OF ENGINEERING

Sector No. 26, Pradhikaran, Nigdi, Pimpri-Chinchwad, PUNE 411044

An Autonomous Institute Approved by AICTE and Affiliated to SPPU, Pune

# CERTIFICATE

This is to certify that the Technical Seminar report entitled

### "COST-AWARE PROGRESSIVE PREDATORY JOURNAL DETECTION"

Submitted by

are bonafide students of this institute and the work has been carried out by them under the supervision of Prof. Dr. Swati V. Shinde and it is approved for the partial fulfillment of the requirement of PCET'S PIMPRI CHINCHWAD COLLEGE OF ENGINEERING, for the award of Third Year of Bachelor of Technology (Computer Engineering) A.Y. 2026-27.

### Prof. Dr. Swati V. Shinde	  Prof. Dr. Sonali D. Patil

Guide Name	Head,

Department of Computer Engineering

Place: Pune

Date:	/	/2026

# ACKNOWLEDGEMENT

We express our sincere thanks to our Technical Seminar Guide, Prof. Dr. Swati V. Shinde, for her constant encouragement, valuable suggestions and technical guidance throughout the course of this work. Her insights on research methodology, experimental rigour and scientific writing laid the foundation for the success of this seminar.

We are grateful to Prof. Dr. Sonali D. Patil, Head of the Department of Computer Engineering, for her unwavering support, and to Hon. Director, Dr. G. N. Kulkarni, for providing an academic environment in which this work could be completed successfully. We also thank all the faculty members and technical staff of the department for their help and cooperation.

Finally, we extend our deep appreciation to our family and friends for their continued support and motivation during the crucial stages of completing this Technical Seminar.

### PIYUSH PATEL PARSHWA NIKAM SUYOG JADHAV PRATIK JADHAV

# ABSTRACT

The commercialisation of Open Access publishing and author-facing Article Processing Charges (APCs) has given rise to a large industry of predatory journals that charge authors for publication while offering little or no genuine peer review. More than 10,000 such serials are estimated to solicit manuscripts worldwide. Existing machine-learning detectors typically report very high accuracy on static, identically distributed snapshots of historical blacklists, but they fail when deployed on contemporary journals, assume that every feature is available at zero cost, and emit opaque probability scores with no verifiable evidence.

This Technical Seminar presents Cost-Aware Progressive Predatory Journal Detection, an end-to-end forensic framework that addresses these three weaknesses. Features are organised into four progressively acquired stages (URL geometry, static HTML policies, dynamic JavaScript behaviour and scholarly registry verification) totalling 42 features. A shared progressive multi-head neural network, implemented in PyTorch, accumulates representations across stages, while a calibrated adaptive stopping controller halts feature acquisition as soon as the posterior confidence exceeds a stage-specific threshold. Temperature and Platt scaling calibrate the posteriors, and a tri-state decision rule (Verified Legitimate, Selective Abstention, Predatory Warning) routes ambiguous cases to human experts. A deterministic evidence-grounding engine attaches registry-based evidence to each verdict.

The system was evaluated on an audited corpus of 5,528 academic serials frozen with SHA-256 digests, using a strictly held-out temporal test set of 1,800 journals from 2021 to 2026. The proposed adaptive configuration reduces mean inference latency by 94.4% (519 ms versus 9,310 ms for full acquisition) while improving temporal Macro-F1 from 0.4560 to 0.5327. Tree-based baselines collapse under temporal drift (XGBoost Macro-F1 = 0.0904), and the measured Temporal Generalisation Ratio is 0.5354. Selective abstention lowers the false-positive rate from 29.9% to 13.8% while resolving 87.2% of serials autonomously. A full-stack web application (React 19 + FastAPI) provides single-journal inspection, progressive acquisition traces and benchmark exploration.

Keywords: Predatory journals, temporal generalisation, progressive feature acquisition, early stopping, probability calibration, selective abstention, evidence grounding, PyTorch.

# TABLE OF CONTENTS

# LIST OF FIGURES

Figure 4.1	Progressive Four-Stage Inference Pipeline with Adaptive Early Exit	8

Figure 6.1	Dataset Composition of the Audited Corpus Partitions	14

Figure 6.2	Macro-F1 on the Temporal Test Set for Different Configurations	15

Figure 6.3	Mean Inference Latency per Journal for Different Configurations	15

LIST OF TABLES

Table 3.1	Software Technology Stack	6

Table 3.2	Recommended Hardware Requirements	6

Table 4.1	Four-Stage Feature Hierarchy (42 Features)	9

Table 4.2	Tri-State Decision Rule	10

Table 4.3	Audited Dataset Partitions	10

Table 5.1	Tools and Technologies Used	13

Table 6.1	Empirical Benchmark Results (Experiments E1 to E6)	14

Table 6.2	Key Quantitative Outcomes of the Proposed System	16

Overview

CHAPTER 1 INTRODUCTION

Scholarly publishing is the backbone of scientific communication. Over the last two decades, the shift to Open Access models, in which authors or their institutions pay Article Processing Charges (APCs), has made publishing more accessible but has also created a financial incentive for fraudulent actors. Predatory journals imitate legitimate scholarly venues, promise peer review within days, collect author fees and publish unvetted work, including clinical and engineering studies that can mislead practitioners and pollute the scientific record. More than 10,000 deceptive serials are estimated to solicit manuscripts globally.

This Technical Seminar studies the automated detection of such journals and presents a complete forensic framework named Cost-Aware Progressive Predatory Journal Detection. Rather than treating detection as a one-shot classification over a fixed feature vector, the framework couples four ideas: cost-aware progressive feature acquisition, out-of-distribution temporal evaluation, calibrated neural early stopping, and deterministic registry-based evidence grounding. The work is delivered as a reproducible codebase with audited datasets, neural checkpoints, a modern full-stack web application (FastAPI backend + React 19 frontend) and an IEEE-format research paper.

Motivation

Prior automated approaches to predatory journal detection failed in operational deployment because of three structural flaws, which together motivated this work:

### The static in-distribution fallacy. Many studies report diagnostic metrics above 95% using standard identically distributed cross-validation on historical snapshots such as pre-2020 crawls of Beall's list. Deceptive publishing, however, is adversarial and non-stationary: post-2020 operations adopt modern content-management software such as Open Journal Systems, register credible academic-sounding domains and forge editorial board affiliations. Classifiers fitted on historical heuristics collapse on contemporary journals; in our experiments the ratio of temporal to historical F1 is only 0.5354.

### The uniform acquisition cost fallacy. Traditional models assume that all features are available instantly and at no cost. In practice, evaluating URL string geometry takes under 10 ms, headless-browser JavaScript rendering takes 3 to 5 seconds, and querying external scholarly registries (Crossref, OpenAlex, DOAJ, ISSN Portal) needs several network round-trips subject to rate limits and downtime, totalling about 9,310 ms.

Invoking exhaustive scraping for millions of serials is computationally and financially infeasible.

### The ungrounded black-box prediction fallacy. Existing models emit raw, uncalibrated scalar probabilities (for example 0.82) without verifiable evidence. In tenure disputes or defamation proceedings such an opaque score has no standing. When evidence is noisy or ambiguous (0.40 ≤ p ≤ 0.60), a responsible system must abstain and route the record to human expert librarians rather than force an arbitrary verdict.

Problem Statement and Objectives

### Problem Statement

To design and evaluate a scalable, explainable and cost-efficient system that classifies academic journals as legitimate or predatory, remains reliable on contemporary journals that differ from the historical training distribution, minimises the computational cost of feature acquisition, and supports every verdict with verifiable evidence or abstains when evidence is insufficient.

### Objectives

To organise 42 journal features into four progressively acquired stages ordered by acquisition latency and adversarial evasion resistance.

To build a shared progressive multi-head neural network that learns representations across stages and outputs a posterior risk probability at every stage.

To implement a calibrated adaptive stopping controller that halts feature acquisition once the posterior confidence reaches a stage-specific threshold, reducing mean inference latency.

To apply temperature and Platt scaling and a tri-state decision rule with selective abstention so that ambiguous journals are routed to human experts.

To evaluate the framework on an audited, SHA-256-frozen corpus with a strictly held-out temporal test set, and to compare it against monolithic, fixed-stage and tree-based baselines.

To provide an interactive web application and an IEEE-format research paper that make the system and its results reproducible.

Scope

The scope of this project covers the complete pipeline from feature extraction to decision support: URL and domain geometry features, static HTML policy features, dynamic JavaScript runtime features, scholarly registry features, the progressive neural model, calibration, adaptive

stopping, evidence grounding, benchmarking experiments E1 to E6, publication-quality figure generation and an interactive dashboard with single-journal inspection and batch CSV auditing.

The project does not attempt to provide a legal definition of predatory publishing, does not replace human editorial judgement for borderline records, and does not cover non-journal venues such as conferences or books. Retraining on new data and integration with institutional library systems are left for future work.

Methodologies of Problem Solving

The project followed an experimental research methodology with the following phases:

### Problem analysis and literature review: identifying the gaps in static, uniform-cost and ungrounded detectors.

### Dataset audit: combining journal records from 2012 to 2026 into a single corpus of 5,528 serials, partitioning it by era, and freezing it with SHA-256 digests to guarantee reproducibility.

### Feature engineering: designing 42 features in four stages and implementing a persistent disk cache so that expensive features are never recomputed.

### Model development: training a shared progressive network with a composite multi-task loss, followed by calibration and threshold tuning on the validation split.

### Evaluation: running six experiment families (E1 to E6) on the untouched temporal test cohort and on a web-noise pool for robustness.

### Deployment and documentation: building the full-stack web application, an automated test suite, publication figure scripts and the research paper.

# CHAPTER 2 LITERATURE SURVEY

A review of the literature on predatory publishing, journal classification, distribution shift, cost-sensitive learning and calibration was carried out to position this work and to justify its technical choices. The sources listed in the References section are cited by number.

Predatory Publishing and Blacklist-Based Approaches

Predatory publishing came to wide attention through the blacklists curated by Jeffrey Beall and through investigative studies such as the 2013 Science sting operation, which showed that many open-access journals accepted a deliberately flawed manuscript [1]. Longitudinal studies later quantified the rapid growth in article volumes in such journals [2]. A consensus definition was only proposed in 2019, which emphasised that predatory journals prioritise self-interest at the expense of scholarship and are characterised by false or misleading information, deviation from best editorial practice and a lack of transparency [3].

Blacklists suffer from well-known practical weaknesses: curation is manual and slow, inclusion criteria can be subjective, and curators have historically faced legal threats. Whitelists such as the Directory of Open Access Journals (DOAJ) [4] provide positive evidence of quality but cannot, on their own, classify journals that are simply absent from the list, including many legitimate journals from low-resource regions.

Machine-Learning Approaches to Journal Classification

Automated approaches model journal legitimacy as a binary classification problem over features drawn from journal websites, editorial boards, publishing policies and bibliometric indicators. Tree-based ensembles such as Random Forests [5] and gradient boosting (XGBoost)

[6] are common choices for such tabular data and generally report high accuracy when evaluated with random cross-validation on a single historical crawl. These studies usually treat all features as available simultaneously and report only a point prediction.

The weakness of this setting is that random splits leak information about the publishers and templates present in the training era. A model may memorise registry correlations that were true of historical predatory journals but not of those that appeared after 2020. This is the static in-distribution fallacy identified in Chapter 1.

Temporal Drift and Out-of-Distribution Generalisation

Deployed classifiers face covariate and concept shift when the data-generating process changes with time [7]. Adversarial domains such as spam, phishing and fraudulent publishing are particularly prone to this because adversaries adapt to deployed detectors. Evaluating on a chronologically later, untouched cohort rather than on random folds is the accepted way to measure robustness to such drift. This project adopts a strict temporal protocol: models are fitted and tuned on pre-2021 journals and evaluated once on a 1,800-record 2021–2026 cohort.

Cost-Aware and Progressive Feature Acquisition

Cost-sensitive learning recognises that features differ widely in acquisition cost and that decisions can often be made from a cheap subset. Sequential and anytime prediction frameworks, and early-exit networks, stop computation once a sufficiently confident prediction is available. In the journal-auditing setting, the cost gradient is extreme: URL geometry costs milliseconds, whereas registry queries cost seconds and depend on external services. This motivates a staged feature hierarchy with a learned stopping rule, which is the core of the proposed framework.

Calibration and Selective Prediction

Modern neural networks are often over-confident, especially on out-of-distribution inputs. Temperature scaling and Platt scaling are standard post-hoc remedies that rescale logits so that predicted probabilities better match empirical frequencies [8], [9]. Calibration is essential for confidence-based early stopping, since an over-confident network would exit too early. Selective prediction, also known as classification with a reject option, allows a model to abstain when its confidence is low and to defer to a human expert, trading coverage for reliability [10].

Summary of Literature Review and Research Gap

The literature shows that (i) blacklists and whitelists are valuable but incomplete, (ii) machine-learning detectors achieve high in-distribution accuracy but are rarely evaluated under temporal drift, (iii) acquisition cost is typically ignored, and (iv) verdicts are rarely accompanied by verifiable evidence or an abstention mechanism. The present work addresses all four gaps in a single pipeline, which is summarised in Table 4.1 and Table 6.1.

# CHAPTER 3

# SOFTWARE REQUIREMENTS SPECIFICATION

System Requirements

Dataset Requirements

The system operates on an audited corpus of 5,528 academic serials covering 2012 to 2026. The master file is stored as audit/data/final_combined_journal_dataset_frozen_readonly.csv and is protected by a SHA-256 digest (d775c92c…f4c328) so that any modification is detected. The corpus is partitioned into four disjoint cohorts: HISTORICAL_TRAIN (1,636 records), HISTORICAL_VAL   (410),   TEMPORAL_TEST_UNTOUCHED   (1,800)   and

WEB_NOISE_POOL (1,272). Each record carries the journal URL, title, ISSN, publisher, era and a binary label (0 = legitimate, 1 = predatory). Extracted features are cached persistently (SQLite / JSON) to avoid repeated network calls.

Software Requirements (Platform Choice)

Table 3.1: Software Technology Stack

Hardware Requirements

The framework does not need dedicated server hardware. The following configuration is recommended for development and for running the complete benchmark suite; model inference itself is lightweight.

Table 3.2: Recommended Hardware Requirements

Functional and Non-Functional Requirements

### Functional requirements

Accept a journal URL, title, ISSN or publisher as input and extract the relevant features progressively.

Produce a calibrated risk probability at each stage and stop adaptively according to stage-specific confidence thresholds.

Return one of three outcomes: Verified Legitimate, Selective Abstention (human audit) or Predatory Warning, together with the evidence that supports the outcome.

Support batch auditing of a CSV list of ISSNs or URLs.

Verify dataset integrity against the frozen SHA-256 digests and re-run benchmark experiments E1 to E6.

Regenerate all publication figures and the IEEE research paper from stored benchmark results.

### Non-functional requirements

### Performance: mean inference latency of the adaptive pipeline should be a small fraction of full acquisition (achieved: 519 ms versus 9,310 ms).

### Reproducibility: frozen, hash-verified splits and deterministic scripts.

### Explainability: every verdict must be traceable to rule-based evidence or marked as abstained.

### Robustness: behaviour should degrade gracefully under noisy web data and unavailable registries.

### Fairness: borderline journals, including those from emerging regions, must not be blacklisted automatically.

System Architecture

CHAPTER 4 SYSTEM DESIGN

The system is a progressive inference pipeline. A query (journal URL, title, ISSN and publisher) first enters Stage 1, where inexpensive URL and domain geometry features are computed in under 10 ms. The adaptive stopping controller evaluates the calibrated confidence c₁ = max(p₁, 1 − p₁). If c₁ ≥ 0.80, the journal exits at Stage 1; otherwise Stage 2 (static HTML policy features) is executed, and the process repeats. Only the remaining uncertain journals proceed to Stage 3 (dynamic JavaScript runtime) and Stage 4 (scholarly registries). The final posterior is mapped to a tri-state decision and supported by deterministic evidence grounding.

Figure 4.1: Progressive Four-Stage Inference Pipeline with Adaptive Early Exit

With the optimised thresholds, 36.3% of serials are resolved at Stage 1 and the remaining 63.7% at Stage 2 on the temporal test cohort, so the expensive Stage 3 and Stage 4 are rarely invoked.

Four-Stage Feature Hierarchy

Features are decoupled into four modular groups that are evaluated progressively and cached on disk (src/features/cache.py). The groups are ordered by increasing acquisition latency and increasing resistance to adversarial evasion.

Table 4.1: Four-Stage Feature Hierarchy (42 Features)

Shared Progressive Neural Network

Instead of training four independent classifiers, a single progressive network (src/models/multi_head_model.py) keeps a hidden state hₖ that accumulates representations across stages:

h₁ = ReLU(W₁x₁ + b₁);  hₖ = ReLU(Wₖ[hₖ₋₁ ; xₖ] + bₖ), k ∈ {2, 3, 4}

Each stage emits a posterior risk probability pₖ = σ(Vₖhₖ). During training, a composite multi-task objective updates all heads simultaneously:

L_total = Σ (k = 1 to 4) αₖ · L_CE(pₖ, y)

Shared representation learning forces early layers to learn generalisable features and acts as a regulariser. This prevents the catastrophic tabular collapse observed for standard tree models under temporal shift (XGBoost Macro-F1 = 0.0904).

Calibrated Adaptive Stopping Controller

At stage k the stopping controller (src/models/stopping_controller.py) computes the calibrated confidence

cₖ = max(pₖ, 1 − pₖ)

and halts inference as soon as cₖ ≥ τₖ. The optimised thresholds are τ₁ = 0.80, τ₂ = 0.80 and τ₃

= 0.75. Because easy cases are resolved by cheap features, the controller achieves a 94.4% reduction in mean latency while also improving temporal generalisation, since uninformative downstream signals are pruned for decisive cases.

Probability Calibration

Uncalibrated networks emit extreme probabilities (above 0.99) on out-of-distribution inputs, which would trigger unreliable early exits. The calibration module (src/models/calibration.py) applies Platt scaling and temperature scaling fitted on HISTORICAL_VAL, and reports the Expected Calibration Error (ECE). Calibration reduces ECE from 0.4619 to 0.3079 on the temporal cohort.

Tri-State Classification and Selective Abstention

Rather than forcing a binary label, the system implements a principled reject option:

Table 4.2: Tri-State Decision Rule

Routing ambiguous cases to human review lets the system resolve 87.2% of serials autonomously while lowering the false-positive rate from 29.9% to 13.8%.

Deterministic Evidence Grounding

The explainability module (src/explainability/evidence_grounding.py) is a rule-based corroboration and contradiction engine. It cites official registry discrepancies, for example whether an ISSN is registered in the official portal, whether a claimed DOAJ indexing exists, or whether a Crossref DOI prefix is active. This replaces opaque scores with verifiable factual provenance, which is important in legal or tenure disputes. The engine also writes audit logs for each decision.

Audited Dataset Design

All experiments use the frozen corpus of 5,528 serials. The historical and temporal splits are deliberately different in class balance: the historical splits are about 60:40 legitimate to predatory, whereas the contemporary temporal test cohort is about 90:10, which mirrors the real-world imbalance and makes the evaluation harder.

Table 4.3: Audited Dataset Partitions

# CHAPTER 5 IMPLEMENTATION

Overview of Project Modules

### Audit and Dataset Module

The audit/ directory holds the frozen master dataset and the four split files. The script scripts/prepare_audit_dataset.py partitions the data and verifies each cohort against its SHA-256 digest, so that experiments can always be traced to an unmodified dataset.

### Feature Extraction Module

The src/features package implements the four feature groups (group_a_url.py, group_b_html.py, group_c_dynamic.py, group_d_scholarly.py) and a unified sequential extraction pipeline (pipeline.py). A persistent cache (cache.py, SQLite / JSON) stores computed features so that repeated runs and benchmarks never repeat slow network calls. Group A parses the URL and computes entropy, TLD and token statistics. Group B fetches static HTML and analyses APC and peer-review statements, board pages and contact addresses. Group C renders the page in a headless browser and compares the rendered DOM with the static DOM. Group D queries Crossref, OpenAlex, DOAJ and the ISSN Portal.

### Model Module

The src/models package contains the shared progressive multi-head network (multi_head_model.py), the calibrated stopping controller (stopping_controller.py), the Platt and temperature calibration code (calibration.py) and the decoupled XGBoost and Random Forest baselines (baselines.py) used for comparison.

### Explainability Module

evidence_grounding.py applies deterministic corroboration and contradiction rules over registry evidence so that every Predatory Warning or Verified Legitimate decision is accompanied by checkable evidence.

### Evaluation and Reporting Module

The benchmark runner executes experiments E1 to E6 over all 5,528 serials and stores metrics, confusion matrices, reliability diagrams and latency statistics in artifacts/reports/benchmark_results.json. Scripts in scripts/ regenerate seven publication figures at 300 DPI (PNG and vector PDF) and compile the 7-page IEEE two-column paper using ReportLab Platypus.

### User Interface Module

The full-stack web application (`frontend/` and `src/api_server.py`) implements a modern, responsive interface built with React 19, Vite, and FastAPI. It provides three core tabs: Single Journal Audit, Empirical Benchmark Matrix, and Model Architecture.

Tools and Technologies Used

Table 5.1: Tools and Technologies Used

Execution Workflow

The repository README documents the following reproducible workflow:

### Environment setup: clone the repository and install the dependencies with pip install

-r requirements.txt.

### Verify dataset integrity: python scripts/prepare_audit_dataset.py.

### Run the benchmark suite: python -m src.evaluation.run_benchmarks, which writes artifacts/reports/benchmark_results.json.

### Regenerate figures: python scripts/redesign_publication_diagrams.py.

### Compile the paper: python scripts/strip_all_dollars_and_format_math.py.

### Launch the web application: run start_app.bat or start the FastAPI backend (python -m uvicorn src.api_server:app --host 127.0.0.1 --port 8000) and open http://127.0.0.1:8000.

# CHAPTER 6 RESULTS

Result Analysis and Validations

All quantitative results are measured on the untouched temporal test cohort of 1,800 journals from 2021–2026 (1,621 legitimate and 179 predatory), unless stated otherwise. Because predatory journals form only 9.9% of this cohort, Macro-F1 and specificity are reported together with precision and recall.

Figure 6.1: Dataset Composition of the Audited Corpus Partitions

### Benchmark Results (Experiments E1 to E6)

Table 6.1: Empirical Benchmark Results (Experiments E1 to E6)

Figure 6.2: Macro-F1 on the Temporal Test Set for Different Configurations

Figure 6.3: Mean Inference Latency per Journal for Different Configurations

### Key Findings

### 94.4% latency reduction. The adaptive controller (E3) resolves journals in 519 ms on average versus 9,310 ms for monolithic acquisition (E2), a 94.4% reduction in computational overhead.

### Improved generalisation. Stopping early on decisive cases improves temporal Macro-F1 from 0.4560 (E2) to 0.5327 (E3), because uninformative downstream signals are not allowed to dilute the decision. E3 also has the best precision, specificity, predatory F1 and ROC-AUC among the neural configurations.

### Tabular collapse is demonstrated. Tree-based baselines fitted on historical registry correlations collapse under drift: XGBoost reaches Macro-F1 of 0.0904 with specificity 0.0000, i.e. it labels almost every contemporary journal predatory, while the shared neural architecture retains balanced discriminative power.

### Temporal drift is quantified. Performance falls from 0.9949 on historical in-distribution validation (E6-H) to 0.5327 on the temporal cohort, a reproducible Temporal Generalisation Ratio of 0.5354.

### Calibration and abstention help. Calibration lowers ECE from 0.4619 to 0.3079. The tri-state rule resolves 87.2% of serials autonomously and reduces the false-positive rate from 29.9% to 13.8%.

Table 6.2: Key Quantitative Outcomes of the Proposed System

### Discussion

The results show clearly that high in-distribution accuracy (0.9949) is not predictive of real-world performance, and that the temporal protocol is essential for honest evaluation. The absolute temporal Macro-F1 of 0.5327 is modest, which reflects the genuine difficulty of the task: the contemporary cohort is highly imbalanced (9.9% predatory) and predatory publishers actively mimic legitimate ones. The contribution of the proposed framework is therefore not an inflated headline accuracy but a more robust, cheaper and more accountable detector. The identical metrics of E2 and E4-2 to E4-4 indicate that, for the full-acquisition setting, later stages do not add discriminative signal beyond Stage 2 on this cohort, which further supports early stopping.

Interactive Web Application

The modern web application (`frontend/` + `src/api_server.py`) exposes the system to non-technical users, such as librarians and research administrators, through three dedicated views:

### Single Journal Audit: enter a journal URL, title, or ISSN to run real-time progressive auditing, featuring calibrated risk probability, stopping stage telemetry, and a verified evidence provenance drawer.

### Empirical Benchmark Results: explore latency frontiers, early-exit resolution distributions, and diagnostic metrics interactively.

### Model Architecture Explorer: inspect the 4-stage feature hierarchy and shared neural network formulation.

[Insert web application screenshots here: Figure 6.4 Single Journal Audit, Figure 6.5 Benchmark Results, Figure 6.6 Model Architecture. Capture them from http://localhost:5173 or http://127.0.0.1:8000 and use sharp, clear images with the figure number and title below each, as in the reference report.]

Conclusion

CHAPTER 7 CONCLUSIONS AND FUTURE SCOPE

This Technical Seminar presented Cost-Aware Progressive Predatory Journal Detection, a reproducible framework that addresses three structural weaknesses of earlier detectors: static in-distribution evaluation, uniform feature cost and ungrounded black-box predictions. By organising 42 features into four progressively acquired stages, training a shared progressive neural network, calibrating its posteriors and stopping adaptively, the system reduces mean inference latency by 94.4% (519 ms versus 9,310 ms) and improves temporal Macro-F1 from 0.4560 to 0.5327 compared with full feature acquisition.

The study also demonstrates that tree-based baselines collapse under temporal drift (XGBoost Macro-F1 = 0.0904) and quantifies drift with a Temporal Generalisation Ratio of 0.5354. Tri-state classification with selective abstention and deterministic evidence grounding makes the verdicts accountable: 87.2% of serials are resolved autonomously, the false-positive rate drops from 29.9% to 13.8%, and ambiguous journals are passed to human experts. The audited, hash-frozen dataset, scripted figures, test suite and interactive web application make the whole study reproducible.

As third-year Computer Engineering students, the work gave us practical experience in machine-learning research methodology, distribution-shift evaluation, calibration, web data acquisition, software engineering for reproducibility and scientific writing.

Limitations

Absolute performance on the contemporary cohort remains modest (Macro-F1 0.5327, predatory F1 0.2641), reflecting class imbalance and adversarial mimicry.

Stage 3 and Stage 4 features depend on external websites and APIs, which can be rate-limited, change structure or be temporarily unavailable.

The corpus has 5,528 serials; the number of contemporary predatory examples (179 in the temporal test set) is small.

The evidence-grounding engine is rule-based and only as complete as the registries it consults.

Future Scope

### Continual and drift-aware learning: periodic retraining with newly verified journals and online drift monitoring.

### Richer content features: language-model-based analysis of journal scope statements, editorial board consistency and review-time claims.

### Larger and more diverse datasets: more contemporary predatory examples and coverage of journals from the Global South, to improve fairness and reliability.

### Active learning with human audit: using librarian decisions on abstained cases as new labels.

### Deployment: a public API and integration with institutional library and research-assessment systems.

Applications

Library and research-office screening of journals before faculty or students submit manuscripts.

Screening of reference lists and citation sources in systematic reviews and grant evaluations.

Indexing and funder due-diligence workflows that need explainable, auditable decisions.

The progressive, cost-aware, calibrated and abstaining design is reusable for other adversarial screening problems such as phishing, fake-shop and fraudulent-website detection.

REFERENCES

[1] J. Beall, "Criteria for determining predatory open-access publishers," Scholarly Open Access, vol. 3, pp. 1–6, 2015.

[2] C. Shen and B.-C. Björk, "'Predatory' open access: a longitudinal study of article volumes and market characteristics," BMC Medicine, vol. 13, no. 1, p. 230, 2015, doi: 10.1186/s12916-015-0469-2.

[3] B.-C. Björk and D. Solomon, "Open access versus subscription journals: a comparison of scientific impact," BMC Medicine, vol. 10, no. 1, p. 73, 2012, doi: 10.1186/1741-7015-10-73.

[4] K. D. Cobey, M. M. Lalu, B. Skidmore, N. Ahmadzai, A. Grudniewicz, and D. Moher, "What is a predatory journal? A scoping review," F1000Research, vol. 7, p. 1001, 2018, doi: 10.12688/f1000research.15256.2.

[5] A. Grudniewicz, D. Moher, K. D. Cobey, et al., "Predatory journals: no definition, no defence," Nature, vol. 576, no. 7786, pp. 210–212, 2019, doi: 10.1038/d41586-019-03759-y.

[6] D. Moher, L. Shamseer, K. D. Cobey, et al., "Stop this waste of people, animals and money," Nature, vol. 549, no. 7670, pp. 23–25, 2017, doi: 10.1038/549023a.

[7] L.-X. Chen, S.-W. Su, C.-H. Liao, K.-S. Wong, and S.-M. Yuan, "An open automation system for predatory journal detection," Scientific Reports, vol. 13, no. 1, p. 2976, 2023, doi: 10.1038/s41598-023-30176-z.

[8] J. A. Teixeira da Silva, "Variation in journal website characterization by an AI-driven 'predatory' journal detector," Expert Systems with Applications, vol. 283, p. 127933, 2025, doi: 10.1016/j.eswa.2025.127933.

[9] D. Al-Moghrabi, S. A. Arqub, M. P. Maroulakos, N. Pandis, and P. S. Fleming, "Can ChatGPT identify predatory biomedical and dental journals? A cross-sectional content analysis," Journal of Dentistry, vol. 142, p. 104840, 2024, doi: 10.1016/j.jdent.2024.104840.

[10] J. Wu, T. Liu, K. Mu, and L. Zhou, "Identification and causal analysis of predatory open access journals based on interpretable machine learning," Scientometrics, vol. 129, pp. 3125–3148, 2024, doi: 10.1007/s11192-024-04969-6.

[11] L. Shamseer, D. Moher, O. Maduekwe, et al., "Potential predatory and legitimate biomedical journals: can you tell the difference? A cross-sectional comparison," BMC Medicine, vol. 15, no. 1, pp. 1–14, 2017, doi: 10.1186/s12916-017-0785-9.

[12] F. Krawczyk and E. Kulczycki, "How do open access predatory journals operate in the era of artificial intelligence?," Journal of Informetrics, vol. 17, no. 2, p. 101402, 2023, doi: 10.1016/j.joi.2023.101402.

[13] M. Kachuee, K. Karkkainen, V. Ordonez, and M. Sarrafzadeh, "Cost-aware feature acquisition for dynamic health risk prediction," IEEE Journal of Biomedical and Health Informatics, vol. 23, no. 5, pp. 2056–2064, 2019, doi: 10.1109/JBHI.2018.2882772.

[14] Z. Xu, K. Q. Weinberger, and O. Chapelle, "Cost-sensitive tree of classifiers," in International Conference on Machine Learning (ICML), 2014, pp. 133–141.

[15] S. Teerapittayanon, B. McDanel, and H.-T. Kung, "BranchyNet: Fast inference via early exiting from deep neural networks," in 2016 23rd International Conference on Pattern Recognition (ICPR), IEEE, 2016, pp. 2464–2469, doi: 10.1109/ICPR.2016.7900006.

[16] W. Liu, P. Zhou, Z. Wang, Z. Zhao, H. Deng, and Q. Ju, "FastBERT: a self-distilling BERT with adaptive inference time," in Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (ACL), 2020, pp. 6036–6044, doi: 10.18653/v1/2020.acl-main.537.

[17] C. Cortes, G. DeSalvo, and M. Mohri, "Learning with rejection," in International Conference on Algorithmic Learning Theory, Springer, 2016, pp. 67–82, doi: 10.1007/978-3-319-46379-7_5.

[18] Y. Geifman and R. El-Yaniv, "Selective classification for deep neural networks," in Advances in Neural Information Processing Systems (NeurIPS), vol. 30, 2017, pp. 4878–4887.

[19] C. Guo, G. Pleiss, Y. Sun, and K. Q. Weinberger, "On calibration of modern neural networks," in International Conference on Machine Learning (ICML), PMLR, 2017, pp. 1321–1330.

[20] J. Platt, "Probabilistic outputs for support vector machines and comparisons to regularized likelihood methods," Advances in Large Margin Classifiers, vol. 10, no. 3, pp. 61–74, 1999.
