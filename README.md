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

This dashboard follows a **What → So What → What Next** structure:

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
| Primary source | Queensland Police Service - LGA Reported Offenders (Monthly) |
| Period | 2010–2025, filtered to ≤ 2025 in `constants.py` |
| Spatial coverage | 77 Queensland LGAs |
| Unit of analysis | LGA × offence group × year × month × age group × sex |
| Key offence groups | Offences Against the Person, Property, Drug, Traffic, Domestic Violence Order Breaches, Good Order |
| Enrichment | ABS geographic reference data used to map LGA names to latitude/longitude for spatial visualisation, plus demographic splits by age group and sex |

In addition to the Queensland Police Service offence dataset, the project uses **ABS geographic reference data** to map LGA names to latitude and longitude coordinates. This enrichment enables the dashboard’s spatial visualisation and map-based prioritisation layer.

The dashboard currently expects these files to be stored in the same directory as `app.py`:

- `qld_summary_long.csv`
- `qld_detail.csv`

---

## Data Dictionary

| Variable | Type | Description | Provenance |
|---|---|---|---|
| `lga_name` | Categorical | Queensland Local Government Area name | QPS / ABS mapping |
| `year` | Temporal | Reporting year | QPS |
| `month` | Temporal | Reporting month | QPS |
| `offence_group` | Categorical | High-level offence category | QPS |
| `age_group` | Categorical | Demographic age grouping | QPS |
| `sex` | Categorical | Sex classification | QPS |
| `count` | Numeric | Number of reported offenders / incidents | QPS |
| `latitude` | Numeric | Latitude used for map placement | ABS reference data |
| `longitude` | Numeric | Longitude used for map placement | ABS reference data |

---

## Project Structure

```bash
Streamlit/
├── app.py
├── data.py
├── charts.py
├── components.py
├── constants.py
├── utils.py
├── styles.css
├── requirements.txt
├── qld_summary_long.csv
└── qld_detail.csv
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

Install them with:

```bash
pip install -r requirements.txt
```

---

## Deployment

The repository includes `requirements.txt`, so Streamlit Cloud can install the required packages automatically.

Use the following deployment settings:

- **Repository:** `mkianfar/QLD-crime-analysis`
- **Branch:** `main`
- **Main file path:** `app.py`

---

## Live App

_Add published Streamlit Cloud link here._

---

## Architecture

The app has been split so each file has a clear responsibility:

- `app.py` coordinates the dashboard flow
- `data.py` handles data preparation, filtering, and KPI calculations
- `charts.py` contains all Plotly figure creation
- `components.py` contains Streamlit UI sections and reusable HTML blocks
- `constants.py` stores shared settings, file paths, colour palettes, and offence ordering
- `utils.py` provides shared helper functions
- `styles.css` keeps visual styling out of Python

This structure keeps the main app easier to read and makes future edits safer, especially when changing chart logic, styling, or data processing separately.

---

## Design Rationale

The dashboard was designed as a human-centred decision-support tool, not a passive reporting interface. The stakeholder requires rapid identification of high-burden LGAs, a clear understanding of dominant offence drivers, and enough demographic context to support targeted intervention design.

The visual structure therefore prioritises:

- clarity over clutter
- place-based prioritisation
- direct comparison across LGAs
- action-oriented interpretation

The dashboard moves from statewide burden to offence composition, then to demographic patterning and local drill-down, helping the stakeholder move from awareness to intervention planning.

---

## Intended Use

This dashboard is intended to support:

- identification of priority LGAs for community safety intervention
- comparison of offence burden across places
- interpretation of dominant offence categories
- demographic tailoring of intervention strategy
- scenario testing for burden reduction

It is not intended to replace detailed operational intelligence systems. Instead, it provides a stakeholder-facing narrative layer for prioritisation and planning.

---

## Credits

Developed as part of **36104 Data Visualisation and Narratives** at the University of Technology Sydney.
