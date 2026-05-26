import pandas as pd

QLD_PATH    = '/Users/miladkianfar/Projects/Third Semester/Data Visualisation/Assignment3/QLD/qld_summary_long.csv'
COORDS_PATH = '/Users/miladkianfar/Projects/Third Semester/Data Visualisation/Assignment3/LGA/lga_centroids_qld_sa.csv'
OUT_PATH    = '/Users/miladkianfar/Projects/Third Semester/Data Visualisation/Assignment3/QLD/qld_summary_long.csv'

df     = pd.read_csv(QLD_PATH)
coords = pd.read_csv(COORDS_PATH)
coords_qld = coords[coords['STE_NAME21'] == 'Queensland'][['lga_name_clean','lat','lon']].copy()

# Manual coordinates for 4 unmatched LGAs
MANUAL_COORDS = pd.DataFrame([
    {'lga_name_clean': 'Central Highlands', 'lat': -23.5281,  'lon': 147.9617},  # Emerald centroid
    {'lga_name_clean': 'Flinders',          'lat': -20.8428,  'lon': 144.2006},  # Wikipedia coords
    {'lga_name_clean': 'McKinlay',          'lat': -20.6567,  'lon': 141.7456},  # Wikipedia coords
    {'lga_name_clean': 'Weipa (T)',         'lat': -12.6367,  'lon': 141.8756},  # Weipa town
])

coords_qld = pd.concat([coords_qld, MANUAL_COORDS], ignore_index=True)

# Clean LGA name
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
    name = name.replace('Blackall-Tambo', 'Blackall Tambo')
    name = name.replace('Mckinlay', 'McKinlay')
    return name

df['lga_name_clean'] = df['lga_name'].apply(clean_lga)

# Drop old lat/lon if exists
for col in ['lat','lon']:
    if col in df.columns:
        df = df.drop(columns=[col])

# Merge
df = df.merge(coords_qld, on='lga_name_clean', how='left')

# QA
matched   = df[df['lat'].notna()]['lga_name_clean'].nunique()
unmatched = sorted(df[df['lat'].isna()]['lga_name_clean'].unique())
print(f"✅ Matched: {matched} / {df['lga_name_clean'].nunique()} LGAs")
print(f"❌ Unmatched ({len(unmatched)}): {unmatched}")

df.to_csv(OUT_PATH, index=False)
print(f"\n✅ Saved: {len(df):,} rows")
print(f"Columns: {df.columns.tolist()}")
