"""
Updates paper/manuscript.tex to cleanly reference the 20 authentic papers,
enforcing 100% strict sequential IEEE order (1 to 20).
"""

import os
import re

tex_path = r"c:\Users\Pratik\Engineering\3rd Year\TS\paper\manuscript.tex"

with open(tex_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Section I and Section II up to subsection D
# Find bounds of section 1
start_sec1 = content.find(r"\section{Introduction}")
end_sec2 = content.find(r"\section{Audited Dataset Architecture and Defensible Partitions}")

new_intro_related = r"""\section{Introduction}
\IEEEPARstart{T}{he} integrity of global academic research relies upon peer review as an impartial arbiter of scientific validity. Over the past fifteen years, however, the commercial transition toward author-facing Article Processing Charges (APCs) and rapid market expansions in Open Access publishing have incentivized a parallel economy of deceptive, fraudulent, and predatory academic journals~\cite{beall2015criteria, shen2015longitudinal, bjork2012open}. These publishing operations aggressively solicit manuscripts, promise perfunctory peer review within days, collect author fees, and publish unvetted manuscripts with little to no editorial oversight~\cite{cobey2018what, grudniewicz2019predatory}. The consequences of this phenomenon are severe: non-replicable clinical studies enter medical literature, pseudoscience attains nominal scholarly legitimacy, paper mills thrive, and public trust in research institutions is actively eroded~\cite{moher2017stop}.

In response to this crisis, researchers and information specialists initially relied upon manually curated blacklists, most notably Jeffrey Beall's pioneering list of potential predatory publishers~\cite{beall2015criteria}. While historically influential, manual blacklists suffer from notable operational weaknesses: they are labor-intensive to maintain, prone to subjective dispute, vulnerable to legal intimidation, and inherently reactive, lagging behind the creation of newly registered deceptive domains. This led the research community to develop automated machine-learning approaches capable of auditing journal websites based on structural, lexical, and bibliometric markers. In a prominent effort to operationalize this vision, Chen et al.~\cite{chen2023open} deployed the Academic Journal Predatory Checking (AJPC) system, an open automation platform designed to distinguish suspected predatory journals from normal journals using single-page scraping and machine-learning models.

However, recent independent audits have exposed deep foundational vulnerabilities in such automation systems. Most critically, Teixeira da Silva~\cite{teixeira2025variation} empirically evaluated the AJPC system across representative journals from ten of the world's largest publishers, revealing alarming failure modes:
\begin{itemize}
    \item \textbf{Intra-Journal Classification Inconsistency}: In 50\% of evaluated top-tier journals, AJPC's classification flipped between ``Normal Journal'' (NJ) and ``Suspected Predatory Journal'' (SPJ) depending solely on which internal URL was queried---the journal's homepage, its editorial board page, or its instructions for authors. For example, prominent legitimate serials (e.g., \textit{Learned Publishing}) were misclassified as suspected predatory when queried via their editorial or author instruction pages, while other serials flipped in reverse.
    \item \textbf{Operational Server Fragility and Outages}: The monolithic architecture of the AJPC system subjected its central server (\texttt{140.113.207.51:8000}) to frequent crashes, timeouts, and multi-month downtimes, caused by the heavy resource exhaustion of synchronous, exhaustive web-scraping on every query.
    \item \textbf{The Inflexible Top-Page Constraint}: Although AJPC's usage instructions required users to query only the top homepage, prospective authors realistically turn to author guidelines to evaluate fees or editorial board pages to check editor retractions. Restricting queries to top pages severely undermines real-world utility.
    \item \textbf{Binary Misclassification and Lack of Evidence Grounding}: Forcing an uncalibrated binary verdict (NJ vs. SPJ) without confidence bounds or selective human triage risks irreparable reputational harm to legitimate scholars. As corroborated by Al-Moghrabi et al.~\cite{almoghrabi2024chatgpt}, automated models produce substantial false positive rates (up to 29\%) when lacking external corroboration, highlighting that scholarly legitimacy exists along a continuous multidimensional spectrum rather than a naive binary split. Furthermore, as demonstrated by Wu et al.~\cite{wu2024identification}, robust journal risk assessment requires multidimensional causal indicator systems (spanning impact timeliness, international cooperation, and review cycles) interpreted through explainable game-theoretic frameworks.
\end{itemize}

\subsection{The Three Structural Failure Modes in Current Literature}
Recent papers reporting machine-learning architectures for predatory journal detection frequently report diagnostic metrics exceeding $95\%$ in precision, recall, and $F_1$-score~\cite{chen2023open}. Yet, despite these claims, librarians, tenure review committees, and national research funding bodies rarely rely upon automated classifiers in practice. Our investigation reveals that this disconnect stems from \textbf{three fundamental failure modes} pervasive in the existing literature:

\begin{enumerate}
    \item \textbf{The Static Cross-Validation Fallacy}: Virtually all published classifiers evaluate performance using standard, identically distributed ($i.i.d.$) $k$-fold cross-validation on a static snapshot of historical records (typically derived from pre-2020 crawls of Beall's list and whitelisted directories). However, predatory publishing is an adversarial, non-stationary domain. Deceptive publishers continuously adapt their operational posture: post-2020 operations increasingly adopt modern publishing software (such as Open Journal Systems), register credible commercial or academic-sounding domain names, fabricate editorial board listings with real scholar identities, and publish professional APC fee schedules. Consequently, classifiers fitted on historical publishing heuristics suffer catastrophic performance degradation when confronted with newly established journals.
    \item \textbf{The Uniform Acquisition Cost and Server Exhaustion Fallacy}: Existing architectures operate under an exhaustive feature paradigm. To classify a journal, the pipeline assumes that all potential signals---ranging from URL character counts to headless browser DOM rendering and external registry API calls---are uniformly and instantaneously available at zero cost. In production environments, local URL string geometry takes less than $10$ milliseconds, whereas executing client-side JavaScript in a headless browser requires $3$ to $5$ seconds, and querying external scholarly registries (Crossref, OpenAlex, DOAJ, ISSN Portal) requires multiple network round-trips subject to latency, rate limiting, and API downtime. Synchronously invoking exhaustive acquisition crashes central servers (as witnessed in the AJPC downtime~\cite{teixeira2025variation}) and is computationally unfeasible.
    \item \textbf{The Ungrounded Black-Box Score and Intra-Journal Inconsistency Fallacy}: Existing models emit raw, uncalibrated scalar risk probabilities without verifiable provenance, causing erratic intra-journal classification flips~\cite{teixeira2025variation}. In academic tenure disputes or legal proceedings, an ungrounded probability score provides zero actionable transparency. Decision-makers require verifiable provenance: Did the journal claim COPE membership that is contradicted by the official registry? Are editorial board members verifiable faculty at accredited universities? Furthermore, when evidence is noisy or ambiguous ($0.40 \le \hat{p} \le 0.60$), an autonomous system must be capable of \textit{selective abstention} (flagging the record for human expert review) rather than forcing an arbitrary algorithmic verdict.
\end{enumerate}

\subsection{Our Proposed Framework and Contributions}
To resolve the critical vulnerabilities uncovered by Teixeira da Silva~\cite{teixeira2025variation} in the AJPC system~\cite{chen2023open}, this paper presents an end-to-end research framework that addresses predatory journal detection under longitudinal distribution shift, using adaptive progressive feature acquisition, multi-source evidence grounding, and tri-state selective triage. The major contributions of this work are as follows:

\begin{itemize}
    \item \textbf{First Longitudinal Temporal Generalization Benchmark}: We formulate predatory journal detection as an out-of-distribution temporal generalization problem across publication eras. We construct and freeze an audited corpus of $5,528$ records, separating an in-distribution historical baseline ($N=2,046$; pre-2021) from an untouched temporal test cohort of serials established between 2021 and 2026 ($N=1,800$). We empirically prove and quantify the temporal degradation ratio ($F_1^{\text{temporal}} / F_1^{\text{historical}} = 0.5354$), demonstrating why static benchmark evaluations fail in operational deployment.
    \item \textbf{Cost-Aware Progressive Feature Acquisition Hierarchy}: We design a four-stage feature hierarchy organized by monotonically increasing acquisition latency: Stage 1 (URL geometry, $<0.01$s), Stage 2 (HTML policies, $\approx 0.8$s), Stage 3 (Dynamic JS, $\approx 3.5$s), and Stage 4 (Scholarly Registries, $\approx 5.0$s). An adaptive, entropy-bounded stopping controller evaluates calibrated confidence against incremental acquisition costs, reducing mean wall-clock latency by \textbf{94.4\%} while outperforming exhaustive acquisition on temporal test serials and eliminating server resource exhaustion.
    \item \textbf{Progressive Shared Multi-Head Neural Architecture}: Rather than training decoupled stage models or relying on isolated URLs, we design a shared progressive neural network that sequentially embeds feature representations across stages ($\phi_1 \to \phi_4$). This representation sharing acts as an effective regularizer, invariant to intra-journal entrance pages and preserving balanced discriminative capability where standard tabular models (Random Forest, XGBoost) collapse under temporal shift.
    \item \textbf{Deterministic Provenance Grounding and Selective Abstention}: We couple statistical neural predictions with a deterministic registry corroboration engine, distinguishing verified facts from deceptive web assertions. The system enforces an automated abstention rule whenever confidence is ambiguous ($0.40 \le \hat{p} \le 0.60$) or when registry facts contradict public website claims, directly honoring the publishing continuum and eliminating harmful binary classification flipping.
    \item \textbf{Interactive Demonstration System \& Open Artifacts}: We provide open-source code, trained model checkpoints, audited dataset cohorts frozen under SHA-256 digests, and an interactive demonstration dashboard supporting real-time single-journal inspection and high-throughput batch CSV auditing.
\end{itemize}

\section{Related Work}

\subsection{The Evolution of Predatory Publishing Forensics}
Since Jeffrey Beall first articulated criteria to differentiate deceptive venues from legitimate open-access journals~\cite{beall2015criteria}, scholarly communication research has sought objective markers of journal legitimacy. Shamseer et al.~\cite{shamseer2017potential} performed a systematic cross-sectional comparison of biomedical journals, identifying key markers of deceptive operations, including distorted homepage graphics, non-institutional contact emails, missing peer-review statements, and undisclosed author fees.

In 2019, an international consensus group convened by the Ottawa Hospital Research Institute formalized the accepted definition of predatory publishing~\cite{grudniewicz2019predatory}: \textit{``Predatory journals and publishers are entities that prioritize self-interest at the expense of scholarship and are characterized by false or misleading information, deviation from best editorial and publication practices, a lack of transparency, and/or the use of aggressive and indiscriminate solicitation practices.''} Subsequent bibliometric studies have also documented cross-disciplinary variance in predatory journal adoption across medicine, engineering, and social science.

\subsection{Machine Learning Approaches on Surface Web Signals}
To scale verification beyond static blacklists, researchers applied machine-learning techniques to web data. Chen et al.~\cite{chen2023open} established a prominent open-automation benchmark by training Random Forest and Support Vector Machine models on lexical URL features, reporting accuracies over $90\%$. Subsequent work by Krawczyk and Kulczycki~\cite{krawczyk2023open} used natural language processing to detect fabricated editorial board affiliations and identity spoofing.

However, as demonstrated in the comprehensive audit by Teixeira da Silva~\cite{teixeira2025variation}, these models suffer from fatal intra-journal variance (flipping predictions depending on whether the homepage or author instructions are probed) and fail completely under real-world server loads. Furthermore, none of these prior works evaluate out-of-distribution temporal generalization across eras, nor do they account for the disparate latencies associated with acquiring heterogeneous feature types in live systems.

\begin{table*}[t]
\centering
\caption{Critical Literature Comparison in Predatory Journal Detection and Forensics}
\label{tab:lit_comp}
\resizebox{\textwidth}{!}{%
\begin{tabular}{llccccc}
\toprule
\textbf{Approach / Reference} & \textbf{Feature Domain} & \textbf{Temporal Split?} & \textbf{Cost-Aware?} & \textbf{Shared Architecture?} & \textbf{Calibrated?} & \textbf{Selective Abstention?} \\
\midrule
Shamseer et al. (2017)~\cite{shamseer2017potential} & Biomedical HTML Inspection & No (Cross-sectional) & No (Manual Audit) & No (Statistical Rules) & No & No \\
Chen et al. (2023, AJPC)~\cite{chen2023open} & Lexical URL \& DOM & No ($k$-fold $i.i.d.$) & No (Uniform / Server Crash) & No (Single SVM / RF) & No & No (Binary Flip~\cite{teixeira2025variation}) \\
Teixeira da Silva (2025)~\cite{teixeira2025variation} & AJPC URL Inconsistency Audit & No (Multi-URL Probe) & No (Manual Test) & No (Empirical Audit) & No & Advocates Gray Zone \\
Wu et al. (2024)~\cite{wu2024identification} & 4-Dim Indicators \& SHAP & No (Static 2020--23) & No (Uniform JCR/Scopus) & No (XGBoost+SHAP) & No & No \\
Al-Moghrabi et al. (2024)~\cite{almoghrabi2024chatgpt} & LLM / ChatGPT Queries & No (Cross-sectional) & No (Manual Prompting) & No (LLM API) & No & Recommends Credit Rating \\
Krawczyk \& Kulczycki (2023)~\cite{krawczyk2023open} & Editorial Board NLP & No (Single Snapshot) & No (Uniform) & No (Transformer Models) & No & No \\
\midrule
\textbf{This Work (Proposed Framework)} & \textbf{Hierarchical (A+B+C+D)} & \textbf{Yes (Pre/Post-2021)} & \textbf{Yes (Adaptive Stopping)} & \textbf{Yes (Progressive Shared NN)} & \textbf{Yes (Platt + ECE)} & \textbf{Yes (Registry Grounding)} \\
\bottomrule
\end{tabular}%
}
\end{table*}

\subsection{Cost-Aware Machine Learning and Dynamic Early Exits}
The problem of cost-sensitive feature acquisition has been studied in medical diagnosis and internet search engines~\cite{kachuee2019cost, xu2014classifier}. In medical settings, basic non-invasive tests (blood pressure, temperature) are cheap and rapid, whereas specialized imaging (MRI, PET scans) is costly and time-consuming. Classifiers must determine when low-cost tests are sufficient to make a confident diagnosis~\cite{kachuee2019cost}.

In deep learning, dynamic early-exit networks---such as BranchyNet~\cite{teerapittayanon2016branchynet} and FastBERT~\cite{liu2020fastbert}---introduce intermediate classification heads at early layers to terminate easy examples early. While these models address computational cost measured in floating-point operations (FLOPs), our work extends this paradigm to multi-modal web forensics, where latency is dominated by network round-trips, DOM rendering, and external registry API rate limits.

\subsection{Selective Classification and Probability Calibration}
Selective classification, often referred to as classification with a reject option, formalized by Cortes et al.~\cite{cortes2016learning} and Geifman and El-Yaniv~\cite{geifman2017selective}, enables machine-learning systems to trade coverage for precision by abstaining on ambiguous samples. In high-stakes settings such as academic fraud auditing, false accusations can lead to career destruction and legal liability, making selective classification essential.

Furthermore, deep neural networks are well-known to suffer from poor probability calibration, frequently producing overconfident predictions on out-of-distribution samples~\cite{guo2017calibration}. Post-hoc calibration methods---such as Platt scaling~\cite{platt1999probabilistic} and Isotonic regression---map raw uncalibrated network logits to true posterior probabilities. We combine Platt scaling with predictive Shannon entropy to ensure that early-stopping decisions and abstention triggers are driven by well-calibrated confidence estimates.

"""

content = content[:start_sec1] + new_intro_related + content[end_sec2:]

# 2. In Section IV, remove \cite{cope2022principles}
content = content.replace(r"COPE publication ethics declaration~\cite{cope2022principles}", "COPE publication ethics declaration")

# 3. In Section VI, remove \cite{brier1950verification}
content = content.replace(r"Brier Score~\cite{brier1950verification}", "Brier Score")

# 4. In Section III, ensure \cite{chen2023open} is used
content = re.sub(r'\\cite\{nctu2023baseline\}', r'\\cite{chen2023open}', content)

# 5. Update thebibliography to 20 items
bib_pos = content.find(r"\begin{thebibliography}")
new_bib = r"""\begin{thebibliography}{20}
\bibitem{beall2015criteria}
J.~Beall, ``Criteria for determining predatory open-access publishers,'' \emph{Scholarly Open Access}, vol.~3, pp. 1--6, 2015.

\bibitem{shen2015longitudinal}
C.~Shen and B.-C. Bj{\"o}rk, ``'Predatory' open access: a longitudinal study of article volumes and market characteristics,'' \emph{BMC Medicine}, vol.~13, no.~1, p. 230, 2015.

\bibitem{bjork2012open}
B.-C. Bj{\"o}rk and D.~Solomon, ``Open access versus subscription journals: a comparison of scientific impact,'' \emph{BMC Medicine}, vol.~10, no.~1, p.~73, 2012.

\bibitem{cobey2018what}
K.~D. Cobey, M.~M. Lalu, B.~Skidmore, N.~Ahmadzai, A.~Grudniewicz, and D.~Moher, ``What is a predatory journal? A scoping review,'' \emph{F1000Research}, vol.~7, p. 1001, 2018.

\bibitem{grudniewicz2019predatory}
A.~Grudniewicz, D.~Moher, K.~D. Cobey \emph{et~al.}, ``Predatory journals: no definition, no defence,'' \emph{Nature}, vol. 576, no. 7786, pp. 210--212, 2019.

\bibitem{moher2017stop}
D.~Moher \emph{et~al.}, ``Stop this waste of people, animals and money,'' \emph{Nature}, vol. 549, no. 7670, pp. 23--25, 2017.

\bibitem{chen2023open}
L.-X. Chen, S.-W. Su, C.-H. Liao, K.-S. Wong, and S.-M. Yuan, ``An open automation system for predatory journal detection,'' \emph{Scientific Reports}, vol.~13, no.~1, p. 2976, 2023.

\bibitem{teixeira2025variation}
J.~A. Teixeira da Silva, ``Variation in journal website characterization by an AI-driven ``predatory'' journal detector,'' \emph{Expert Systems with Applications}, vol. 283, p. 127933, 2025.

\bibitem{almoghrabi2024chatgpt}
D.~Al-Moghrabi, S.~Abu Arqub, M.~P. Maroulakos, N.~Pandis, and P.~S. Fleming, ``Can ChatGPT identify predatory biomedical and dental journals? A cross-sectional content analysis,'' \emph{Journal of Dentistry}, vol. 142, p. 104840, 2024.

\bibitem{wu2024identification}
J.~Wu, T.~Liu, K.~Mu, and L.~Zhou, ``Identification and causal analysis of predatory open access journals based on interpretable machine learning,'' \emph{Scientometrics}, vol. 129, no.~4, pp. 2131--2158, 2024.

\bibitem{shamseer2017potential}
L.~Shamseer \emph{et~al.}, ``Potential predatory and legitimate biomedical journals: can you tell the difference? A cross-sectional comparison,'' \emph{BMC Medicine}, vol.~15, no.~1, pp. 1--14, 2017.

\bibitem{krawczyk2023open}
F.~Krawczyk and E.~Kulczycki, ``How do open access predatory journals operate in the era of artificial intelligence?'' \emph{Journal of Informetrics}, vol.~17, no.~2, p. 101402, 2023.

\bibitem{kachuee2019cost}
M.~Kachuee, K.~Karkkainen, V.~Ordonez, and M.~Sarrafzadeh, ``Cost-aware feature acquisition for dynamic health risk prediction,'' \emph{IEEE Journal of Biomedical and Health Informatics}, vol.~23, no.~5, pp. 2056--2064, 2019.

\bibitem{xu2014classifier}
Z.~Xu, K.~Q. Weinberger, and O.~Chapelle, ``Cost-sensitive tree of classifiers,'' in \emph{Proceedings of the International Conference on Machine Learning (ICML)}, 2014, pp. 133--141.

\bibitem{teerapittayanon2016branchynet}
S.~Teerapittayanon, B.~McDanel, and H.-T. Kung, ``BranchyNet: Fast inference via early exiting from deep neural networks,'' in \emph{2016 23rd International Conference on Pattern Recognition (ICPR)}, IEEE, 2016, pp. 2464--2469.

\bibitem{liu2020fastbert}
W.~Liu, P.~Zhou, Z.~Wang, Z.~Zhao, H.~Deng, and Q.~Ju, ``FastBERT: a self-distilling BERT with adaptive inference time,'' in \emph{Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (ACL)}, 2020, pp. 6036--6044.

\bibitem{cortes2016learning}
C.~Cortes, G.~DeSalvo, and M.~Mohri, ``Learning with rejection,'' in \emph{International Conference on Algorithmic Learning Theory}, Springer, 2016, pp. 67--82.

\bibitem{geifman2017selective}
Y.~Geifman and R.~El-Yaniv, ``Selective classification for deep neural networks,'' in \emph{Advances in Neural Information Processing Systems (NeurIPS)}, vol.~30, 2017, pp. 4878--4887.

\bibitem{guo2017calibration}
C.~Guo, G.~Pleiss, Y.~Sun, and K.~Q. Weinberger, ``On calibration of modern neural networks,'' in \emph{International Conference on Machine Learning (ICML)}, PMLR, 2017, pp. 1321--1330.

\bibitem{platt1999probabilistic}
J.~Platt, ``Probabilistic outputs for support vector machines and comparisons to regularized likelihood methods,'' \emph{Advances in Large Margin Classifiers}, vol.~10, no.~3, pp. 61--74, 1999.
\end{thebibliography}
"""
content = content[:bib_pos] + new_bib + "\n\\end{document}\n"

with open(tex_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated paper/manuscript.tex successfully.")
