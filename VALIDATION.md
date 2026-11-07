# Validation record

November 6, 2026 · Python 3.12 · Project 2

- Retrieved original UCI dataset 352 and converted all 541,909 workbook rows to gzip CSV without filtering. Workbook/serialized hashes and source citation recorded.
- Executed audited cleaning and the frozen 365-day window: 378,508 eligible lines, 4,264 customers and 17,756 customer-invoice orders.
- Verified explicit manual pandas RFM calculations against reusable feature functions before clustering.
- Executed all nine notebook code cells with captured outputs/figures. The build environment blocks kernel sockets, so execution used in-process IPython; the deliverable remains a standard Python 3 notebook.
- Evaluated k=1…10, reproducible normalized-chord elbow, sampled silhouettes, range sensitivity, five alternate initializations and an outlier-capping diagnostic.
- Six tests passed: cleaning/manual RFM arithmetic, tie-safe baseline/coverage, elbow definition, export reconciliation/model round-trip, schema validation, and dashboard default/empty-audience behavior.
- Batch assignment succeeded on the included RFM example.
- Evidence PNG visually inspected after wrapping labels; no clipped chart text remains. Dashboard checked with Streamlit AppTest; no new browser screenshot captured.
- Verified named profile counts, purchase-value shares, baseline tiers, campaign overlays and notebook outputs. No fabricated campaign outcomes or household attributes are included.
- Archive paths, CRC and required deliverables validated before saving.

GitHub workflows are prepared but have not run remotely. Windows batch launchers are provided with direct Python 3.12 environment commands; this Linux environment cannot execute Windows batch files. No external repository, hosted deployment or marketing campaign was created. Local and internal clustering checks do not establish future population stability, conversion uplift or production readiness.
