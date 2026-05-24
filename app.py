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
from utils import load_css, sync_theme_switches

try:
    from components import render_active_filter_banner
except ImportError:
    def render_active_filter_banner():
        filter_labels = {
            "chart_lga_filter": "LGA",
            "chart_offence_filter": "Offence",
            "chart_year_filter": "Year",
            "chart_age_filter": "Age",
            "chart_sex_filter": "Sex",
        }
        active_parts = [
            f"{label}: **{st.session_state.get(key)}**"
            for key, label in filter_labels.items()
            if st.session_state.get(key)
        ]

        if not active_parts:
            return

        def clear_chart_filters():
            for key in filter_labels:
                st.session_state[key] = None
            st.session_state.chart_filter_version += 1
            st.rerun()

        col1, col2 = st.columns([1, 6])
        with col1:
            if st.button("Clear filters", key="clear_chart_filters_main", use_container_width=True, type="primary"):
                clear_chart_filters()
        with col2:
            st.info("Chart filter active - " + " | ".join(active_parts))


CHART_FILTER_DEFAULTS = {
    "chart_lga_filter": None,
    "chart_offence_filter": None,
    "chart_year_filter": None,
    "chart_age_filter": None,
    "chart_sex_filter": None,
}


def configure_page():
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    load_css(STYLES_CSS)
    sync_theme_switches()


def init_session_state():
    """Initialise chart-driven filter keys if they don't exist yet."""
    for key, default in CHART_FILTER_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default
    if "chart_filter_version" not in st.session_state:
        st.session_state.chart_filter_version = 0


def chart_key(name):
    return f"{name}_{st.session_state.chart_filter_version}"


def custom_value(point, index):
    customdata = point.get("customdata")
    if isinstance(customdata, (list, tuple)) and len(customdata) > index:
        return customdata[index]
    if index == 0:
        return customdata
    return None


def first_selected_point(event):
    if not event or not getattr(event, "selection", None):
        return None
    points = event.selection.get("points", [])
    return points[0] if points else None


def update_chart_filters(updates):
    changed = False
    for key, value in updates.items():
        if value is not None and st.session_state.get(key) != value:
            st.session_state[key] = value
            changed = True

    if changed:
        st.session_state.chart_filter_version += 1
        st.rerun()


def toggle_chart_filter(key, value):
    st.session_state[key] = None if st.session_state.get(key) == value else value
    st.session_state.chart_filter_version += 1
    st.rerun()


def handle_chart_selection(event, updates_from_point):
    point = first_selected_point(event)
    if point:
        update_chart_filters(updates_from_point(point))


