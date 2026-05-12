import streamlit as st

from charts import (
    build_age_chart,
    build_detail_chart,
    build_donut,
    build_lga_trend,
    build_map,
    build_sex_chart,
    build_top_lgas,
    build_trend,
    build_whatif,
)
from components import (
    render_footer,
    render_hero,
    render_kpi_row,
    render_lga_insight,
    render_narrative_cards,
    render_recommendation,
    render_sidebar,
    section_header,
)
from constants import PAGE_ICON, PAGE_TITLE, STYLES_CSS
from data import (
    calculate_kpis,
    filter_summary,
    get_filter_options,
    get_lga_detail_mix,
    get_lga_stats,
    load_data,
)
from utils import load_css


def configure_page():
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    load_css(STYLES_CSS)


def render_dashboard(summary_full, detail_full):
    options = get_filter_options(summary_full)
    filters = render_sidebar(options)

    scope = filter_summary(summary_full, filters)
    if scope.empty:
        st.warning("⚠️ No data for selected filters.")
        st.stop()

    kpis = calculate_kpis(scope, filters["reduction_pct"])

    render_hero(kpis, filters)
    render_kpi_row(kpis)
    st.markdown("---")

    section_header("📍 Where — Geographic Crime Distribution")
    fig_map = build_map(scope, filters["map_mode"], filters["top_n"])
    fig_donut = build_donut(kpis["top_cat_df"], kpis["total"])
    c1, c2 = st.columns([3, 2])
    with c1:
        st.plotly_chart(fig_map, use_container_width=True)
    with c2:
        st.plotly_chart(fig_donut, use_container_width=True)

    section_header("📈 What — Trend & Concentration")
    fig_trend = build_trend(scope)
    fig_topn = build_top_lgas(kpis["top_lga_df"], filters["top_n"])
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(fig_trend, use_container_width=True)
    with c4:
        st.plotly_chart(fig_topn, use_container_width=True)

    section_header("👥 Who — Demographic Breakdown")
    fig_age = build_age_chart(scope)
    fig_sex = build_sex_chart(scope)
    c5, c6 = st.columns(2)
    with c5:
        st.plotly_chart(fig_age, use_container_width=True)
    with c6:
        st.plotly_chart(fig_sex, use_container_width=True)

    st.markdown("---")
    section_header("🔍 Drill-Down — Inspect Any LGA")
    default_idx = options["lgas"].index(kpis["top_lga"]) if kpis["top_lga"] in options["lgas"] else 0
    sel_lga = st.selectbox("Select an LGA to investigate", options["lgas"], index=default_idx)

    lga_stats = get_lga_stats(scope, sel_lga, kpis["total"])
    render_lga_insight(sel_lga, lga_stats, kpis)

    detail_mix = get_lga_detail_mix(detail_full, summary_full, sel_lga, filters)
    fig_lga_trend = build_lga_trend(lga_stats["lga_df"], sel_lga)
    fig_detail = build_detail_chart(detail_mix, sel_lga)
    d1, d2 = st.columns(2)
    with d1:
        st.plotly_chart(fig_lga_trend, use_container_width=True)
    with d2:
        st.plotly_chart(fig_detail, use_container_width=True)

    st.markdown("---")
    section_header("🧮 What Next — Model an Intervention")
    fig_wi = build_whatif(
        kpis["total"],
        kpis["projected_total"],
        filters["reduction_pct"],
        kpis["top_lga"],
    )
    w1, w2, w3, w4 = st.columns([2, 1, 1, 1])
    with w1:
        st.plotly_chart(fig_wi, use_container_width=True)
    render_narrative_cards((w2, w3, w4), kpis, filters)

    render_recommendation(kpis, filters)
    render_footer(scope)


def main():
    configure_page()
    summary_full, detail_full = load_data()
    render_dashboard(summary_full, detail_full)


if __name__ == "__main__":
    main()
