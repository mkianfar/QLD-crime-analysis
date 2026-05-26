import pandas as pd

INPUT_FILE = "/Users/miladkianfar/Projects/Third Semester/Data Visualisation/Assignment3/QLD/LGA_Reported_Offenders_Number.csv"

OUTPUT_SUMMARY_WIDE = "/Users/miladkianfar/Projects/Third Semester/Data Visualisation/Assignment3/QLD/qld_summary.csv"
OUTPUT_SUMMARY_LONG = "/Users/miladkianfar/Projects/Third Semester/Data Visualisation/Assignment3/QLD/qld_summary_long.csv"
OUTPUT_DETAIL = "/Users/miladkianfar/Projects/Third Semester/Data Visualisation/Assignment3/QLD/qld_detail.csv"

# ==========================================
# STEP 1 — READ RAW FILE CORRECTLY
# ==========================================
df = pd.read_csv(INPUT_FILE, index_col=False)
df.columns = df.columns.str.strip()

# drop unnamed last column if exists
unnamed_cols = [c for c in df.columns if str(c).startswith("Unnamed")]
df = df.drop(columns=unnamed_cols, errors="ignore")

print("========== CHECK RAW ==========")
print(df.head(5).to_string())
print("\nColumns:")
print(df.columns.tolist())

# hard validation
if "Month Year" not in df.columns:
    raise ValueError("Column 'Month Year' not found.")

sample_vals = df["Month Year"].astype(str).head(10).tolist()
print("\nSample Month Year values:")
print(sample_vals)

# if still wrong, stop immediately
if not any(str(v).strip().upper().startswith(("JAN", "FEB", "MAR", "APR", "MAY", "JUN",
                                              "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"))
           for v in sample_vals):
    raise ValueError(
        "Month Year column is still wrong. You are likely running the wrong script or the file is being read incorrectly."
    )

# ==========================================
# STEP 2 — PARSE DATE
# ==========================================
def parse_month_year(val):
    try:
        return pd.to_datetime(str(val).strip().title(), format="%b%y")
    except:
        return pd.NaT

df["date"] = df["Month Year"].apply(parse_month_year)

print("\nBad dates count:", df["date"].isna().sum())

if df["date"].isna().all():
    raise ValueError("All dates failed to parse. Stop here and inspect the raw file again.")

df["year"] = df["date"].dt.year
df["month_num"] = df["date"].dt.month
df["month_name"] = df["date"].dt.strftime("%B")
df["month_label"] = df["date"].dt.strftime("%b %Y")

# ==========================================
# STEP 3 — STANDARDISE TEXT
# ==========================================
df["LGA Name"] = df["LGA Name"].astype(str).str.strip().str.title()
df["Age"] = df["Age"].astype(str).str.strip().str.title()
df["Sex"] = df["Sex"].astype(str).str.strip().str.title()

# ==========================================
# STEP 4 — DEFINE COLUMNS
# ==========================================
id_vars = ["LGA Name", "date", "year", "month_num", "month_name", "month_label", "Age", "Sex"]

summary_cols = [
    "Offences Against the Person",
    "Offences Against Property",
    "Drug Offences",
    "Traffic and Related Offences",
    "Breach Domestic Violence Protection Order",
    "Good Order Offences",
    "Miscellaneous Offences",
    "Other Offences"
]

detail_cols = [
    "Assault",
    "Grievous Assault",
    "Serious Assault",
    "Sexual Offences",
    "Robbery",
    "Armed Robbery",
    "Unlawful Entry",
    "Other Property Damage",
    "Fraud",
    "Breach Domestic Violence Protection Order",
    "Drink Driving"
]

summary_cols = [c for c in summary_cols if c in df.columns]
detail_cols = [c for c in detail_cols if c in df.columns]

# numeric conversion
for col in sorted(set(summary_cols + detail_cols)):
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

# keep 2010 onwards
df = df[df["year"] >= 2010].copy()

# rename clean columns
df = df.rename(columns={
    "LGA Name": "lga_name",
    "Age": "age_group",
    "Sex": "sex"
})

id_vars_clean = ["lga_name", "date", "year", "month_num", "month_name", "month_label", "age_group", "sex"]

# ==========================================
# STEP 5 — SUMMARY WIDE
# ==========================================
df_summary = df[id_vars_clean + summary_cols].copy()
df_summary = df_summary[df_summary[summary_cols].sum(axis=1) > 0].copy()
df_summary.to_csv(OUTPUT_SUMMARY_WIDE, index=False)

# ==========================================
# STEP 6 — SUMMARY LONG
# ==========================================
df_summary_long = df_summary.melt(
    id_vars=id_vars_clean,
    value_vars=summary_cols,
    var_name="offence_group",
    value_name="offence_count"
)
df_summary_long = df_summary_long[df_summary_long["offence_count"] > 0].copy()
df_summary_long.to_csv(OUTPUT_SUMMARY_LONG, index=False)

# ==========================================
# STEP 7 — DETAIL
# ==========================================
df_detail = df[id_vars_clean + detail_cols].copy()
df_detail = df_detail[df_detail[detail_cols].sum(axis=1) > 0].copy()
df_detail.to_csv(OUTPUT_DETAIL, index=False)

# ==========================================
# STEP 8 — VALIDATION
# ==========================================
print("\n========== DONE ==========")
print("qld_summary rows:", len(df_summary))
print("qld_summary_long rows:", len(df_summary_long))
print("qld_detail rows:", len(df_detail))
print("Date range:", df["date"].min(), "→", df["date"].max())

for check_col in ["Other Offences", "Miscellaneous Offences", "Offences Against Property", "Offences Against the Person"]:
    if check_col in df.columns:
        print(f"\n{check_col} top values:")
        print(df[check_col].sort_values(ascending=False).head(10).tolist())