"""
Netflix Analytics Dashboard
============================
Requirements: dash, dash-bootstrap-components, Pillow
Install: pip install dash dash-bootstrap-components Pillow

Usage:
    python netflix_dashboard.py
    Then open → http://127.0.0.1:8050

Place this file in the SAME folder that contains the 'netflix_plots' directory.
Expected charts inside netflix_plots/:
    01_content_type_donut.png
    02_content_added_per_year.png
    03_top_countries.png
    04_top_genres.png
    05_rating_distribution.png
    06_movie_duration_hist.png
    07_tvshow_seasons_hist.png
    08_release_year_trend.png
"""

import base64
import os
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

# ── Config ────────────────────────────────────────────────────────────────────
PLOTS_DIR = Path("netflix_plots")

CHART_META = [
    {
        "file": "01_content_type_donut.png",
        "title": "Content Split",
        "subtitle": "Movies vs TV Shows",
        "icon": "🍿",
        "size": "sm",
    },
    {
        "file": "04_top_genres.png",
        "title": "Top Genres",
        "subtitle": "Most popular content categories",
        "icon": "🎭",
        "size": "sm",
    },
    {
        "file": "03_top_countries.png",
        "title": "Top Countries",
        "subtitle": "Biggest content producers",
        "icon": "🌍",
        "size": "sm",
    },
    {
        "file": "05_rating_distribution.png",
        "title": "Ratings Breakdown",
        "subtitle": "Content audience classification",
        "icon": "🔞",
        "size": "sm",
    },
    {
        "file": "02_content_added_per_year.png",
        "title": "Growth Over Time",
        "subtitle": "Content added to Netflix by year",
        "icon": "📈",
        "size": "lg",
    },
    {
        "file": "08_release_year_trend.png",
        "title": "Release Year Trends",
        "subtitle": "Original release years distribution",
        "icon": "📅",
        "size": "lg",
    },
    {
        "file": "06_movie_duration_hist.png",
        "title": "Movie Duration",
        "subtitle": "Distribution of film runtimes",
        "icon": "🎬",
        "size": "md",
    },
    {
        "file": "07_tvshow_seasons_hist.png",
        "title": "TV Show Seasons",
        "subtitle": "How long do shows run?",
        "icon": "📺",
        "size": "md",
    },
]

# ── Helpers ───────────────────────────────────────────────────────────────────
def encode_image(path: Path) -> str:
    """Base64-encode a PNG for inline embedding."""
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def load_charts() -> dict:
    images = {}
    for meta in CHART_META:
        fp = PLOTS_DIR / meta["file"]
        if fp.exists():
            images[meta["file"]] = encode_image(fp)
        else:
            images[meta["file"]] = None
    return images


# ── Layout helpers ────────────────────────────────────────────────────────────
def chart_card(meta: dict, images: dict) -> dbc.Col:
    src = images.get(meta["file"])
    size_map = {"sm": 3, "md": 4, "lg": 6}   # Bootstrap grid columns (out of 12)
    col_width = size_map.get(meta["size"], 4)

    img_el = (
        html.Img(
            src=src,
            style={
                "width": "100%",
                "borderRadius": "6px",
                "display": "block",
                "transition": "transform .3s ease",
            },
            className="chart-img",
        )
        if src
        else html.Div(
            "⚠ Chart not found",
            style={
                "color": "#666",
                "textAlign": "center",
                "padding": "60px 0",
                "fontFamily": "'DM Sans', sans-serif",
            },
        )
    )

    card_body = html.Div(
        [
            # Header row
            html.Div(
                [
                    html.Span(meta["icon"], style={"fontSize": "22px", "marginRight": "10px"}),
                    html.Div(
                        [
                            html.P(
                                meta["title"],
                                style={
                                    "margin": "0",
                                    "fontFamily": "'Bebas Neue', cursive",
                                    "fontSize": "18px",
                                    "letterSpacing": "1.5px",
                                    "color": "#FFFFFF",
                                },
                            ),
                            html.P(
                                meta["subtitle"],
                                style={
                                    "margin": "0",
                                    "fontFamily": "'DM Sans', sans-serif",
                                    "fontSize": "11px",
                                    "color": "#888888",
                                    "letterSpacing": "0.4px",
                                },
                            ),
                        ]
                    ),
                ],
                style={"display": "flex", "alignItems": "center", "marginBottom": "14px"},
            ),
            # Divider
            html.Hr(
                style={
                    "border": "none",
                    "borderTop": "1px solid #2A2A2A",
                    "margin": "0 0 14px 0",
                }
            ),
            # Chart image
            img_el,
        ],
        style={
            "background": "linear-gradient(145deg, #1C1C1C 0%, #161616 100%)",
            "border": "1px solid #2B2B2B",
            "borderRadius": "12px",
            "padding": "20px",
            "boxShadow": "0 8px 32px rgba(0,0,0,0.5)",
            "transition": "border-color .25s ease, box-shadow .25s ease",
        },
        className="card-hover",
    )

    return dbc.Col(card_body, width=12, lg=col_width, style={"marginBottom": "24px"})


# ── App ───────────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&display=swap",
    ],
    title="Netflix Analytics",
)

images = load_charts()

# KPI strip (static, derived from earlier EDA run)
KPIS = [
    ("🎬", "8,807", "Total Titles"),
    ("🎥", "6,131", "Movies"),
    ("📺", "2,676", "TV Shows"),
    ("🌍", "748", "Countries"),
    ("🗂", "42", "Genres"),
    ("📅", "2021", "Peak Year"),
]


