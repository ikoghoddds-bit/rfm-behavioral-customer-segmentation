# Project 2 Requirements Audit

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


## Dashboard Enhancement Mapping

| Recommendation | Implementation |
|---|---|
| Account for screenshot zoom | Explicit 16 px default, restrained typography, no assumption that the zoomed-out screenshot represented normal viewing |
| Lead with a decision | Concentration insight and action/KPI cards before detailed tables |
| Business-friendly profiles | Seven-column summary, percentage/GBP/day formats, definition tooltips, expandable behavioral fields |
| Horizontal readable charts | Full segment names and direct count/share labels |
| Stable segment identity | Teal loyal, blue developing, amber lapsed across cards, bars, scatter and publication figure |
| Value versus audience share | Paired horizontal customer/purchase-value share comparison |
| Outlier visibility | Logarithmic default, linear option, detailed hover and optional display-only 99% zoom |
| Filter consistency | KPIs, insights, profiles, charts, cards, baseline tables and exports use the selected audience |
| Benchmark separation | Explicit full-population expander and model-evidence scope |
| Better audience controls | Wider desktop sidebar, short labels, Select All, Clear and Reset |
| Immediate activation handoff | Segment-card View Audience drill-down and direct export |
| Historical context | Prominent snapshot/lookback/GBP band |
| Capitalized headings | Title Case UI headings, table labels, axes, chart titles, document and notebook headings; acronyms retained |

Customer assignment, fitted model and source CSV schemas are unchanged. Campaign actions remain hypotheses requiring controlled validation.
