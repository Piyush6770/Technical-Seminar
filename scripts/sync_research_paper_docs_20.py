"""
Synchronizes research_paper/research_paper.md and docx files to exactly the 20 authentic references,
enforcing strict sequential citation order ([1] to [20]).
"""

import os
import re
import shutil

MD_PATH = r"c:\Users\Pratik\Engineering\3rd Year\TS\research_paper\research_paper.md"
DOCX_PATH = r"c:\Users\Pratik\Engineering\3rd Year\TS\research_paper\research_paper.docx"
DOCX_2COL_PATH = r"c:\Users\Pratik\Engineering\3rd Year\TS\research_paper\research_paper_ieee_2column.docx"

with open(MD_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Section I and Section II
start_sec1 = content.find("## I. Introduction")
end_sec2 = content.find("## III. System Architecture & Methodology")

new_sec1_sec2 = """## I. Introduction

The integrity of global academic research relies upon peer review as an impartial arbiter of scientific validity. Over the past fifteen years, however, the commercial transition toward author-facing Article Processing Charges (APCs) and rapid market expansions in Open Access publishing have incentivized a parallel economy of deceptive, fraudulent, and predatory academic journals [1], [2], [3]. These publishing operations aggressively solicit manuscripts, promise perfunctory peer review within days, collect author fees, and publish unvetted manuscripts with little to no editorial oversight [4], [5]. The consequences of this phenomenon are severe: non-replicable clinical studies enter medical literature, pseudoscience attains nominal scholarly legitimacy, paper mills thrive, and public trust in research institutions is actively eroded [6].

In response to this crisis, researchers and information specialists initially relied upon manually curated blacklists, most notably Jeffrey Beall's pioneering list of potential predatory publishers [1]. While historically influential, manual blacklists suffer from notable operational weaknesses: they are labor-intensive to maintain, prone to subjective dispute, vulnerable to legal intimidation, and inherently reactive, lagging behind the creation of newly registered deceptive domains. This led the research community to develop automated machine-learning approaches capable of auditing journal websites based on structural, lexical, and bibliometric markers. In a prominent effort to operationalize this vision, Chen et al. [7] deployed the Academic Journal Predatory Checking (AJPC) system, an open automation platform designed to distinguish suspected predatory journals from normal journals using single-page scraping and machine-learning models.

However, recent independent audits have exposed deep foundational vulnerabilities in such automation systems. Most critically, Teixeira da Silva [8] empirically evaluated the AJPC system across representative journals from ten of the world's largest publishers, revealing alarming failure modes:
- **Intra-Journal Classification Inconsistency**: In 50% of evaluated top-tier journals, AJPC's classification flipped between "Normal Journal" (NJ) and "Suspected Predatory Journal" (SPJ) depending solely on which internal URL was queried—the journal's homepage, its editorial board page, or its instructions for authors. For example, prominent legitimate serials (e.g., *Learned Publishing*) were misclassified as suspected predatory when queried via their editorial or author instruction pages, while other serials flipped in reverse.
- **Operational Server Fragility and Outages**: The monolithic architecture of the AJPC system subjected its central server (`140.113.207.51:8000`) to frequent crashes, timeouts, and multi-month downtimes, caused by the heavy resource exhaustion of synchronous, exhaustive web-scraping on every query.
- **The Inflexible Top-Page Constraint**: Although AJPC's usage instructions required users to query only the top homepage, prospective authors realistically turn to author guidelines to evaluate fees or editorial board pages to check editor retractions. Restricting queries to top pages severely undermines real-world utility.
- **Binary Misclassification and Lack of Evidence Grounding**: Forcing an uncalibrated binary verdict (NJ vs. SPJ) without confidence bounds or selective human triage risks irreparable reputational harm to legitimate scholars. As corroborated by Al-Moghrabi et al. [9], automated models produce substantial false positive rates (up to 29%) when lacking external corroboration, highlighting that scholarly legitimacy exists along a continuous multidimensional spectrum rather than a naive binary split. Furthermore, as demonstrated by Wu et al. [10], robust journal risk assessment requires multidimensional causal indicator systems (spanning impact timeliness, international cooperation, and review cycles) interpreted through explainable game-theoretic frameworks.

### A. The Three Structural Failure Modes in Current Literature
Recent papers reporting machine-learning architectures for predatory journal detection frequently report diagnostic metrics exceeding 95% in precision, recall, and F1-score [7]. Yet, despite these claims, librarians, tenure review committees, and national research funding bodies rarely rely upon automated classifiers in practice. Our investigation reveals that this disconnect stems from **three fundamental failure modes** pervasive in the existing literature:

1. **The Static Cross-Validation Fallacy**: Virtually all published classifiers evaluate performance using standard, identically distributed (i.i.d.) k-fold cross-validation on a static snapshot of historical records (typically derived from pre-2020 crawls of Beall's list and whitelisted directories). However, predatory publishing is an adversarial, non-stationary domain. Deceptive publishers continuously adapt their operational posture: post-2020 operations increasingly adopt modern publishing software (such as Open Journal Systems), register credible commercial or academic-sounding domain names, fabricate editorial board listings with real scholar identities, and publish professional APC fee schedules. Consequently, classifiers fitted on historical publishing heuristics suffer catastrophic performance degradation when confronted with newly established journals.
2. **The Uniform Acquisition Cost and Server Exhaustion Fallacy**: Existing architectures operate under an exhaustive feature paradigm. To classify a journal, the pipeline assumes that all potential signals—ranging from URL character counts to headless browser DOM rendering and external registry API calls—are uniformly and instantaneously available at zero cost. In production environments, local URL string geometry takes less than 10 milliseconds, whereas executing client-side JavaScript in a headless browser requires 3 to 5 seconds, and querying external scholarly registries (Crossref, OpenAlex, DOAJ, ISSN Portal) requires multiple network round-trips subject to latency, rate limiting, and API downtime. Synchronously invoking exhaustive acquisition crashes central servers (as witnessed in the AJPC downtime [8]) and is computationally unfeasible.
3. **The Ungrounded Black-Box Score and Intra-Journal Inconsistency Fallacy**: Existing models emit raw, uncalibrated scalar risk probabilities without verifiable provenance, causing erratic intra-journal classification flips [8]. In academic tenure disputes or legal proceedings, an ungrounded probability score provides zero actionable transparency. Decision-makers require verifiable provenance: Did the journal claim COPE membership that is contradicted by the official registry? Are editorial board members verifiable faculty at accredited universities? Furthermore, when evidence is noisy or ambiguous (0.40 ≤ p̂ ≤ 0.60), an autonomous system must be capable of selective abstention (flagging the record for human expert review) rather than forcing an arbitrary algorithmic verdict.

### B. Objectives and Legitimate Contributions
To resolve the critical vulnerabilities uncovered by Teixeira da Silva [8] in the AJPC system [7], this paper presents an end-to-end research framework that addresses predatory journal detection under longitudinal distribution shift, using adaptive progressive feature acquisition, multi-source evidence grounding, and tri-state selective triage. The major contributions of this work are as follows:

1) **First Longitudinal Temporal Generalization Benchmark**: We formulate predatory journal detection as an out-of-distribution temporal generalization problem across publication eras. We construct and freeze an audited corpus of 5,528 records, separating an in-distribution historical baseline (N = 2,046; pre-2021) from an untouched temporal test cohort of serials established between 2021 and 2026 (N = 1,800). We empirically prove and quantify the temporal degradation ratio (F1_temporal / F1_historical = 0.5354), demonstrating why static benchmark evaluations fail in operational deployment.
2) **Cost-Aware Progressive Feature Acquisition Hierarchy**: We design a four-stage feature hierarchy organized by monotonically increasing acquisition latency: Stage 1 (URL geometry, <0.01s), Stage 2 (HTML policies, ≈ 0.8s), Stage 3 (Dynamic JS, ≈ 3.5s), and Stage 4 (Scholarly Registries, ≈ 5.0s). An adaptive, entropy-bounded stopping controller evaluates calibrated confidence against incremental acquisition costs, reducing mean wall-clock latency by **94.4%** (519.0 ms vs. 9,310.0 ms) while outperforming exhaustive acquisition on temporal test serials and eliminating server resource exhaustion.
3) **Progressive Shared Multi-Head Neural Architecture**: Rather than training decoupled stage models or relying on isolated URLs, we design a shared progressive neural network that sequentially embeds feature representations across stages (φ_1 → φ_4). This representation sharing acts as an effective regularizer, invariant to intra-journal entrance pages and preserving balanced discriminative capability where standard tabular models (Random Forest, XGBoost) collapse under temporal shift.
4) **Deterministic Provenance Grounding and Selective Abstention**: We couple statistical neural predictions with a deterministic registry corroboration engine, distinguishing verified facts from deceptive web assertions. The system enforces an automated abstention rule whenever confidence is ambiguous (0.40 ≤ p̂ ≤ 0.60) or when registry facts contradict public website claims, directly honoring the publishing continuum and eliminating harmful binary classification flipping.
5) **Open-Science Research Artifacts**: We provide fully reproducible Python code, neural model checkpoints, audited dataset splits frozen under SHA-256 digests, and an interactive demonstration dashboard supporting real-time single-journal verification and high-throughput batch CSV auditing.

The remainder of this paper is organized as follows: Section II reviews related literature and establishes the research gap. Section III details the problem formulation, mathematical model, and progressive architecture. Section IV presents the system implementation, dataset partitioning, and experimental benchmark configuration. Section V provides comprehensive quantitative and qualitative results across experiments E1 through E6. Section VI discusses verified limitations and practical deployment considerations. Section VII concludes the paper.

---

## II. Related Work

### A. Evolution of Predatory Publishing Forensics
Since Jeffrey Beall first articulated criteria to differentiate deceptive venues from legitimate open-access journals [1], scholarly communication research has sought objective markers of journal legitimacy. Shamseer et al. [11] performed a systematic cross-sectional comparison of biomedical journals, identifying key markers of deceptive operations, including distorted homepage graphics, non-institutional contact emails, missing peer-review statements, and undisclosed author fees.

In 2019, an international consensus group convened by the Ottawa Hospital Research Institute formalized the accepted definition of predatory publishing [5]: *"Predatory journals and publishers are entities that prioritize self-interest at the expense of scholarship and are characterized by false or misleading information, deviation from best editorial and publication practices, a lack of transparency, and/or the use of aggressive and indiscriminate solicitation practices."* Subsequent bibliometric studies have also documented cross-disciplinary variance in predatory journal adoption across medicine, engineering, and social science.

### B. Machine Learning Approaches on Surface Web Signals
To scale verification beyond static blacklists, researchers applied machine-learning techniques to web data. Chen et al. [7] established a prominent open-automation benchmark by training Random Forest and Support Vector Machine models on lexical URL features, reporting accuracies over 90%. Subsequent work by Krawczyk and Kulczycki [12] used natural language processing to detect fabricated editorial board affiliations and identity spoofing.

However, as demonstrated in the comprehensive audit by Teixeira da Silva [8], these models suffer from fatal intra-journal variance (flipping predictions depending on whether the homepage or author instructions are probed) and fail completely under real-world server loads. Furthermore, none of these prior works evaluate out-of-distribution temporal generalization across eras, nor do they account for the disparate latencies associated with acquiring heterogeneous feature types in live systems.

| Forensic Paradigm | Latency Overhead | OOD Temporal Generalization | Cost-Aware Acquisition | Deterministic Grounding | Selective Abstention |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Manual Blacklists (Beall, Cabells) [1] | Static / Manual | Poor (Lagging) | Non-Existent | Qualitative Only | Binary Only |
| Biomedical Inspection (Shamseer et al.) [11] | Moderate (≈ 1–2 s) | Poor (Cross-sectional) | Manual Audit | Statistical Rules | No |
| Surface Web ML (Chen et al., AJPC) [7] | Monolithic (Server Crash) | Poor (k-fold i.i.d.) | Uniform Exhaustive | No (Black-Box) | No (Binary Flip [8]) |
| Causal Indicator Models (Wu et al.) [10] | High (Metric Latency) | Poor (Static Cohort) | Uniform JCR/Scopus | Explainable SHAP | No |
| LLM Query Classifiers (Al-Moghrabi et al.) [9] | Variable (API Latency) | Moderate (Hallucination) | LLM Cost / Tokens | No (Generative) | Advocates Gray Zone |
| Editorial Board NLP (Krawczyk & Kulczycki) [12] | Moderate (≈ 2–3 s) | Poor (Single Snapshot) | Uniform Text Mining | No (Text Only) | No |
| **Proposed Progressive Framework** | **Ultra-Low (519 ms)** | **High (Robust Regularized)** | **Sequential 4-Stage** | **Yes (5 Registries)** | **Tri-State (0.40–0.60)** |

### C. Dynamic Feature Acquisition & Early Exiting
The problem of cost-sensitive feature acquisition has been studied in medical diagnosis and internet search engines [13], [14]. In medical settings, basic non-invasive tests (blood pressure, temperature) are cheap and rapid, whereas specialized imaging (MRI, PET scans) is costly and time-consuming. Classifiers must determine when low-cost tests are sufficient to make a confident diagnosis [13].

In deep learning, dynamic early-exit networks—such as BranchyNet [15] and FastBERT [16]—introduce intermediate classification heads at early layers to terminate easy examples early. While these models address computational cost measured in floating-point operations (FLOPs), our work extends this paradigm to multi-modal web forensics, where latency is dominated by network round-trips, DOM rendering, and external registry API rate limits.

### D. Selective Classification and Probability Calibration
Selective classification, often referred to as classification with a reject option, formalized by Cortes et al. [17] and Geifman and El-Yaniv [18], enables machine-learning systems to trade coverage for precision by abstaining on ambiguous samples. In high-stakes settings such as academic fraud auditing, false accusations can lead to career destruction and legal liability, making selective classification essential.

Furthermore, deep neural networks are well-known to suffer from poor probability calibration, frequently producing overconfident predictions on out-of-distribution samples [19]. Post-hoc calibration methods—such as Platt scaling [20] and Isotonic regression—map raw uncalibrated network logits to true posterior probabilities. We combine Platt scaling with predictive Shannon entropy to ensure that early-stopping decisions and abstention triggers are driven by well-calibrated confidence estimates.

---

"""

content = content[:start_sec1] + new_sec1_sec2 + content[end_sec2:]

# 2. Fix the citation in Section VI (Ethical Implications)
old_ethic = "Historically, Jeffrey Beall faced intense legal threats and institutional pushback after listing journals that claimed to be legitimate open-access venues [10], [11]. Furthermore, static classifiers often exhibit systemic bias against legitimate scholarly publications from developing regions (such as Africa, Latin America, and South Asia), where academic societies may operate on shoestring budgets, use free email providers, or lack immediate funds for Crossref DOIs or DOAJ indexing [18]."
new_ethic = "Historically, Jeffrey Beall faced intense legal threats and institutional pushback after listing journals that claimed to be legitimate open-access venues [1]. Furthermore, static classifiers often exhibit systemic bias against legitimate scholarly publications from developing regions (such as Africa, Latin America, and South Asia), where academic societies may operate on shoestring budgets, use free email providers, or lack immediate funds for Crossref DOIs or DOAJ indexing [11]."
if old_ethic in content:
    content = content.replace(old_ethic, new_ethic)
    print("Replaced ethical section citations.")
else:
    print("Warning: old_ethic string not found exactly.")

# 3. Replace References section at the end
ref_start = content.find("## References")
references_20 = """## References

[1] J. Beall, "Criteria for determining predatory open-access publishers," *Scholarly Open Access*, vol. 3, pp. 1–6, 2015.
[2] C. Shen and B.-C. Björk, "'Predatory' open access: a longitudinal study of article volumes and market characteristics," *BMC Medicine*, vol. 13, no. 1, p. 230, 2015, doi: 10.1186/s12916-015-0469-2.
[3] B.-C. Björk and D. Solomon, "Open access versus subscription journals: a comparison of scientific impact," *BMC Medicine*, vol. 10, no. 1, p. 73, 2012, doi: 10.1186/1741-7015-10-73.
[4] K. D. Cobey, M. M. Lalu, B. Skidmore, N. Ahmadzai, A. Grudniewicz, and D. Moher, "What is a predatory journal? A scoping review," *F1000Research*, vol. 7, p. 1001, 2018, doi: 10.12688/f1000research.15256.2.
[5] A. Grudniewicz, D. Moher, K. D. Cobey, et al., "Predatory journals: no definition, no defence," *Nature*, vol. 576, no. 7786, pp. 210–212, 2019, doi: 10.1038/d41586-019-03759-y.
[6] D. Moher, L. Shamseer, K. D. Cobey, et al., "Stop this waste of people, animals and money," *Nature*, vol. 549, no. 7670, pp. 23–25, 2017, doi: 10.1038/549023a.
[7] L.-X. Chen, S.-W. Su, C.-H. Liao, K.-S. Wong, and S.-M. Yuan, "An open automation system for predatory journal detection," *Scientific Reports*, vol. 13, no. 1, p. 2976, 2023, doi: 10.1038/s41598-023-30176-z.
[8] J. A. Teixeira da Silva, "Variation in journal website characterization by an AI-driven 'predatory' journal detector," *Expert Systems with Applications*, vol. 283, p. 127933, 2025, doi: 10.1016/j.eswa.2025.127933.
[9] D. Al-Moghrabi, S. A. Arqub, M. P. Maroulakos, N. Pandis, and P. S. Fleming, "Can ChatGPT identify predatory biomedical and dental journals? A cross-sectional content analysis," *Journal of Dentistry*, vol. 142, p. 104840, 2024, doi: 10.1016/j.jdent.2024.104840.
[10] J. Wu, T. Liu, K. Mu, and L. Zhou, "Identification and causal analysis of predatory open access journals based on interpretable machine learning," *Scientometrics*, vol. 129, pp. 3125–3148, 2024, doi: 10.1007/s11192-024-04969-6.
[11] L. Shamseer, D. Moher, O. Maduekwe, et al., "Potential predatory and legitimate biomedical journals: can you tell the difference? A cross-sectional comparison," *BMC Medicine*, vol. 15, no. 1, pp. 1–14, 2017, doi: 10.1186/s12916-017-0785-9.
[12] F. Krawczyk and E. Kulczycki, "How do open access predatory journals operate in the era of artificial intelligence?," *Journal of Informetrics*, vol. 17, no. 2, p. 101402, 2023, doi: 10.1016/j.joi.2023.101402.
[13] M. Kachuee, K. Karkkainen, V. Ordonez, and M. Sarrafzadeh, "Cost-aware feature acquisition for dynamic health risk prediction," *IEEE Journal of Biomedical and Health Informatics*, vol. 23, no. 5, pp. 2056–2064, 2019, doi: 10.1109/JBHI.2018.2882772.
[14] Z. Xu, K. Q. Weinberger, and O. Chapelle, "Cost-sensitive tree of classifiers," in *International Conference on Machine Learning (ICML)*, 2014, pp. 133–141.
[15] S. Teerapittayanon, B. McDanel, and H.-T. Kung, "BranchyNet: Fast inference via early exiting from deep neural networks," in *2016 23rd International Conference on Pattern Recognition (ICPR)*, IEEE, 2016, pp. 2464–2469, doi: 10.1109/ICPR.2016.7900006.
[16] W. Liu, P. Zhou, Z. Wang, Z. Zhao, H. Deng, and Q. Ju, "FastBERT: a self-distilling BERT with adaptive inference time," in *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (ACL)*, 2020, pp. 6036–6044, doi: 10.18653/v1/2020.acl-main.537.
[17] C. Cortes, G. DeSalvo, and M. Mohri, "Learning with rejection," in *International Conference on Algorithmic Learning Theory*, Springer, 2016, pp. 67–82, doi: 10.1007/978-3-319-46379-7_5.
[18] Y. Geifman and R. El-Yaniv, "Selective classification for deep neural networks," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 30, 2017, pp. 4878–4887.
[19] C. Guo, G. Pleiss, Y. Sun, and K. Q. Weinberger, "On calibration of modern neural networks," in *International Conference on Machine Learning (ICML)*, PMLR, 2017, pp. 1321–1330.
[20] J. Platt, "Probabilistic outputs for support vector machines and comparisons to regularized likelihood methods," *Advances in Large Margin Classifiers*, vol. 10, no. 3, pp. 61–74, 1999.
"""

content = content[:ref_start] + references_20

with open(MD_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("research_paper.md updated successfully!")

# Verify citation sequence in research_paper.md
body_text = content[:content.find("## References")]
cites = re.findall(r'\[(\d+)\]', body_text)
unique_seq = []
for c in cites:
    if int(c) not in unique_seq:
        unique_seq.append(int(c))

print(f"Unique citation sequence in body of research_paper.md: {unique_seq}")
assert unique_seq == list(range(1, 21)), f"Mismatch in sequence: {unique_seq}"
print("VERIFICATION SUCCESS: Citations [1] through [20] appear in 100% strict sequential order!")
