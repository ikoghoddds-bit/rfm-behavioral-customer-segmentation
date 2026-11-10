# From Customer Groups To Marketing Decisions

Joseph Ikogho · Data Science Portfolio Project 2

## Problem And Framework

Marketing treats a first observed buyer, a repeat high spender and a long-inactive occasional buyer differently only if the segmentation explains how. I built a reproducible pipeline that first establishes an intuitive manual RFM benchmark, then uses K-Means to find compact groups and translates them into campaign hypotheses.

## Data And Approach

The public UCI Online Retail source contains 541,909 transaction lines. A fixed 365-day purchase window ending before December 10, 2011 yields 378,508 eligible lines, 17,756 orders and 4,264 identifiable customers. Monetary is positive purchase value in GBP, not net revenue or profit. Exclusions and provenance are audited.

I calculate Recency, distinct-invoice Frequency and Monetary in pandas before clustering. Tied-value-safe quintile scores produce six rule-based tiers. K-Means fits log1p-transformed, standardized RFM only. The largest normalized chord gap in the k=1…10 inertia curve selects three; range 1…8 also selects three. Silhouette favors two, so three is presented as a defensible finer split, not a uniquely true solution. Alternate-seed minimum ARI is 0.984; a 99%-capped sensitivity gives 0.917 ARI.

## Finding And Action

703 loyal high-value customers account for 65.5% of purchase value; 1,654 active developing customers account for 26.5%; 1,907 lapsed occasional customers account for 8.1%. Median profiles support plain-English names instead of arbitrary cluster IDs.

Recommend VIP recognition/cross-sell for loyal customers, repeat-purchase nurture for active developing customers, and low-cost reactivation pilots for lapsed customers. Preserve manual high-value-at-risk and newly observed tiers as overrides, because cluster medians can hide valuable exceptions. Export named customer audiences with the recommended campaign and measure incremental contribution in a randomized segment-level experiment.

## Decisions I Can Justify

**Why manual RFM first?** It gives stakeholders a transparent benchmark to compare with mathematical groups. It is interpretable without machine learning.

**Why distinct invoices?** Multiple products on one order are not multiple purchase occasions. Frequency must not count invoice lines.

**Why transform and scale?** Frequency and spend have long tails; unscaled GBP would dominate Euclidean distance. Log1p and standardization reduce that imbalance without deleting major accounts.

**Why k=3 despite a higher k=2 silhouette?** A specified elbow heuristic selects three over two ranges, and three profiles support a useful middle developing group. This is a tradeoff to test with stakeholders, not proof of natural categories.

**Are conversion gains demonstrated?** No. There are no marketing exposure or control outcomes. The project delivers testable actions and a measurement plan.

**Does top SKU reveal personal interests?** It reveals purchased products only. Broader interests, households and browsing intent require additional authorized data.

**What does the dashboard add?** Stakeholders can inspect profiles, compare baseline tiers, filter named audiences, export campaign groups, review elbow evidence and assign comparable RFM files to frozen groups.

## Recruiter-Safe Summary

“Built an RFM and K-Means customer-segmentation portfolio on public e-commerce transactions; translated 4,264 customer histories into three named segments, six manual benchmark tiers and targeted campaign hypotheses, with documented robustness and cleaning checks.”
