import streamlit as st

from utils import fmt


CHART_FILTER_LABELS = {
    "chart_lga_filter": "LGA",
    "chart_offence_filter": "Offence",
    "chart_year_filter": "Year",
    "chart_age_filter": "Age",
    "chart_sex_filter": "Sex",
}


def active_chart_filter_parts():
    return [
        f"{label}: **{st.session_state.get(key)}**"
        for key, label in CHART_FILTER_LABELS.items()
        if st.session_state.get(key)
    ]


def clear_chart_filters():
    for key in CHART_FILTER_LABELS:
        st.session_state[key] = None
    st.session_state.chart_filter_version += 1
    st.rerun()


def sidebar_label(text, spaced=False):
    class_name = "sidebar-section-label spaced" if spaced else "sidebar-section-label"
    st.sidebar.markdown(f'<p class="{class_name}">{text}</p>', unsafe_allow_html=True)


def render_sidebar(options):
    st.sidebar.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-mark">QLD</div>
            <div>
                <div class="sidebar-brand-title">Crime Intelligence</div>
                <div class="sidebar-brand-subtitle">Community safety planning</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if active_chart_filter_parts():
        st.sidebar.info("Chart filters active")
        if st.sidebar.button(
            "Clear chart filters",
            key="clear_chart_filters_sidebar",
            use_container_width=True,
            type="primary",
        ):
            clear_chart_filters()
        st.sidebar.markdown("---")

    sidebar_label("TIME RANGE")
    year_range = st.sidebar.slider(
        "Year range",
        min_value=min(options["years"]),
        max_value=max(options["years"]),
        value=(2018, 2025),
    )

    sidebar_label("OFFENCE TYPE", spaced=True)
    offences = st.sidebar.multiselect(
        "Offence groups",
        options["offences"],
        default=options["offences"],
    )

    sidebar_label("DEMOGRAPHICS", spaced=True)
    age_groups = st.sidebar.multiselect(
        "Age group",
        options["ages"],
        default=options["ages"],
    )
    sexes = st.sidebar.multiselect(
        "Sex",
        options["sexes"],
        default=options["sexes"],
    )

    sidebar_label("DISPLAY", spaced=True)
    top_n = st.sidebar.slider("Top N LGAs", 5, 20, 10)
    map_mode = st.sidebar.radio("Map display", ["Top N LGAs", "All LGAs"], index=0)

    st.sidebar.markdown("---")

    sidebar_label("WHAT-IF")
    reduction_pct = st.sidebar.slider(
        "Intervention reduction in top LGA",
        0,
        50,
        20,
        format="%d%%",
    )

    return {
        "year_range": year_range,
        "offences": offences,
        "age_groups": age_groups,
        "sexes": sexes,
        "top_n": top_n,
        "map_mode": map_mode,
        "reduction_pct": reduction_pct,
    }


