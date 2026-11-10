# Model Card

## Identity And Use

RFM & Behavioral Customer Segmentation · Joseph Ikogho · Descriptive portfolio model. Supports audience profiling and experimental marketing design. Does not estimate churn, conversion probability, treatment uplift, household attributes or future lifetime value.

## Population And Preparation

UCI Online Retail original, dataset 352, CC BY 4.0. Reference date 2011-12-10; window [2010-12-10, 2011-12-10); GBP. 4,264 customers with at least one eligible positive purchase. Missing-ID, cancellation/nonpositive and duplicate exclusions are explicit. Monetary is gross positive purchase value and may include charges; source is a mixture of retail and wholesale customers. Customers without identified purchases are unrepresented.

## Method

Manual tied-score quintile RFM tiers precede K-Means. Model inputs only Recency, Frequency and Monetary. Log1p, StandardScaler, KMeans n_init=20, seed=42. No main-model winsorization. k=3 selected by maximum distance below normalized endpoint chord for k=1…10, with range 1…8 sensitivity also k=3. Original-unit medians determine business names. Baseline overlays preserve at-risk/newly observed exceptions for campaign activation.

## Diagnostics

Chosen-k sampled silhouette 0.3403, sample up to 2,000 seed-42 customers. Higher silhouette at k=2 is disclosed. Minimum ARI across alternate seeds 0.9840; 99th-percentile-capped alternative ARI 0.9172. These are internal geometry/optimization/outlier diagnostics, not accuracy, temporal validity or business impact. All eligible customers participate in the descriptive fit; no artificial supervised holdout claim.

## Limits And Controls

Historical seasonality, the reference date, tie-heavy invoice counts, uncertain duplicate identity and exclusions influence profiles. K-Means prefers roughly compact groups; mathematical clusters are not customer identities. Public pseudonymous IDs do not provide contact eligibility. Behavioral profiles are descriptive, not demographic inference. No email campaigns, production identity integration, access-control layer or causal claims are provided.

Frozen assignment validates required columns, unique IDs, finite nonnegative RFM and positive integer invoice counts/Monetary. Optional first-observed age must be at least Recency. Without it no baseline newly observed tier is assigned. Distance-to-center is not probability. Input window, currency and domain must match. Load only trusted serialized models.

## Monitoring And Validation Path

For operational use, confirm data lineage, return treatment, customer identity resolution, contact permissions and product taxonomy. Rebuild at a common recent cutoff and assess temporal membership/size/centroid drift. Compare alternative windows and features without presenting k as a fact. Randomize targeted versus control campaigns within segments, prespecify costs, horizon, sample size and minimum detectable effect, and measure incremental contribution with uncertainty and multiple-testing controls. Monitor fairness where authorized relevant attributes exist; do not fabricate missing household data.
