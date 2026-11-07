# Publish Project 2 on GitHub

Suggested repository: `rfm-behavioral-customer-segmentation`  
Description: “Manual RFM scoring and K-Means customer segmentation with elbow analysis, named audiences, behavioral profiles and an actionable campaign playbook.”  
Topics: python, customer-segmentation, rfm-analysis, kmeans, unsupervised-learning, marketing-analytics, streamlit, portfolio-project.

## Upload the whole project

Create an empty public repository. Extract the ZIP and upload the **contents of `rfm-customer-segmentation` at repository root**, including `.github`, `.streamlit`, `.gitignore`, compressed data, outputs and executed notebook. Do not upload only the ZIP or nest the project one level below the repository root. Do not upload `.venv312`.

```bash
git init -b main
git add .
git commit -m "Add RFM and behavioral customer segmentation portfolio"
# Replace YOUR_USERNAME:
git remote add origin https://github.com/YOUR_USERNAME/rfm-behavioral-customer-segmentation.git
git push -u origin main
```

For an existing repository, use its normal commit workflow rather than reinitializing it. No external repository has been created or pushed by this deliverable.

## Recruiter walkthrough

1. Start with the business question and the three named profiles in README.
2. Inspect the manual RFM baseline, then the elbow evidence; explain why a higher k=2 silhouette does not uniquely determine the business segmentation.
3. Open the executed notebook, source comments and cleaning audit.
4. Run the dashboard, filter audiences and export a segment-specific campaign hypothesis.
5. Explain the at-risk/newly observed RFM overlays and how a randomized pilot would test conversion and contribution.

GitHub renders the README, PNG and saved notebook. The Streamlit server runs separately; it is not deployed by uploading the repository. The HTML overview is for local viewing. Do not claim a live demo or passing CI badge before it exists.

Push/PR workflow runs tests and example assignment. Manual reproduction workflow refits from bundled data and uploads outputs. Workflows are supplied but have not been executed remotely here. Keep data attribution and license with the source/derived files.