def render_active_filter_banner():
    """
    Shows a dismissable banner when a chart click filter is active.
    Displays what is filtered and a reset button to clear it.
    """
    active_parts = active_chart_filter_parts()

    if not active_parts:
        return

    st.markdown('<div class="active-filter-offset"></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("Clear filters", key="clear_chart_filters_main", use_container_width=True, type="primary"):
            clear_chart_filters()
    with col2:
            st.info("Chart filter active - " + " | ".join(active_parts))


def section_header(text):
    st.markdown(f'<p class="section-header">{text}</p>', unsafe_allow_html=True)


def render_hero(kpis, filters):
    year_range = filters["year_range"]
    st.markdown(
        f"""
        <div class="dashboard-header">
            <div class="dashboard-header-copy">
                <div class="dashboard-eyebrow">Queensland Community Safety</div>
                <div class="dashboard-title">Crime intelligence dashboard</div>
                <div class="dashboard-summary">
                    <b>{fmt(kpis['total'])}</b> recorded offences across <b>{kpis['n_lgas']}</b> LGAs.
                    <b>{kpis['top_lga']}</b> is the current highest-burden LGA at <b>{kpis['top_lga_pct']:.1f}%</b> of scope.
                </div>
            </div>
            <div class="dashboard-header-meta">
                <div class="meta-tile">
                    <span>Period</span>
                    <b>{year_range[0]}-{year_range[1]}</b>
                </div>
                <div class="meta-tile">
                    <span>Priority LGA</span>
                    <b>{kpis['top_lga']}</b>
                </div>
                <div class="meta-tile">
                    <span>Top driver</span>
                    <b>{kpis['top_cat'].replace("Offences ", "")}</b>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_row(kpis):
    top_lga = kpis["top_lga"]
    top_cat = kpis["top_cat"]
    top_lga_label = top_lga[:16] + "…" if len(top_lga) > 16 else top_lga
    top_cat_label = top_cat.replace("Offences ", "")[:16]

    st.markdown(
        f"""
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-accent"></div>
                <div class="kpi-value">{fmt(kpis['total'])}</div>
                <div class="kpi-label">Total Offences</div>
                <div class="kpi-delta"><span class="{kpis['trend_cls']}">{kpis['trend_txt']}</span></div>
            </div>
            <div class="kpi-card">
                <div class="kpi-accent"></div>
                <div class="kpi-value">{kpis['n_lgas']}</div>
                <div class="kpi-label">LGAs in Scope</div>
                <div class="kpi-delta">&nbsp;</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-accent"></div>
                <div class="kpi-value">{top_lga_label}</div>
                <div class="kpi-label">Highest-Burden LGA</div>
                <div class="kpi-delta">{kpis['top_lga_pct']:.1f}% of total</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-accent"></div>
                <div class="kpi-value">{top_cat_label}</div>
                <div class="kpi-label">Top Offence Group</div>
                <div class="kpi-delta">{fmt(kpis['top_cat_cnt'])} incidents</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-accent"></div>
                <div class="kpi-value">{kpis['juv_pct']:.1f}%</div>
                <div class="kpi-label">Juvenile Share</div>
                <div class="kpi-delta">of total offences</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_lga_insight(sel_lga, stats, kpis):
    top_lga_note = "&nbsp; ⚠️ <b>Highest-burden LGA in current view.</b>" if sel_lga == kpis["top_lga"] else ""
    st.markdown(
        f"""
        <div class="insight-box">
            <b>{sel_lga}</b> — <b>{fmt(stats['lga_total'])} offences</b> ({stats['lga_share']:.1f}% of scope total).
            Dominant high-level category: <b>{stats['lga_top_cat']}</b> ({fmt(stats['lga_top_cnt'])} incidents).
            {top_lga_note}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_narrative_cards(columns, kpis, filters):
    reduction_pct = filters["reduction_pct"]
    w2, w3, w4 = columns

    with w2:
        st.markdown(
            """
            <div class="narrative-card">
                <h4>What</h4>
                <p>Crime is not evenly distributed across Queensland. A small number of LGAs account for a disproportionate share of recorded offences.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with w3:
        st.markdown(
            f"""
            <div class="narrative-card">
                <h4>So What</h4>
                <p><b>{kpis['top_lga']}</b> represents {kpis['top_lga_pct']:.1f}% of all offences in scope. The dominant issue is <b>{kpis['top_cat']}</b>, suggesting targeted programs could have outsized impact.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with w4:
        st.markdown(
            f"""
            <div class="narrative-card">
                <h4>What Next</h4>
                <p>A {reduction_pct}% reduction in <b>{kpis['top_lga']}</b> would save <b>{fmt(kpis['projected_saving'])}</b> incidents, bringing the total down to <b>{fmt(kpis['projected_total'])}</b>.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_recommendation(kpis, filters):
    year_range = filters["year_range"]
    st.markdown(
        f"""
        <div class="recommend-box">
            <h3>Priority Recommendation</h3>
            <p>
                Based on {year_range[0]}-{year_range[1]} data, <b>{kpis['top_lga']}</b> should be the highest-priority
                LGA for targeted community safety intervention in Queensland.
                <b>{kpis['top_cat']}</b> is the dominant high-level offence group, while the drill-down shows the more specific
                offence types driving local burden. Juvenile offenders represent <b>{kpis['juv_pct']:.1f}%</b> of the total in scope.
            </p>
            <span class="tag tag-purple">QLD Government</span>
            <span class="tag tag-red">Community Safety</span>
            <span class="tag tag-green">Data-Driven Policy</span>
            <span class="tag tag-purple">Sources: QLD Police Service + ABS</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer(scope):
    st.markdown("---")
    with st.expander("Data Dictionary"):
        st.markdown(
            """
            | Column | Description |
            |---|---|
            | `lga_name_clean` | Queensland LGA name (standardised) |
            | `date` | First day of recorded month |
            | `year` / `month_num` | Temporal filters |
            | `age_group` | Adult or Juvenile |
            | `sex` | Female / Male / Not Stated |
            | `offence_group` | High-level offence category |
            | `offence_count` | Recorded offences |
            | `lat` / `lon` | ABS LGA centroid coordinates matched to QLD Police LGA names |

            **Sources:** Queensland Police Service — Monthly LGA Reported Offenders data; Australian Bureau of Statistics (ABS)
            geographic reference data for LGA latitude/longitude coordinates, matched by LGA name when creating `qld_summary_long.csv`.
            """
        )
    with st.expander("View Filtered Summary Data"):
        st.dataframe(scope, use_container_width=True)
