# Queensland Crime Intelligence Dashboard

An interactive Streamlit dashboard for exploring reported offender patterns across Queensland Local Government Areas (LGAs). The dashboard supports filtering by year range, offence group, age group, sex, map display mode, and a simple intervention what-if scenario.

## Features

- Geographic offence concentration map
- Offence group mix donut chart
- Annual offence trend by category
- Top-N LGA comparison
- Adult vs juvenile trend
- Sex and offence group breakdown
- LGA drill-down with detailed offence drivers
- Intervention scenario showing projected offence reduction

## Project Structure

```text
Streamlit/
  app.py                 # Main Streamlit entry point and page flow
  data.py                # Data loading, cleaning, filtering, and KPI logic
  charts.py              # Plotly chart builders
  components.py          # Sidebar, cards, hero, footer, and HTML UI components
  constants.py           # File paths, colours, labels, and shared constants
  utils.py               # Small shared helpers
  styles.css             # Custom dashboard CSS
  qld_summary_long.csv   # Summary-level offence data
  qld_detail.csv         # Detailed offence data
```

## How to Run

From this folder, run:

```bash
streamlit run app.py
```

If you are using the Anaconda installation on this machine, this also works:

```bash
/opt/anaconda3/bin/streamlit run app.py
```

Then open the local URL shown by Streamlit, usually:

```text
http://localhost:8501
```

## Dependencies

The app uses:

- Streamlit
- pandas
- Plotly

Install them if needed:

```bash
pip install streamlit pandas plotly
```

## Data Notes

The dashboard expects these files to be in the same folder as `app.py`:

- `qld_summary_long.csv`
- `qld_detail.csv`

The app filters records to years up to and including 2025. This limit is defined in `constants.py`.

## Architecture

The app has been split so each file has a clear responsibility:

- `app.py` coordinates the dashboard flow.
- `data.py` owns data preparation and calculations.
- `charts.py` owns all Plotly figure creation.
- `components.py` owns Streamlit UI sections and reusable HTML blocks.
- `styles.css` keeps visual styling out of Python.

This keeps the main app easier to read and makes future edits safer, especially when changing chart logic, styling, or data processing separately.
