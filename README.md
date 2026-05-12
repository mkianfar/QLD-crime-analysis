# Queensland Crime Intelligence Dashboard

An interactive Streamlit dashboard designed for the **Queensland Community Safety Planning Team** to identify which Local Government Areas (LGAs) should be prioritised for targeted intervention and which offence patterns are driving that burden.

> **Decision question:** Which Queensland LGAs carry the highest and most persistent offence burden, and what interventions should planners prioritise first?

---

## Stakeholder and User Story

**Stakeholder:** Queensland Community Safety Planning Team

**User story:**  
As a community safety planner, I want to identify which LGAs have the highest and most persistent offence burden, so that limited intervention resources can be directed where they will have the greatest impact.

---

## Narrative Logic

This dashboard follows a **What -> So What -> What Next** structure:

- **What:** Show where offence burden is concentrated across Queensland LGAs
- **So What:** Reveal which offence categories and demographic patterns are driving that burden
- **What Next:** Support prioritisation through ranking, drill-down, and intervention scenario modelling

---

## Features

### Core Views

- Geographic offence concentration map across Queensland LGAs
- Offence group mix donut chart
- Annual offence trend by category
- Top-N LGA ranking bar chart
- Demographic trend breakdowns by age group and sex
- Local LGA drill-down for offence drivers and trend detail

### Advanced Features

1. **Context-aware filtering**  
   Sidebar filters for year, offence group, age group, and sex update KPIs and visuals dynamically, allowing users to move from statewide patterns to targeted subgroup analysis.

2. **LGA drill-down interaction**  
   Users can select an LGA to reveal its local offence trend and detailed offence-type breakdown, supporting place-based investigation.

3. **What-if intervention scenario**  
   A slider models a configurable percentage reduction in the top-priority LGA and updates the projected total burden in real time, helping planners test intervention impact.

---

## Dashboard Preview

_Add dashboard screenshots here once final layouts are exported._

---

## Data

| Item | Detail |
|---|---|
| Source | Queensland Police Service — LGA Reported Offenders (Monthly) |
| Period | 2001-2025 (filtered to <= 2025 in `constants.py`) |
| Spatial coverage | 77 Queensland LGAs |
| Unit of analysis | LGA x offence group x year x month x age group x sex |
| Key offence groups | Offences Against the Person, Property, Drug, Traffic, Domestic Violence Order Breaches, Good Order |
| Enrichment | Demographic splits by age group and sex |

The dashboard expects these files to be in the same folder as `app.py`:

- `qld_summary_long.csv`
- `qld_detail.csv`

---

## Project Structure

```bash
Streamlit/
├── app.py               # Page flow and section orchestration
├── data.py              # Loading, cleaning, filtering, KPI calculations
├── charts.py            # Plotly figure builders
├── components.py        # Sidebar, KPI cards, hero banner, reusable UI blocks
├── constants.py         # File paths, labels, palette, global settings
├── utils.py             # Shared helper functions
├── styles.css           # Custom CSS (dark theme)
├── requirements.txt     # Streamlit Cloud and local Python dependencies
├── qld_summary_long.csv # Summary: LGA x offence group x year x demographics
└── qld_detail.csv       # Detailed offence-type counts per LGA
```

---

## How to Run Locally

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

---

## Dependencies

The app uses:

- Streamlit
- pandas
- Plotly

Install them if needed:

```bash
pip install -r requirements.txt
```

---

## Deployment

The repository includes `requirements.txt`, so Streamlit Cloud can install the required packages automatically. When deploying, use:

- **Repository:** `mkianfar/QLD-crime-analysis`
- **Branch:** `main`
- **Main file path:** `app.py`

---

## Architecture

The app has been split so each file has a clear responsibility:

- `app.py` coordinates the dashboard flow.
- `data.py` owns data preparation and calculations.
- `charts.py` owns all Plotly figure creation.
- `components.py` owns Streamlit UI sections and reusable HTML blocks.
- `constants.py` stores shared settings, file paths, colour palettes, and offence ordering.
- `styles.css` keeps visual styling out of Python.

This keeps the main app easier to read and makes future edits safer, especially when changing chart logic, styling, or data processing separately.
