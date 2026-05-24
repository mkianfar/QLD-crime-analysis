import streamlit as st
import streamlit.components.v1 as components


THEME_PALETTES = {
    "dark": {
        "app_bg": "#0b1120",
        "app_text": "#e2e8f0",
        "surface": "#111827",
        "surface_alt": "#151f32",
        "surface_soft": "#1f2937",
        "panel_text": "#e2e8f0",
        "muted_text": "#94a3b8",
        "rule": "#1e293b",
        "chart_panel": "#111827",
        "chart_border": "#263449",
        "chart_text": "#e2e8f0",
        "chart_muted": "#94a3b8",
        "chart_grid": "#334155",
        "map_style": "carto-darkmatter",
        "chart_shadow": "0 1px 2px rgba(0,0,0,0.28)",
        "hero_shadow": "0 1px 2px rgba(0,0,0,0.24)",
        "kpi_shadow": "0 1px 2px rgba(0,0,0,0.24)",
        "panel_shadow": "0 1px 2px rgba(0,0,0,0.24)",
        "sidebar_bg": "#0b1220",
        "sidebar_text": "#e2e8f0",
        "sidebar_muted": "#94a3b8",
        "sidebar_border": "#1e293b",
        "accent": "#38bdf8",
        "accent_strong": "#0ea5e9",
        "accent_soft": "rgba(14,165,233,0.12)",
        "danger": "#f87171",
        "success": "#4ade80",
        "section_accent": "#38bdf8",
        "button_secondary_text": "#e2e8f0",
        "button_secondary_border": "#475569",
    },
    "light": {
        "app_bg": "#f4f7fb",
        "app_text": "#1e293b",
        "surface": "#ffffff",
        "surface_alt": "#f7fafc",
        "surface_soft": "#eaf0f7",
        "panel_text": "#172033",
        "muted_text": "#64748b",
        "rule": "#e2e8f0",
        "chart_panel": "#ffffff",
        "chart_border": "#dbe3ef",
        "chart_text": "#1e293b",
        "chart_muted": "#64748b",
        "chart_grid": "#e2e8f0",
        "map_style": "carto-positron",
        "chart_shadow": "0 1px 2px rgba(15,23,42,0.06)",
        "hero_shadow": "0 1px 2px rgba(15,23,42,0.06)",
        "kpi_shadow": "0 1px 2px rgba(15,23,42,0.06)",
        "panel_shadow": "0 1px 2px rgba(15,23,42,0.06)",
        "sidebar_bg": "#0f172a",
        "sidebar_text": "#e2e8f0",
        "sidebar_muted": "#94a3b8",
        "sidebar_border": "#dbe3ef",
        "accent": "#0f766e",
        "accent_strong": "#0d9488",
        "accent_soft": "rgba(13,148,136,0.10)",
        "danger": "#dc2626",
        "success": "#16a34a",
        "section_accent": "#0f766e",
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


def sync_theme_switches():
    components.html(
        """
        <script>
        (() => {
          try {
            const key = "qld-dashboard-theme-class";
            const parentWindow = window.parent;
            const parentDocument = parentWindow.document;
            const app = parentDocument.querySelector(".stApp");
            if (!app) return;

            const currentClass = app.className || "";
            parentWindow.sessionStorage.setItem(key, currentClass);

            let pendingReload = false;
            const observer = new parentWindow.MutationObserver(() => {
              const nextClass = app.className || "";
              const previousClass = parentWindow.sessionStorage.getItem(key);
              if (!pendingReload && nextClass && nextClass !== previousClass) {
                pendingReload = true;
                parentWindow.sessionStorage.setItem(key, nextClass);
                parentWindow.setTimeout(() => parentWindow.location.reload(), 150);
              }
            });

            observer.observe(app, { attributes: true, attributeFilter: ["class"] });
          } catch (error) {
            // Theme syncing is progressive enhancement; the dashboard still works without it.
          }
        })();
        </script>
        """,
        height=0,
        width=0,
    )