def kpi_tile(icon, value, label):
    return html.Div(
        [
            html.Span(icon, style={"fontSize": "26px"}),
            html.P(
                value,
                style={
                    "margin": "4px 0 2px",
                    "fontFamily": "'Bebas Neue', cursive",
                    "fontSize": "28px",
                    "letterSpacing": "2px",
                    "color": "#E50914",
                    "lineHeight": "1",
                },
            ),
            html.P(
                label,
                style={
                    "margin": "0",
                    "fontFamily": "'DM Sans', sans-serif",
                    "fontSize": "10px",
                    "letterSpacing": "1.2px",
                    "color": "#777777",
                    "textTransform": "uppercase",
                },
            ),
        ],
        style={
            "textAlign": "center",
            "background": "#1A1A1A",
            "border": "1px solid #2A2A2A",
            "borderRadius": "10px",
            "padding": "18px 12px",
            "flex": "1",
            "minWidth": "100px",
        },
    )


app.layout = html.Div(
    [
        # ── Inline CSS ────────────────────────────────────────────────────────
        html.Style(
            """
            body { background-color: #0F0F0F !important; margin: 0; }
            .card-hover:hover {
                border-color: #E50914 !important;
                box-shadow: 0 12px 40px rgba(229,9,20,0.18) !important;
            }
            .card-hover:hover .chart-img {
                transform: scale(1.018);
            }
            ::-webkit-scrollbar { width: 6px; }
            ::-webkit-scrollbar-track { background: #0F0F0F; }
            ::-webkit-scrollbar-thumb { background: #E50914; border-radius: 3px; }
            """
        ),

        # ── Hero Header ───────────────────────────────────────────────────────
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span(
                                    "N",
                                    style={
                                        "color": "#E50914",
                                        "fontFamily": "'Bebas Neue', cursive",
                                        "fontSize": "52px",
                                        "lineHeight": "1",
                                        "marginRight": "2px",
                                    },
                                ),
                                html.Span(
                                    "ETFLIX",
                                    style={
                                        "color": "#FFFFFF",
                                        "fontFamily": "'Bebas Neue', cursive",
                                        "fontSize": "52px",
                                        "lineHeight": "1",
                                    },
                                ),
                            ],
                            style={"display": "flex", "alignItems": "baseline"},
                        ),
                        html.P(
                            "Content Analytics Dashboard",
                            style={
                                "fontFamily": "'DM Sans', sans-serif",
                                "fontSize": "13px",
                                "color": "#888",
                                "letterSpacing": "3px",
                                "textTransform": "uppercase",
                                "margin": "4px 0 0 4px",
                            },
                        ),
                    ]
                ),
                html.Div(
                    html.P(
                        "Exploratory data analysis across 8,800+ titles",
                        style={
                            "fontFamily": "'DM Sans', sans-serif",
                            "fontSize": "13px",
                            "color": "#555",
                            "margin": "0",
                        },
                    ),
                    style={"alignSelf": "flex-end"},
                ),
            ],
            style={
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "flex-end",
                "padding": "36px 48px 24px",
                "borderBottom": "1px solid #1E1E1E",
            },
        ),

        # ── Red accent line ───────────────────────────────────────────────────
        html.Div(
            style={
                "height": "3px",
                "background": "linear-gradient(90deg, #E50914 0%, #FF6B6B 50%, transparent 100%)",
            }
        ),

        # ── KPI Strip ─────────────────────────────────────────────────────────
        html.Div(
            [kpi_tile(icon, val, lbl) for icon, val, lbl in KPIS],
            style={
                "display": "flex",
                "gap": "16px",
                "padding": "28px 48px",
                "flexWrap": "wrap",
            },
        ),

        # ── Section label ─────────────────────────────────────────────────────
        html.Div(
            [
                html.Span(
                    "▎",
                    style={"color": "#E50914", "fontSize": "22px", "marginRight": "10px"},
                ),
                html.Span(
                    "CHARTS & INSIGHTS",
                    style={
                        "fontFamily": "'Bebas Neue', cursive",
                        "fontSize": "20px",
                        "letterSpacing": "3px",
                        "color": "#CCCCCC",
                    },
                ),
            ],
            style={"padding": "0 48px 20px", "display": "flex", "alignItems": "center"},
        ),

        # ── Chart Grid ────────────────────────────────────────────────────────
        html.Div(
            dbc.Row(
                [chart_card(meta, images) for meta in CHART_META],
                style={"margin": "0"},
            ),
            style={"padding": "0 36px"},
        ),

        # ── Footer ────────────────────────────────────────────────────────────
        html.Div(
            [
                html.P(
                    "Netflix Titles Dataset  ·  EDA built with Python & Dash",
                    style={
                        "fontFamily": "'DM Sans', sans-serif",
                        "fontSize": "12px",
                        "color": "#444",
                        "margin": "0",
                        "letterSpacing": "0.5px",
                    },
                )
            ],
            style={
                "textAlign": "center",
                "padding": "32px",
                "borderTop": "1px solid #1A1A1A",
                "marginTop": "16px",
            },
        ),
    ],
    style={"background": "#0F0F0F", "minHeight": "100vh"},
)

if __name__ == "__main__":
    missing = [m["file"] for m in CHART_META if not (PLOTS_DIR / m["file"]).exists()]
    if missing:
        print(f"\n⚠  Missing chart files (will show placeholder):")
        for f in missing:
            print(f"   • netflix_plots/{f}")
    print("\n🎬  Netflix Dashboard running → http://127.0.0.1:8050\n")
    app.run(debug=False)