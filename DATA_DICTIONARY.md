# Data dictionary and provenance

Source: Chen, D. (2015). Online Retail [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33 . Dataset 352, CC BY 4.0. The original workbook is converted to compressed CSV without filtering. Source and converted hashes are in `data/source.json`.

## Transaction columns

| Field | Meaning |
|---|---|
| InvoiceNo | Invoice identifier; C-prefixed invoices indicate cancellations |
| StockCode | Product/item code; includes some non-merchandise/administrative codes |
| Description | Product description; missing values preserved in raw conversion |
| Quantity | Units per line; nonpositive lines excluded from purchase model |
| InvoiceDate | Recorded purchase timestamp; no timezone inferred |
| UnitPrice | Unit price in pounds sterling; nonpositive values excluded |
| CustomerID | Source pseudonymous customer ID; missing IDs are not imputed |
| Country | Recorded country, not demographic or household information |
| LineRevenue | Derived Quantity × UnitPrice for eligible lines |

## Customer outputs

| Field | Meaning |
|---|---|
| Recency | Calendar days since last eligible purchase at the reference date |
| Frequency | Distinct invoices in the 365-day observation window |
| Monetary | Sum of positive purchase line values, GBP; not net of returns |
| R_score/F_score/M_score | Quintile-cutoff 1–5 scores; Recency reversed; ties preserved |
| RFM_code | String combining R, F and M scores |
| baseline_tier | Ordered manual RFM business tier |
| cluster_id | Internal K-Means identifier, no ordinal business meaning |
| segment | Plain-English cluster profile name |
| recommended_campaign | Cluster campaign hypothesis plus at-risk/newly observed baseline overlays |
| first_purchase/last_purchase | First/last eligible purchase timestamp inside the window |
| first_observed_age_days | Days since first eligible purchase in the window, not lifetime tenure |
| average_order_value | Monetary / Frequency, GBP |
| total_units/units_per_order | Positive purchased units and units per distinct invoice |
| unique_products | Distinct StockCode count, including unfiltered administrative codes |
| repeat_buyer | Frequency > 1 |
| country | Modal country by eligible line count, lexical tie-break |
| top_product_code | Highest total positive-unit SKU, lexical tie-break |
| distance_to_center | Frozen-assignment Euclidean distance in standardized log-RFM; not confidence |

Profile files use original-unit medians/means. Purchase-value share is the segment's historical Monetary sum divided by the population sum. Behavioral fields describe clusters; they are not K-Means inputs. Household composition, browsing interests, campaign permissions, marketing outcomes and margins are absent.

Known modification: exact-duplicate/identity/cancellation/value/window exclusions as documented in the cleaning audit. Adapted customer exports are credited to the original dataset under CC BY 4.0. No assertion of source endorsement.
