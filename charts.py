import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from constants import INDIGO_SCALE, OFFENCE_COLOURS
from utils import fmt, theme_palette


MAP_HEIGHT = 560
DONUT_HEIGHT = 560


def enable_point_selection(fig):
    fig.update_layout(clickmode="event+select")
    return fig


def base_layout(height=380, xtitle="", ytitle=""):
    palette = theme_palette()
    return dict(
        height=height,
        paper_bgcolor=palette["chart_panel"],
        plot_bgcolor=palette["chart_panel"],
        font=dict(color=palette["chart_text"], size=12, family="Inter"),
        title_font=dict(color=palette["chart_text"], size=13, family="Inter"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=palette["chart_muted"], size=11)),
        margin=dict(t=42, b=28, l=10, r=10),
        xaxis_title=xtitle,
        yaxis_title=ytitle,
    )


def empty_chart(title, height=380):
    fig = go.Figure()
    fig.update_layout(**base_layout(height, "", ""), title=title)
    return fig


def build_map(scope, map_mode, top_n):
    palette = theme_palette()
    map_df = (
        scope.groupby(["lga_name_clean", "lat", "lon"], as_index=False)["offence_count"]
        .sum()
        .dropna(subset=["lat", "lon"])
    )

    if map_df.empty:
        return empty_chart("Geographic concentration of offence burden", MAP_HEIGHT)

    if map_mode == "Top N LGAs":
        map_df = map_df.sort_values("offence_count", ascending=False).head(top_n)

    max_count = map_df["offence_count"].max()
    map_df["bubble"] = (map_df["offence_count"] / max_count * 40 + 5).clip(5, 45) if max_count else 5

    fig = px.scatter_mapbox(
        map_df,
        lat="lat",
        lon="lon",
        size="bubble",
        size_max=45,
        color="offence_count",
        color_continuous_scale="Reds",
        hover_name="lga_name_clean",
        custom_data=["lga_name_clean", "offence_count"],
        zoom=4.6,
        center={"lat": -22, "lon": 144.5},
        mapbox_style=palette["map_style"],
        title="Geographic concentration of offence burden",
    )
    fig.update_traces(
        marker=dict(opacity=0.78),
        hovertemplate="<b>%{customdata[0]}</b><br>Offences: <b>%{customdata[1]:,}</b><extra></extra>",
    )
    fig.update_layout(
        height=MAP_HEIGHT,
        paper_bgcolor=palette["chart_panel"],
        plot_bgcolor=palette["chart_panel"],
        font=dict(color=palette["chart_text"], size=12, family="Inter"),
        title_font=dict(color=palette["chart_text"], size=13),
        coloraxis_colorbar=dict(title="Count", tickfont=dict(color=palette["chart_text"])),
        margin=dict(t=42, b=8, l=8, r=8),
    )
    return enable_point_selection(fig)


def build_donut(top_cat_df, total):
    palette = theme_palette()
    donut_df = top_cat_df.copy()
    donut_df["colour"] = donut_df["offence_group"].map(OFFENCE_COLOURS).fillna("#94a3b8")

    fig = go.Figure(
        go.Pie(
            labels=donut_df["offence_group"],
            values=donut_df["offence_count"],
            customdata=donut_df[["offence_group"]],
            hole=0.60,
            marker_colors=donut_df["colour"],
            hovertemplate="<b>%{label}</b><br>%{value:,} offences (%{percent})<extra></extra>",
            textinfo="none",
        )
    )
    fig.update_layout(
        title="Offence mix across selected period",
        height=DONUT_HEIGHT,
        paper_bgcolor=palette["chart_panel"],
        plot_bgcolor=palette["chart_panel"],
        font=dict(color=palette["chart_text"], size=12, family="Inter"),
        title_font=dict(color=palette["chart_text"], size=13),
        legend=dict(
            orientation="v",
            x=1.02,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, color=palette["chart_muted"]),
        ),
        annotations=[
            dict(
                text=f"<b>{fmt(total)}</b><br>total",
                x=0.5,
                y=0.5,
                font=dict(size=15, color=palette["chart_muted"]),
                showarrow=False,
            )
        ],
        margin=dict(t=42, b=8, l=8, r=136),
    )
    return enable_point_selection(fig)


def build_trend(scope):
    trend_df = scope.groupby(["year", "offence_group"], as_index=False)["offence_count"].sum()
    fig = px.area(
        trend_df,
        x="year",
        y="offence_count",
        color="offence_group",
        custom_data=["year", "offence_group"],
        color_discrete_map=OFFENCE_COLOURS,
        title="Annual offence trend by category",
    )
    fig.update_traces(hovertemplate="<b>%{fullData.name}</b><br>%{x}: <b>%{y:,}</b><extra></extra>")
    fig.update_layout(**base_layout(360, "Year", "Offence Count"))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor=theme_palette()["chart_grid"])
    return enable_point_selection(fig)


