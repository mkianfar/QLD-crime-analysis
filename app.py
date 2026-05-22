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

try:
    from components import render_active_filter_banner
except ImportError:
    def render_active_filter_banner():
        offence_filter = st.session_state.get("chart_offence_filter")
        lga_filter = st.session_state.get("chart_lga_filter")

        active_parts = []
        if offence_filter:
            active_parts.append(f"Offence: **{offence_filter}**")
        if lga_filter:
            active_parts.append(f"LGA drill-down: **{lga_filter}**")

        if not active_parts:
            return

        col1, col2 = st.columns([5, 1])
        with col1:
            st.info("🎯 Chart filter active - " + " | ".join(active_parts))
        with col2:
            if st.button("✕ Reset", use_container_width=True, type="secondary"):
                st.session_state.chart_offence_filter = None
                st.session_state.chart_lga_filter = None
                st.rerun()


def configure_page():
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    load_css(STYLES_CSS)


def init_session_state():
    """Initialise chart-driven filter keys if they don't exist yet."""
    if "chart_offence_filter" not in st.session_state:
        st.session_state.chart_offence_filter = None  # str or None
    if "chart_lga_filter" not in st.session_state:
        st.session_state.chart_lga_filter = None      # str or None


def apply_chart_filters(filters, options):
    """
    Merge chart click state into the sidebar filters dict.
    Chart clicks narrow the sidebar selection rather than replace it,
    so behaviour is consistent with the existing filter logic.
    """
    if st.session_state.chart_offence_filter:
        clicked = st.session_state.chart_offence_filter
        # Only apply if the clicked group is currently in scope
        if clicked in filters["offences"]:
            filters["offences"] = [clicked]

    return filters


def render_dashboard(summary_full, detail_full):
    options = get_filter_options(summary_full)
    filters = render_sidebar(options)

    # Merge any active chart-click filters
    filters = apply_chart_filters(filters, options)

    # Show banner + reset button when a chart filter is active
    render_active_filter_banner()

    scope = filter_summary(summary_full, filters)

    if scope.empty:
        st.warning("⚠️ No data for selected filters.")
        st.stop()

    kpis = calculate_kpis(scope, filters["reduction_pct"])

    render_hero(kpis, filters)
    render_kpi_row(kpis)

    st.markdown("---")

    # --- WHERE ---
    section_header("📍 Where — Geographic Crime Distribution")
    fig_map = build_map(scope, filters["map_mode"], filters["top_n"])
    fig_donut = build_donut(kpis["top_cat_df"], kpis["total"])

    c1, c2 = st.columns([3, 2])
    with c1:
        st.plotly_chart(fig_map, use_container_width=True)
    with c2:
        st.plotly_chart(fig_donut, use_container_width=True)
        
        # Clickable offence filter buttons below the donut
        st.markdown("**Filter by offence group:**")
        offence_options = kpis["top_cat_df"]["offence_group"].tolist()
        
        cols = st.columns(2)
        for i, offence in enumerate(offence_options):
            is_active = st.session_state.chart_offence_filter == offence
            label = f"✓ {offence}" if is_active else offence
            if cols[i % 2].button(label, key=f"btn_{offence}", use_container_width=True):
                if is_active:
                    st.session_state.chart_offence_filter = None
                else:
                    st.session_state.chart_offence_filter = offence
                st.rerun()

    # --- WHAT ---
    section_header("📈 What — Trend & Concentration")
    fig_trend = build_trend(scope)
    fig_topn = build_top_lgas(kpis["top_lga_df"], filters["top_n"])

    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(fig_trend, use_container_width=True)
    with c4:
        # Capture top-N bar click to jump the drill-down LGA
        topn_event = st.plotly_chart(
            fig_topn,
            use_container_width=True,
            on_select="rerun",
            key="topn_chart",
        )
        if topn_event and topn_event.selection and topn_event.selection.get("points"):
            clicked_lga = topn_event.selection["points"][0].get("label")
            if clicked_lga and clicked_lga != st.session_state.chart_lga_filter:
                st.session_state.chart_lga_filter = clicked_lga
                st.rerun()

    # --- WHO ---
    section_header("👥 Who — Demographic Breakdown")
    fig_age = build_age_chart(scope)
    fig_sex = build_sex_chart(scope)

    c5, c6 = st.columns(2)
    with c5:
        st.plotly_chart(fig_age, use_container_width=True)
    with c6:
        st.plotly_chart(fig_sex, use_container_width=True)

    st.markdown("---")

    # --- DRILL-DOWN ---
    section_header("🔍 Drill-Down — Inspect Any LGA")

    # If a bar chart click set a specific LGA, use it as the default
    if st.session_state.chart_lga_filter and st.session_state.chart_lga_filter in options["lgas"]:
        default_idx = options["lgas"].index(st.session_state.chart_lga_filter)
    elif kpis["top_lga"] in options["lgas"]:
        default_idx = options["lgas"].index(kpis["top_lga"])
    else:
        default_idx = 0

    sel_lga = st.selectbox("Select an LGA to investigate", options["lgas"], index=default_idx)

    # Keep session state in sync if user manually changes the selectbox
    if sel_lga != st.session_state.chart_lga_filter:
        st.session_state.chart_lga_filter = sel_lga

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

    # --- WHAT NEXT ---
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
    init_session_state()
    summary_full, detail_full = load_data()
    render_dashboard(summary_full, detail_full)


if __name__ == "__main__":
    main()