def apply_chart_filters(filters, options):
    """
    Merge chart click state into the sidebar filters dict.
    Chart clicks narrow the sidebar selection rather than replace it,
    so behaviour is consistent with the existing filter logic.
    """
    filters["lgas"] = options["lgas"]

    if st.session_state.chart_year_filter:
        try:
            clicked = int(st.session_state.chart_year_filter)
        except (TypeError, ValueError):
            clicked = None
        if clicked is not None and clicked in options["years"]:
            filters["year_range"] = (clicked, clicked)

    if st.session_state.chart_lga_filter:
        clicked = st.session_state.chart_lga_filter
        if clicked in options["lgas"]:
            filters["lgas"] = [clicked]

    if st.session_state.chart_offence_filter:
        clicked = st.session_state.chart_offence_filter
        # Only apply if the clicked group is currently in scope
        if clicked in filters["offences"]:
            filters["offences"] = [clicked]

    if st.session_state.chart_age_filter:
        clicked = st.session_state.chart_age_filter
        if clicked in filters["age_groups"]:
            filters["age_groups"] = [clicked]

    if st.session_state.chart_sex_filter:
        clicked = st.session_state.chart_sex_filter
        if clicked in filters["sexes"]:
            filters["sexes"] = [clicked]

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
    section_header("Where — Geographic Crime Distribution")
    fig_map = build_map(scope, filters["map_mode"], filters["top_n"])
    fig_donut = build_donut(kpis["top_cat_df"], kpis["total"])

    c1, c2 = st.columns([3, 2])
    with c1:
        map_event = st.plotly_chart(
            fig_map,
            use_container_width=True,
            on_select="rerun",
            selection_mode="points",
            key=chart_key("map_chart"),
        )
        handle_chart_selection(
            map_event,
            lambda point: {"chart_lga_filter": custom_value(point, 0) or point.get("hovertext")},
        )
    with c2:
        donut_event = st.plotly_chart(
            fig_donut,
            use_container_width=True,
            on_select="rerun",
            selection_mode="points",
            key=chart_key("donut_chart"),
        )
        handle_chart_selection(
            donut_event,
            lambda point: {"chart_offence_filter": custom_value(point, 0) or point.get("label")},
        )
        
        # Clickable offence filter buttons below the donut
        st.markdown("**Filter by offence group:**")
        offence_options = kpis["top_cat_df"]["offence_group"].tolist()
        
        cols = st.columns(2)
        for i, offence in enumerate(offence_options):
            is_active = st.session_state.chart_offence_filter == offence
            label = f"✓ {offence}" if is_active else offence
            if cols[i % 2].button(label, key=f"btn_{offence}", use_container_width=True):
                toggle_chart_filter("chart_offence_filter", offence)

    # --- WHAT ---
    section_header("What — Trend & Concentration")
    fig_trend = build_trend(scope)
    fig_topn = build_top_lgas(kpis["top_lga_df"], filters["top_n"])

    c3, c4 = st.columns(2)
    with c3:
        trend_event = st.plotly_chart(
            fig_trend,
            use_container_width=True,
            on_select="rerun",
            selection_mode="points",
            key=chart_key("trend_chart"),
        )
        handle_chart_selection(
            trend_event,
            lambda point: {
                "chart_year_filter": custom_value(point, 0) or point.get("x"),
                "chart_offence_filter": custom_value(point, 1)
                or point.get("legendgroup")
                or point.get("fullData", {}).get("name"),
            },
        )
    with c4:
        topn_event = st.plotly_chart(
            fig_topn,
            use_container_width=True,
            on_select="rerun",
            selection_mode="points",
            key=chart_key("topn_chart"),
        )
        handle_chart_selection(
            topn_event,
            lambda point: {"chart_lga_filter": custom_value(point, 0) or point.get("y") or point.get("label")},
        )

    # --- WHO ---
    section_header("Who — Demographic Breakdown")
    fig_age = build_age_chart(scope)
    fig_sex = build_sex_chart(scope)

    c5, c6 = st.columns(2)
    with c5:
        age_event = st.plotly_chart(
            fig_age,
            use_container_width=True,
            on_select="rerun",
            selection_mode="points",
            key=chart_key("age_chart"),
        )
        handle_chart_selection(
            age_event,
            lambda point: {
                "chart_year_filter": custom_value(point, 0) or point.get("x"),
                "chart_age_filter": custom_value(point, 1)
                or point.get("legendgroup")
                or point.get("fullData", {}).get("name"),
            },
        )
    with c6:
        sex_event = st.plotly_chart(
            fig_sex,
            use_container_width=True,
            on_select="rerun",
            selection_mode="points",
            key=chart_key("sex_chart"),
        )
        handle_chart_selection(
            sex_event,
            lambda point: {
                "chart_offence_filter": custom_value(point, 0) or point.get("y"),
                "chart_sex_filter": custom_value(point, 1)
                or point.get("legendgroup")
                or point.get("fullData", {}).get("name"),
            },
        )

    st.markdown("---")

    # --- DRILL-DOWN ---
    section_header("Drill-Down — Inspect Any LGA")

    drill_lgas = sorted(scope["lga_name_clean"].dropna().unique().tolist())

    # If a chart click set a specific LGA, use it as the default.
    if st.session_state.chart_lga_filter and st.session_state.chart_lga_filter in drill_lgas:
        default_idx = drill_lgas.index(st.session_state.chart_lga_filter)
    elif kpis["top_lga"] in drill_lgas:
        default_idx = drill_lgas.index(kpis["top_lga"])
    else:
        default_idx = 0

    sel_lga = st.selectbox("Select an LGA to investigate", drill_lgas, index=default_idx)

    lga_stats = get_lga_stats(scope, sel_lga, kpis["total"])
    render_lga_insight(sel_lga, lga_stats, kpis)

    detail_mix = get_lga_detail_mix(detail_full, summary_full, sel_lga, filters)
    fig_lga_trend = build_lga_trend(lga_stats["lga_df"], sel_lga)
    fig_detail = build_detail_chart(detail_mix, sel_lga)

    d1, d2 = st.columns(2)
    with d1:
        lga_trend_event = st.plotly_chart(
            fig_lga_trend,
            use_container_width=True,
            on_select="rerun",
            selection_mode="points",
            key=chart_key("lga_trend_chart"),
        )
        handle_chart_selection(
            lga_trend_event,
            lambda point: {
                "chart_year_filter": custom_value(point, 0) or point.get("x"),
                "chart_offence_filter": custom_value(point, 1)
                or point.get("legendgroup")
                or point.get("fullData", {}).get("name"),
            },
        )
    with d2:
        st.plotly_chart(fig_detail, use_container_width=True)

    st.markdown("---")

    # --- WHAT NEXT ---
    section_header("What Next — Model an Intervention")
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
