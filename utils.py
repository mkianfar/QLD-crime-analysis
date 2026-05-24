import streamlit as st


THEME_PALETTES = {
    "dark": {
        "app_bg": "#0f172a",
        "app_text": "#e2e8f0",
        "surface": "#111827",
        "surface_alt": "#172033",
        "surface_soft": "#1e293b",
        "panel_text": "#e2e8f0",
        "muted_text": "#94a3b8",
        "rule": "#1e293b",
        "chart_panel": "#111827",
        "chart_border": "#334155",
        "chart_text": "#e2e8f0",
        "chart_muted": "#94a3b8",
        "chart_grid": "#334155",
        "map_style": "carto-darkmatter",
        "chart_shadow": "0 10px 24px rgba(0,0,0,0.24)",
        "hero_shadow": "0 12px 40px rgba(79,70,229,0.28)",
        "kpi_shadow": "0 4px 16px rgba(0,0,0,0.28)",
        "panel_shadow": "0 18px 40px rgba(0,0,0,0.28)",
        "sidebar_bg": "#0b1220",
        "sidebar_text": "#e2e8f0",
        "sidebar_muted": "#94a3b8",
        "sidebar_border": "#1e293b",
        "accent": "#818cf8",
        "accent_strong": "#6366f1",
        "accent_soft": "rgba(129,140,248,0.16)",
        "danger": "#f87171",
        "success": "#4ade80",
        "section_accent": "#818cf8",
        "button_secondary_text": "#e2e8f0",
        "button_secondary_border": "#475569",
    },
    "light": {
        "app_bg": "#eef3f8",
        "app_text": "#1e293b",
        "surface": "#ffffff",
        "surface_alt": "#f8fafc",
        "surface_soft": "#eaf0f7",
        "panel_text": "#172033",
        "muted_text": "#64748b",
        "rule": "#e2e8f0",
        "chart_panel": "#ffffff",
        "chart_border": "#e2e8f0",
        "chart_text": "#1e293b",
        "chart_muted": "#64748b",
        "chart_grid": "#e2e8f0",
        "map_style": "carto-positron",
        "chart_shadow": "0 10px 24px rgba(15,23,42,0.06)",
        "hero_shadow": "0 18px 42px rgba(30,41,59,0.18)",
        "kpi_shadow": "0 12px 24px rgba(15,23,42,0.16)",
        "panel_shadow": "0 18px 40px rgba(15,23,42,0.08)",
        "sidebar_bg": "#0f172a",
        "sidebar_text": "#e2e8f0",
        "sidebar_muted": "#94a3b8",
        "sidebar_border": "#dbe3ef",
        "accent": "#4f46e5",
        "accent_strong": "#4338ca",
        "accent_soft": "rgba(79,70,229,0.10)",
        "danger": "#dc2626",
        "success": "#16a34a",
        "section_accent": "#4f46e5",
        "button_secondary_text": "#334155",
        "button_secondary_border": "#dbe3ef",
    },
}


def current_theme_type():
    theme_type = getattr(st.context.theme, "type", None)
    if theme_type in THEME_PALETTES:
        return theme_type

    configured_theme = st.get_option("theme.base")
    if configured_theme in THEME_PALETTES:
        return configured_theme

    return "dark"


def theme_palette():
    return THEME_PALETTES[current_theme_type()]


def theme_css_variables():
    palette = theme_palette()
    variables = "\n".join(f"  --{name.replace('_', '-')}: {value};" for name, value in palette.items())
    return f":root {{\n{variables}\n}}"


def fmt(x):
    return f"{int(round(x)):,}"


def load_css(path):
    css = path.read_text(encoding="utf-8")
    st.markdown(f"<style>{theme_css_variables()}\n{css}</style>", unsafe_allow_html=True)
