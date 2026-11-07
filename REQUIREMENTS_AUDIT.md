# Project 2 requirements audit

| Brief / screenshot requirement | Implementation | Evidence |
|---|---|---|
| Title | RFM & Behavioral Customer Segmentation | README, dashboard and notebook |
| Public e-commerce transactions | UCI Online Retail original, dataset 352, exact source and license | Bundled raw CSV, source.json, DATA_LICENSE.md |
| Manual pandas RFM baseline before clustering | Explicit Recency, distinct-invoice Frequency, Monetary groupby calculations | features.py and executed notebook sections 3–4 |
| Bucket customers into tiers | Tied-score-safe quintiles plus six ordered business tiers | baseline_tier/RFM_code in customer_segments.csv |
| K-Means on scaled RFM | Log1p + StandardScaler + KMeans, only three RFM inputs | segment.py and model.joblib |
| Elbow justification of k | k=1…10 inertia curve, normalized-chord gap, range sensitivity | elbow_diagnostics.csv and evidence PNG |
| Plain-English segment naming | Original-unit profile rules; names lead stakeholder outputs | segment_profiles.csv and dashboard |
| Actionable targeted campaigns | Cluster playbook plus manual at-risk/newly observed overlays | campaign_playbook.csv, recommended_campaign and SEGMENT_PLAYBOOK.md |
| Behavioral/household expansion acknowledged | Transaction descriptors separated from missing consented household/engagement data | README and dashboard |
| Nontechnical stakeholder interpretation | Names, original-unit medians, exportable audiences, actions and KPIs | Dashboard and HTML overview |
| Comments, framework and justified choices | Rationale in source docstrings/comments, narrative and notebook | Source, README and CASE_STUDY.md |
| GitHub-ready portfolio | Executed notebook, test suite, workflows, license, guide and bundled evidence | Repository root |

Elbow is an explicit heuristic, not proof of a unique natural k. Silhouette favors two more strongly than three and is disclosed. Historical purchase value is not net revenue/profit, and no conversion gain or campaign outcome is claimed.
