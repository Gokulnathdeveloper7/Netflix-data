"""
Netflix Titles Dataset - Data Cleaning, EDA & Visualization
============================================================
Requirements: pandas, matplotlib, seaborn, wordcloud
Install: pip install pandas matplotlib seaborn wordcloud
Usage:  python netflix_eda.py
        Place 'netflix_titles.csv' in the same directory.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from wordcloud import WordCloud
import warnings
import os

warnings.filterwarnings("ignore")

# ── Aesthetics ────────────────────────────────────────────────────────────────
NETFLIX_RED  = "#E50914"
BG_DARK      = "#141414"
BG_CARD      = "#1F1F1F"
TEXT_LIGHT   = "#FFFFFF"
TEXT_MUTED   = "#AAAAAA"
ACCENT_GOLD  = "#F5C518"
PALETTE      = [NETFLIX_RED, "#FF6B6B", "#FF8E53", ACCENT_GOLD,
                "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]

plt.rcParams.update({
    "figure.facecolor":  BG_DARK,
    "axes.facecolor":    BG_CARD,
    "axes.edgecolor":    "#333333",
    "axes.labelcolor":   TEXT_LIGHT,
    "axes.titlecolor":   TEXT_LIGHT,
    "xtick.color":       TEXT_MUTED,
    "ytick.color":       TEXT_MUTED,
    "text.color":        TEXT_LIGHT,
    "grid.color":        "#2A2A2A",
    "grid.linestyle":    "--",
    "grid.linewidth":    0.6,
    "font.family":       "DejaVu Sans",
    "axes.titlesize":    13,
    "axes.labelsize":    11,
})

OUTPUT_DIR = "netflix_plots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def save(fig, name):
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG_DARK)
    print(f"  ✔  Saved → {path}")
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# 1. LOAD
# ══════════════════════════════════════════════════════════════════════════════
print("\n━━━  1. LOADING DATA  ━━━")
df = pd.read_csv("netflix_titles.csv")
print(f"  Shape (raw): {df.shape}")


# ══════════════════════════════════════════════════════════════════════════════
# 2. DATA CLEANING
# ══════════════════════════════════════════════════════════════════════════════
print("\n━━━  2. DATA CLEANING  ━━━")

# 2-a  Duplicates
dupes = df.duplicated().sum()
df.drop_duplicates(inplace=True)
print(f"  Duplicate rows removed : {dupes}")

# 2-b  Missing values (before)
print("\n  Missing values (before cleaning):")
mv = df.isnull().sum()
print(mv[mv > 0].to_string())

# 2-c  Fill missing values with sensible defaults
df["director"].fillna("Unknown", inplace=True)
df["cast"].fillna("Unknown", inplace=True)
df["country"].fillna("Unknown", inplace=True)
df["rating"].fillna("Unknown", inplace=True)
df.dropna(subset=["date_added", "duration"], inplace=True)

# 2-d  Parse date_added → year / month
df["date_added"]   = pd.to_datetime(df["date_added"].str.strip(), errors="coerce")
df["year_added"]   = df["date_added"].dt.year
df["month_added"]  = df["date_added"].dt.month_name()

# 2-e  Numeric duration
df["duration_int"] = df["duration"].str.extract(r"(\d+)").astype(float)

# 2-f  Primary genre (first listed)
df["primary_genre"] = df["listed_in"].str.split(",").str[0].str.strip()

print("\n  Missing values (after cleaning):")
mv2 = df.isnull().sum()
print(mv2[mv2 > 0].to_string() if mv2[mv2 > 0].any() else "  → None")
print(f"\n  Shape (clean): {df.shape}")

# 2-g  Basic stats
print("\n  Descriptive statistics (numeric columns):")
print(df[["release_year", "duration_int"]].describe().to_string())


# ══════════════════════════════════════════════════════════════════════════════
# 3. VISUALISATIONS
# ══════════════════════════════════════════════════════════════════════════════
print("\n━━━  3. GENERATING PLOTS  ━━━")

# ── Helper ────────────────────────────────────────────────────────────────────
def style_ax(ax, title, xlabel="", ylabel="", grid_axis="y"):
    ax.set_title(title, pad=12, fontweight="bold")
    ax.set_xlabel(xlabel, labelpad=8)
    ax.set_ylabel(ylabel, labelpad=8)
    ax.grid(axis=grid_axis, alpha=0.4)
    ax.spines[["top", "right", "left", "bottom"]].set_visible(False)

# ── 3-1  Movies vs TV Shows (donut) ──────────────────────────────────────────
print("\n  [1/10] Content type split …")
counts = df["type"].value_counts()
fig, ax = plt.subplots(figsize=(6, 6), facecolor=BG_DARK)
wedges, texts, autotexts = ax.pie(
    counts, labels=counts.index, autopct="%1.1f%%",
    colors=[NETFLIX_RED, ACCENT_GOLD], startangle=90,
    wedgeprops=dict(width=0.55, edgecolor=BG_DARK, linewidth=3),
    textprops=dict(color=TEXT_LIGHT, fontsize=13, fontweight="bold"),
)
for at in autotexts:
    at.set_fontsize(11)
ax.set_title("Movies vs TV Shows", fontsize=15, fontweight="bold", pad=20)
fig.patch.set_facecolor(BG_DARK)
save(fig, "01_content_type_donut.png")

# ── 3-2  Content added per year (bar) ────────────────────────────────────────
print("  [2/10] Content added per year …")
yearly = df.groupby(["year_added", "type"]).size().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(14, 5), facecolor=BG_DARK)
yearly.plot(kind="bar", ax=ax, color=[NETFLIX_RED, ACCENT_GOLD],
            width=0.7, edgecolor="none")
style_ax(ax, "Content Added to Netflix by Year", "Year", "Number of Titles")
ax.legend(facecolor=BG_CARD, edgecolor="#444", labelcolor=TEXT_LIGHT)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
save(fig, "02_content_added_per_year.png")

# ── 3-3  Top 15 countries ─────────────────────────────────────────────────────
print("  [3/10] Top 15 content-producing countries …")
countries = (
    df[df["country"] != "Unknown"]["country"]
    .str.split(",").explode().str.strip()
    .value_counts().head(15)
)
fig, ax = plt.subplots(figsize=(10, 6), facecolor=BG_DARK)
bars = ax.barh(countries.index[::-1], countries.values[::-1],
               color=[NETFLIX_RED if i == 14 else "#FF6B6B"
                      for i in range(15)], edgecolor="none")
for bar, val in zip(bars, countries.values[::-1]):
    ax.text(bar.get_width() + 8, bar.get_y() + bar.get_height() / 2,
            str(val), va="center", fontsize=9, color=TEXT_MUTED)
style_ax(ax, "Top 15 Countries by Number of Titles", "Count", "", grid_axis="x")
save(fig, "03_top_countries.png")

# ── 3-4  Top 10 genres ────────────────────────────────────────────────────────
print("  [4/10] Top 10 genres …")
genres = df["primary_genre"].value_counts().head(10)
fig, ax = plt.subplots(figsize=(10, 5), facecolor=BG_DARK)
sns.barplot(x=genres.values, y=genres.index, ax=ax,
            palette=sns.color_palette(PALETTE, 10))
style_ax(ax, "Top 10 Primary Genres", "Number of Titles", "", grid_axis="x")
for i, v in enumerate(genres.values):
    ax.text(v + 5, i, str(v), va="center", fontsize=9, color=TEXT_MUTED)
save(fig, "04_top_genres.png")

# ── 3-5  Rating distribution ─────────────────────────────────────────────────
print("  [5/10] Rating distribution …")
rating_order = (df[df["rating"] != "Unknown"]["rating"]
                .value_counts().index.tolist())
fig, ax = plt.subplots(figsize=(12, 5), facecolor=BG_DARK)
sns.countplot(data=df[df["rating"] != "Unknown"],
              x="rating", order=rating_order, ax=ax,
              palette=sns.color_palette(PALETTE * 3, len(rating_order)))
style_ax(ax, "Content Ratings Distribution", "Rating", "Count")
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
save(fig, "05_rating_distribution.png")

# ── 3-6  Movie duration histogram ────────────────────────────────────────────
print("  [6/10] Movie duration histogram …")
movies = df[(df["type"] == "Movie") & (df["duration_int"].notna())]
fig, ax = plt.subplots(figsize=(10, 5), facecolor=BG_DARK)
ax.hist(movies["duration_int"], bins=40, color=NETFLIX_RED,
        edgecolor=BG_DARK, linewidth=0.5, alpha=0.9)
ax.axvline(movies["duration_int"].median(), color=ACCENT_GOLD,
           linestyle="--", linewidth=1.5,
           label=f'Median: {movies["duration_int"].median():.0f} min')
style_ax(ax, "Movie Duration Distribution", "Duration (minutes)", "Count")
ax.legend(facecolor=BG_CARD, edgecolor="#444", labelcolor=TEXT_LIGHT)
save(fig, "06_movie_duration_hist.png")

# ── 3-7  TV Show seasons histogram ───────────────────────────────────────────
print("  [7/10] TV show seasons histogram …")
shows = df[(df["type"] == "TV Show") & (df["duration_int"].notna())]
fig, ax = plt.subplots(figsize=(10, 5), facecolor=BG_DARK)
max_s = int(shows["duration_int"].max())
ax.hist(shows["duration_int"], bins=range(1, max_s + 2),
        color=ACCENT_GOLD, edgecolor=BG_DARK, linewidth=0.5, alpha=0.9,
        align="left")
style_ax(ax, "TV Show – Number of Seasons Distribution",
         "Seasons", "Number of Shows")
ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
save(fig, "07_tvshow_seasons_hist.png")

# ── 3-8  Releases per year (line) ────────────────────────────────────────────
print("  [8/10] Releases per year …")
yearly_release = df.groupby(["release_year", "type"]).size().unstack(fill_value=0)
yearly_release = yearly_release[yearly_release.index >= 1990]
fig, ax = plt.subplots(figsize=(14, 5), facecolor=BG_DARK)
for col, color in zip(yearly_release.columns, [NETFLIX_RED, ACCENT_GOLD]):
    ax.plot(yearly_release.index, yearly_release[col],
            color=color, linewidth=2, label=col, marker="o",
            markersize=3, markerfacecolor=color)
    ax.fill_between(yearly_release.index, yearly_release[col],
                    alpha=0.15, color=color)
style_ax(ax, "Titles Released per Year (1990–)", "Release Year", "Count")
ax.legend(facecolor=BG_CARD, edgecolor="#444", labelcolor=TEXT_LIGHT)
save(fig, "08_release_year_trend.png")

# ── 3-9  Month added heatmap ─────────────────────────────────────────────────
print("  [9/10] Month-added heatmap …")
month_order = ["January","February","March","April","May","June",
               "July","August","September","October","November","December"]
heat_df = (df.groupby(["year_added", "month_added"])
             .size().reset_index(name="count"))
heat_df["month_added"] = pd.Categorical(heat_df["month_added"],
                                         categories=month_order, ordered=True)
pivot = heat_df.pivot_table(index="month_added", columns="year_added",
                             values="count", fill_value=0)
fig, ax = plt.subplots(figsize=(14, 7), facecolor=BG_DARK)
sns.heatmap(pivot, cmap="YlOrRd", linewidths=0.5, linecolor="#0A0A0A",
            ax=ax, annot=True, fmt="d", annot_kws={"size": 7},
            cbar_kws={"shrink": 0.8})
ax.set_title("Titles Added by Month & Year", fontsize=13,
             fontweight="bold", pad=12)
ax.set_xlabel("Year Added", labelpad=8)
ax.set_ylabel("Month Added", labelpad=8)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", rotation=0)
save(fig, "09_month_added_heatmap.png")

# ── 3-10  Word cloud of titles ───────────────────────────────────────────────
print("  [10/10] Title word cloud …")
text = " ".join(df["title"].dropna().tolist())
wc = WordCloud(
    width=1400, height=700,
    background_color=BG_DARK,
    colormap="Reds",
    max_words=200,
    collocations=False,
    prefer_horizontal=0.85,
).generate(text)
fig, ax = plt.subplots(figsize=(14, 7), facecolor=BG_DARK)
ax.imshow(wc, interpolation="bilinear")
ax.axis("off")
ax.set_title("Netflix Titles – Word Cloud", fontsize=15,
             fontweight="bold", pad=12)
save(fig, "10_title_wordcloud.png")


# ══════════════════════════════════════════════════════════════════════════════
# 4. SUMMARY DASHBOARD (single composite figure)
# ══════════════════════════════════════════════════════════════════════════════
print("\n━━━  4. BUILDING SUMMARY DASHBOARD  ━━━")

fig = plt.figure(figsize=(20, 24), facecolor=BG_DARK)
fig.suptitle("🎬  Netflix Titles – EDA Dashboard",
             fontsize=22, fontweight="bold", color=TEXT_LIGHT, y=0.98)

gs = fig.add_gridspec(4, 3, hspace=0.55, wspace=0.4)

# Row 0 — Donut | Countries | Genres
ax0 = fig.add_subplot(gs[0, 0])
ax0.pie(counts, labels=counts.index, autopct="%1.1f%%",
        colors=[NETFLIX_RED, ACCENT_GOLD], startangle=90,
        wedgeprops=dict(width=0.55, edgecolor=BG_DARK, linewidth=2),
        textprops=dict(color=TEXT_LIGHT, fontsize=10))
ax0.set_title("Content Split", fontweight="bold")

ax1 = fig.add_subplot(gs[0, 1])
top10c = countries.head(10)
ax1.barh(top10c.index[::-1], top10c.values[::-1], color=NETFLIX_RED)
style_ax(ax1, "Top 10 Countries", "Count", "", grid_axis="x")
ax1.tick_params(labelsize=8)

ax2 = fig.add_subplot(gs[0, 2])
top8g = genres.head(8)
sns.barplot(x=top8g.values, y=top8g.index, ax=ax2,
            palette=sns.color_palette(PALETTE, 8))
style_ax(ax2, "Top 8 Genres", "Count", "", grid_axis="x")
ax2.tick_params(labelsize=8)

# Row 1 — Added per year (span 3 cols)
ax3 = fig.add_subplot(gs[1, :])
yearly.plot(kind="bar", ax=ax3, color=[NETFLIX_RED, ACCENT_GOLD],
            width=0.7, edgecolor="none")
style_ax(ax3, "Content Added per Year", "Year", "Titles Added")
ax3.legend(facecolor=BG_CARD, edgecolor="#444", labelcolor=TEXT_LIGHT,
           fontsize=9)
ax3.set_xticklabels(ax3.get_xticklabels(), rotation=45, ha="right",
                    fontsize=8)

# Row 2 — Rating | Movie duration | TV seasons
ax4 = fig.add_subplot(gs[2, 0])
r_data = df[df["rating"] != "Unknown"]["rating"].value_counts().head(10)
sns.barplot(x=r_data.values, y=r_data.index, ax=ax4,
            palette=sns.color_palette(PALETTE * 2, 10))
style_ax(ax4, "Top Ratings", "Count", "", grid_axis="x")
ax4.tick_params(labelsize=8)

ax5 = fig.add_subplot(gs[2, 1])
ax5.hist(movies["duration_int"], bins=30, color=NETFLIX_RED,
         edgecolor=BG_DARK, alpha=0.9)
ax5.axvline(movies["duration_int"].median(), color=ACCENT_GOLD,
            linestyle="--", linewidth=1.3,
            label=f'Median {movies["duration_int"].median():.0f} min')
style_ax(ax5, "Movie Duration (min)", "Minutes", "Count")
ax5.legend(fontsize=8, facecolor=BG_CARD, edgecolor="#444",
           labelcolor=TEXT_LIGHT)

ax6 = fig.add_subplot(gs[2, 2])
ax6.hist(shows["duration_int"], bins=range(1, int(shows["duration_int"].max()) + 2),
         color=ACCENT_GOLD, edgecolor=BG_DARK, alpha=0.9, align="left")
style_ax(ax6, "TV Show Seasons", "Seasons", "Count")
ax6.tick_params(labelsize=8)

# Row 3 — Release year trend (span 3 cols)
ax7 = fig.add_subplot(gs[3, :])
for col, color in zip(yearly_release.columns, [NETFLIX_RED, ACCENT_GOLD]):
    ax7.plot(yearly_release.index, yearly_release[col],
             color=color, linewidth=2, label=col, marker="o",
             markersize=3, markerfacecolor=color)
    ax7.fill_between(yearly_release.index, yearly_release[col],
                     alpha=0.15, color=color)
style_ax(ax7, "Titles Released per Year (1990–)", "Release Year", "Count")
ax7.legend(facecolor=BG_CARD, edgecolor="#444", labelcolor=TEXT_LIGHT,
           fontsize=9)

dash_path = os.path.join(OUTPUT_DIR, "00_dashboard.png")
fig.savefig(dash_path, dpi=150, bbox_inches="tight", facecolor=BG_DARK)
print(f"  ✔  Dashboard saved → {dash_path}")
plt.close(fig)

# ══════════════════════════════════════════════════════════════════════════════
# 5. PRINTED EDA SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
print("\n━━━  5. EDA SUMMARY  ━━━")
print(f"  Total titles           : {len(df):,}")
print(f"  Movies                 : {(df['type']=='Movie').sum():,}")
print(f"  TV Shows               : {(df['type']=='TV Show').sum():,}")
print(f"  Unique countries       : {df['country'].str.split(',').explode().str.strip().nunique()}")
print(f"  Unique genres          : {df['primary_genre'].nunique()}")
print(f"  Date range (added)     : {df['year_added'].min():.0f} – {df['year_added'].max():.0f}")
print(f"  Release year range     : {df['release_year'].min()} – {df['release_year'].max()}")
print(f"  Avg movie duration     : {movies['duration_int'].mean():.1f} min")
print(f"  Avg TV show seasons    : {shows['duration_int'].mean():.1f}")
print(f"  Most common rating     : {df[df['rating']!='Unknown']['rating'].mode()[0]}")
print(f"  Top country            : {countries.index[0]}")
print(f"  Top genre              : {genres.index[0]}")
print(f"\n  All plots saved to → ./{OUTPUT_DIR}/")
print("  Done! ✅\n")