def build_top_lgas(top_lga_df, top_n):
    top_lgas_df = top_lga_df.head(top_n).sort_values("offence_count", ascending=True)
    fig = px.bar(
        top_lgas_df,
        x="offence_count",
        y="lga_name_clean",
        orientation="h",
        title=f"Top {top_n} LGAs by total offence count",
        color="offence_count",
        custom_data=["lga_name_clean"],
        color_continuous_scale=INDIGO_SCALE,
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Offences: <b>%{x:,}</b><extra></extra>")
    layout = base_layout(360, "Offence Count", "")
    layout["coloraxis_showscale"] = False
    fig.update_layout(**layout)
    fig.update_xaxes(showgrid=True, gridcolor=theme_palette()["chart_grid"])
    fig.update_yaxes(showgrid=False)
    return enable_point_selection(fig)


def build_age_chart(scope):
    demo_age = scope.groupby(["year", "age_group"], as_index=False)["offence_count"].sum()
    fig = px.line(
        demo_age,
        x="year",
        y="offence_count",
        color="age_group",
        custom_data=["year", "age_group"],
        color_discrete_map={"Adult": "#0d9488", "Juvenile": "#f59e0b"},
        markers=True,
        title="Adult vs Juvenile offenders over time",
    )
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=7),
        hovertemplate="<b>%{fullData.name}</b> — %{x}: <b>%{y:,}</b><extra></extra>",
    )
    fig.update_layout(**base_layout(320, "Year", "Offence Count"))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor=theme_palette()["chart_grid"])
    return enable_point_selection(fig)


def build_sex_chart(scope):
    demo_sex = scope.groupby(["offence_group", "sex"], as_index=False)["offence_count"].sum()
    fig = px.bar(
        demo_sex,
        x="offence_count",
        y="offence_group",
        color="sex",
        orientation="h",
        barmode="group",
        custom_data=["offence_group", "sex"],
        color_discrete_map={"Female": "#f43f5e", "Male": "#0ea5e9", "Not Stated": "#94a3b8"},
        title="Offences by sex and category",
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>%{fullData.name}: <b>%{x:,}</b><extra></extra>")
    fig.update_layout(**base_layout(320, "Offence Count", ""))
    fig.update_xaxes(showgrid=True, gridcolor=theme_palette()["chart_grid"])
    fig.update_yaxes(showgrid=False)
    return enable_point_selection(fig)


def build_lga_trend(lga_df, sel_lga):
    lga_trend = lga_df.groupby(["year", "offence_group"], as_index=False)["offence_count"].sum()
    fig = px.line(
        lga_trend,
        x="year",
        y="offence_count",
        color="offence_group",
        custom_data=["year", "offence_group"],
        color_discrete_map=OFFENCE_COLOURS,
        markers=True,
        title=f"Offence trend — {sel_lga}",
    )
    fig.update_traces(
        line=dict(width=2.5),
        marker=dict(size=6),
        hovertemplate="<b>%{fullData.name}</b> — %{x}: <b>%{y:,}</b><extra></extra>",
    )
    fig.update_layout(**base_layout(380, "Year", "Count"))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor=theme_palette()["chart_grid"])
    return enable_point_selection(fig)


def build_detail_chart(detail_mix, sel_lga):
    if detail_mix.empty:
        return empty_chart("Detailed offence drivers — no data under current filters", 380)

    fig = px.bar(
        detail_mix,
        x="count",
        y="offence_type",
        orientation="h",
        title=f"Detailed offence drivers — {sel_lga}",
        color="count",
        color_continuous_scale=INDIGO_SCALE,
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Offences: <b>%{x:,}</b><extra></extra>")
    layout = base_layout(380, "Offence Count", "")
    layout["coloraxis_showscale"] = False
    fig.update_layout(**layout)
    fig.update_xaxes(showgrid=True, gridcolor=theme_palette()["chart_grid"])
    fig.update_yaxes(showgrid=False)
    return fig


def build_whatif(total, projected_total, reduction_pct, top_lga):
    whatif_df = pd.DataFrame(
        {
            "Scenario": ["Current Total", f"After {reduction_pct}% reduction in {top_lga.split()[0]}"],
            "Offences": [total, projected_total],
            "Colour": ["#0d9488", "#22c55e"],
        }
    )

    fig = px.bar(
        whatif_df,
        x="Scenario",
        y="Offences",
        color="Colour",
        color_discrete_map="identity",
        text_auto=True,
        title=f"What if offences in {top_lga} drop by {reduction_pct}%?",
    )
    fig.update_traces(
        texttemplate="%{y:,}",
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Offences: <b>%{y:,}</b><extra></extra>",
    )
    layout = base_layout(360, "", "Total Offences")
    layout["showlegend"] = False
    layout["yaxis_range"] = [0, total * 1.2]
    fig.update_layout(**layout)
    fig.update_yaxes(showgrid=True, gridcolor=theme_palette()["chart_grid"])
    return fig
