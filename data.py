import pandas as pd
import streamlit as st

from constants import (
    DETAIL_CSV,
    DETAIL_OFFENCE_ORDER,
    GENERIC_OFFENCE_GROUPS,
    MAX_YEAR,
    SUMMARY_CSV,
)


@st.cache_data
def load_summary(path=SUMMARY_CSV):
    df = pd.read_csv(path, parse_dates=["date"])
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["offence_count"] = pd.to_numeric(df["offence_count"], errors="coerce").fillna(0).astype(int)

    for col in ["lga_name", "lga_name_clean", "age_group", "sex", "offence_group"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    if "lga_name_clean" not in df.columns:
        df["lga_name_clean"] = df["lga_name"]

    return df


@st.cache_data
def load_detail(path=DETAIL_CSV):
    id_cols = [
        "lga_name",
        "date",
        "year",
        "month_num",
        "month_name",
        "month_label",
        "age_group",
        "sex",
    ]
    df = pd.read_csv(path, parse_dates=["date"])
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

    for col in ["lga_name", "age_group", "sex"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    offence_cols = [c for c in df.columns if c not in id_cols]
    for col in offence_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    keep_id = [c for c in ["lga_name", "year", "age_group", "sex"] if c in df.columns]
    df_long = df[keep_id + offence_cols].melt(
        id_vars=keep_id,
        var_name="offence_type",
        value_name="count",
    )
    return df_long.groupby(keep_id + ["offence_type"], as_index=False)["count"].sum()


def load_data():
    summary_full = load_summary()
    detail_full = load_detail()

    summary_full = summary_full[summary_full["year"] <= MAX_YEAR].copy()
    detail_full = detail_full[detail_full["year"] <= MAX_YEAR].copy()
    return summary_full, detail_full


def get_filter_options(summary_full):
    return {
        "years": sorted(summary_full["year"].dropna().astype(int).unique().tolist()),
        "offences": sorted(summary_full["offence_group"].dropna().unique().tolist()),
        "lgas": sorted(summary_full["lga_name_clean"].dropna().unique().tolist()),
        "ages": sorted(summary_full["age_group"].dropna().unique().tolist()),
        "sexes": sorted(summary_full["sex"].dropna().unique().tolist()),
    }


def filter_summary(summary_full, filters):
    year_range = filters["year_range"]
    return summary_full[
        (summary_full["year"] >= year_range[0])
        & (summary_full["year"] <= year_range[1])
        & (summary_full["lga_name_clean"].isin(filters["lgas"]))
        & (summary_full["offence_group"].isin(filters["offences"]))
        & (summary_full["age_group"].isin(filters["age_groups"]))
        & (summary_full["sex"].isin(filters["sexes"]))
    ].copy()


def calculate_kpis(scope, reduction_pct):
    total = scope["offence_count"].sum()
    n_lgas = scope["lga_name_clean"].nunique()

    top_lga_df = (
        scope.groupby("lga_name_clean", as_index=False)["offence_count"]
        .sum()
        .sort_values("offence_count", ascending=False)
    )
    top_lga = top_lga_df.iloc[0]["lga_name_clean"]
    top_lga_cnt = top_lga_df.iloc[0]["offence_count"]
    top_lga_pct = top_lga_cnt / total * 100 if total else 0

    top_cat_df = (
        scope.groupby("offence_group", as_index=False)["offence_count"]
        .sum()
        .sort_values("offence_count", ascending=False)
    )
    meaningful = top_cat_df[~top_cat_df["offence_group"].isin(GENERIC_OFFENCE_GROUPS)]
    top_row = meaningful.iloc[0] if not meaningful.empty else top_cat_df.iloc[0]
    top_cat = top_row["offence_group"]
    top_cat_cnt = top_row["offence_count"]

    year_totals = scope.groupby("year", as_index=False)["offence_count"].sum().sort_values("year")
    trend_txt, trend_cls = "", "kpi-delta"
    if len(year_totals) >= 2:
        latest = year_totals.iloc[-1]["offence_count"]
        previous = year_totals.iloc[-2]["offence_count"]
        change = (latest - previous) / previous * 100 if previous else 0
        trend_txt = f"{'▲' if change > 0 else '▼'} {abs(change):.1f}% vs prior year"
        trend_cls = "delta-up" if change > 0 else "delta-down"

    juvenile_total = scope[scope["age_group"].str.lower() == "juvenile"]["offence_count"].sum()
    juv_pct = juvenile_total / total * 100 if total else 0
    projected_saving = top_lga_cnt * (reduction_pct / 100)
    projected_total = total - projected_saving

    return {
        "total": total,
        "n_lgas": n_lgas,
        "top_lga_df": top_lga_df,
        "top_lga": top_lga,
        "top_lga_cnt": top_lga_cnt,
        "top_lga_pct": top_lga_pct,
        "top_cat_df": top_cat_df,
        "top_cat": top_cat,
        "top_cat_cnt": top_cat_cnt,
        "trend_txt": trend_txt,
        "trend_cls": trend_cls,
        "juv_pct": juv_pct,
        "projected_saving": projected_saving,
        "projected_total": projected_total,
    }


def get_lga_stats(scope, sel_lga, total):
    lga_df = scope[scope["lga_name_clean"] == sel_lga].copy()
    lga_total = lga_df["offence_count"].sum()
    lga_share = lga_total / total * 100 if total else 0

    lga_group_totals = (
        lga_df.groupby("offence_group", as_index=False)["offence_count"]
        .sum()
        .sort_values("offence_count", ascending=False)
    )
    meaningful = lga_group_totals[~lga_group_totals["offence_group"].isin(GENERIC_OFFENCE_GROUPS)]
    top_row = meaningful.iloc[0] if not meaningful.empty else lga_group_totals.iloc[0]

    return {
        "lga_df": lga_df,
        "lga_total": lga_total,
        "lga_share": lga_share,
        "lga_top_cat": top_row["offence_group"],
        "lga_top_cnt": top_row["offence_count"],
    }


def get_clean_to_full_map(summary_full):
    clean_to_full = summary_full[["lga_name", "lga_name_clean"]].drop_duplicates()
    return dict(zip(clean_to_full["lga_name_clean"], clean_to_full["lga_name"]))


def get_lga_detail_mix(detail_full, summary_full, sel_lga, filters):
    year_range = filters["year_range"]
    clean_to_full = get_clean_to_full_map(summary_full)
    sel_lga_full = clean_to_full.get(sel_lga, sel_lga)

    detail_lga = detail_full[
        (detail_full["lga_name"].str.strip() == sel_lga_full.strip())
        & (detail_full["year"] >= year_range[0])
        & (detail_full["year"] <= year_range[1])
        & (detail_full["age_group"].isin(filters["age_groups"]))
        & (detail_full["sex"].isin(filters["sexes"]))
    ].groupby("offence_type", as_index=False)["count"].sum()

    return (
        detail_lga[
            detail_lga["offence_type"].isin(DETAIL_OFFENCE_ORDER)
            & (detail_lga["count"] > 0)
        ]
        .sort_values("count", ascending=True)
    )
