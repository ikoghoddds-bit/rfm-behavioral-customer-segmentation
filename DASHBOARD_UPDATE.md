# Apply The Dashboard Update

## Keep Your Existing Python Environment

1. Stop the running dashboard with Ctrl+C in PowerShell.
2. Extract the updated ZIP into a different folder.
3. Copy the contents of the new `rfm-customer-segmentation` folder into your existing project folder and allow replacement of project files. Keep `.venv312`; do not delete your existing folder. The archive does not contain a virtual environment.
4. From your existing project folder, launch:

```powershell
.\.venv312\Scripts\python.exe -m streamlit run app.py
```

5. Refresh the browser. Ctrl+0 restores 100% zoom if you want to inspect the normal layout after making zoomed-out screenshots.

No model retraining is needed. Altair is already installed as a Streamlit dependency; the requirements file now pins its tested version explicitly. If the environment reports an import/version problem, run:

```powershell
.\.venv312\Scripts\python.exe -m pip install -r requirements.txt
```

## Main Changes

- Main insight, historical snapshot badge and campaign cards lead the overview.
- All audience metrics, profiles, charts and exports follow the same filters.
- Full-population benchmarks and cluster evidence are labeled separately.
- Short filter names, a wider desktop sidebar and Select All / Clear / Reset controls.
- Horizontal count bars, customer/value share comparison and consistent segment colors.
- Readable table labels, GBP/percentage/day formats and definition tooltips.
- Log/linear scatter with customer tooltips and optional display-only 99% zoom.
- View Audience and direct export from each segment card.
- Title Case headings/subheadings throughout the dashboard and publication material.

## Update GitHub

Commit the updated app, source helpers, theme configuration, requirements, documentation, notebook and publication figure. Data schema, customer assignments and model outputs are unchanged. Do not commit `.venv312`.
