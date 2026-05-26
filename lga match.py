import pandas as pd
import os

# ==========================================================
# PATHS
# ==========================================================
QLD_PATH    = '/Users/miladkianfar/Projects/Third Semester/Data Visualisation/Assignment3/QLD/qld_summary_long.csv'
COORDS_PATH = '/Users/miladkianfar/Projects/Third Semester/Data Visualisation/Assignment3/LGA/lga_centroids_qld_sa.csv'
OUT_PATH    = '/Users/miladkianfar/Projects/Third Semester/Data Visualisation/Assignment3/QLD/qld_summary_long.csv'

# ==========================================================
# STEP 1 — Load files
# ==========================================================
df     = pd.read_csv(QLD_PATH)
coords = pd.read_csv(COORDS_PATH)
coords_qld = coords[coords['STE_NAME21'] == 'Queensland'][['lga_name_clean', 'lat', 'lon']].copy()

# ==========================================================
# STEP 2 — Clean LGA Name (strip suffixes)
# ==========================================================
SUFFIXES = [
    ' Aboriginal Shire Council',
    ' Shire Council',
    ' Regional Council',
    ' City Council',
    ' Town Council',
    ' Indigenous Council',
    ' Borough Council',
    ' Council',
]

def clean_lga(name: str) -> str:
    name = str(name).strip().title()
    for s in SUFFIXES:
        if name.endswith(s):
            name = name[:-len(s)].strip()
            break
    # Manual edge cases
    name = name.replace('Blackall-Tambo', 'Blackall Tambo')
    name = name.replace('Mckinlay',       'McKinlay')
    name = name.replace('Mornington Island Shire', 'Mornington Island')
    return name

df['lga_name_clean'] = df['lga_name'].apply(clean_lga)

# ==========================================================
# STEP 3 — Merge lat/lon
# ==========================================================
df = df.merge(coords_qld, on='lga_name_clean', how='left')

# ==========================================================
# STEP 4 — QA Report
# ==========================================================
total      = df['lga_name_clean'].nunique()
matched    = df[df['lat'].notna()]['lga_name_clean'].nunique()
unmatched  = sorted(df[df['lat'].isna()]['lga_name_clean'].unique())

print(f"✅ Matched:   {matched} / {total} LGAs")
print(f"❌ Unmatched: {len(unmatched)}")
if unmatched:
    print("   Unmatched names:")
    for u in unmatched:
        print(f"     '{u}'")

# ==========================================================
# STEP 5 — Save
# ==========================================================
df.to_csv(OUT_PATH, index=False)
print(f"\n✅ Saved → {OUT_PATH}")
print(f"   Columns: {df.columns.tolist()}")
print(f"   Rows: {len(df):,}")