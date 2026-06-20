"""
Dataset Analysis Charts for yesil_traffic_history_dataset.csv
=============================================================
Generates 5 professional charts:
  1. Univariate Analysis (histograms + KDE)
  2. Boxplot (outlier detection)
  3. Correlation Heatmap
  4. Categorical Encoding (bar charts)
  5. Missing Values Analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from pathlib import Path

matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['axes.unicode_minus'] = False

# ── Color palette ────────────────────────────────────────────────
DARK_BG      = "#0f1117"
CARD_BG      = "#1a1d29"
ACCENT_BLUE  = "#4FC3F7"
ACCENT_CYAN  = "#00E5FF"
ACCENT_PINK  = "#FF4081"
ACCENT_GREEN = "#69F0AE"
ACCENT_AMBER = "#FFD740"
ACCENT_PURPLE = "#B388FF"
GRID_COLOR   = "#2a2d3a"
TEXT_COLOR    = "#e0e0e0"

PALETTE = [ACCENT_BLUE, ACCENT_PINK, ACCENT_GREEN, ACCENT_AMBER, ACCENT_PURPLE, ACCENT_CYAN]

OUTPUT_DIR = Path(__file__).parent / "dataset_charts"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Load data ────────────────────────────────────────────────────
df = pd.read_csv(Path(__file__).parent / "yesil_traffic_history_dataset.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])

numeric_cols = ['vehicle_count', 'avg_speed_kmh', 'temperature_c', 'congestion_level']
categorical_cols = ['intersection_id', 'weather', 'is_weekend', 'is_peak_hour', 'accident_occurred']

print(f"[OK] Dataset loaded: {df.shape[0]} rows x {df.shape[1]} columns")
print(f"   Numeric:     {numeric_cols}")
print(f"   Categorical: {categorical_cols}")
print()

# ==============================================================
# 1. UNIVARIATE ANALYSIS -- Distribution histograms + KDE
# ==============================================================
print("[1/5] Univariate Analysis ...")
fig, axes = plt.subplots(2, 2, figsize=(16, 12), facecolor=DARK_BG)
fig.suptitle("Univariate Analysis - Distribution of Numeric Features",
             color=TEXT_COLOR, fontsize=20, fontweight='bold', y=0.97)

for idx, col in enumerate(numeric_cols):
    ax = axes[idx // 2][idx % 2]
    ax.set_facecolor(CARD_BG)

    sns.histplot(df[col], bins=50, kde=True, color=PALETTE[idx],
                 edgecolor='none', alpha=0.7, ax=ax,
                 line_kws={'linewidth': 2.5})

    mean_val = df[col].mean()
    median_val = df[col].median()
    ax.axvline(mean_val, color=ACCENT_PINK, linestyle='--', linewidth=1.5, label=f'Mean = {mean_val:.1f}')
    ax.axvline(median_val, color=ACCENT_GREEN, linestyle=':', linewidth=1.5, label=f'Median = {median_val:.1f}')

    ax.set_title(col, color=TEXT_COLOR, fontsize=15, fontweight='bold', pad=10)
    ax.set_xlabel('Value', color=TEXT_COLOR, fontsize=11)
    ax.set_ylabel('Frequency', color=TEXT_COLOR, fontsize=11)
    ax.tick_params(colors=TEXT_COLOR, labelsize=10)
    ax.legend(fontsize=9, facecolor=CARD_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
    ax.grid(axis='y', color=GRID_COLOR, alpha=0.4)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)

    # Stats annotation box
    stats_text = f"std = {df[col].std():.2f}\nskew = {df[col].skew():.2f}\nkurt = {df[col].kurtosis():.2f}"
    ax.text(0.97, 0.95, stats_text, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=DARK_BG, edgecolor=ACCENT_CYAN, alpha=0.85),
            color=ACCENT_CYAN, family='monospace')

plt.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(OUTPUT_DIR / "1_univariate_analysis.png", dpi=180, facecolor=DARK_BG, bbox_inches='tight')
plt.close(fig)
print("   -> Saved: 1_univariate_analysis.png")


# ==============================================================
# 2. BOXPLOT -- Outlier Detection
# ==============================================================
print("[2/5] Boxplot ...")
fig, axes = plt.subplots(1, 4, figsize=(20, 7), facecolor=DARK_BG)
fig.suptitle("Boxplot Analysis - Outlier Detection",
             color=TEXT_COLOR, fontsize=20, fontweight='bold', y=0.98)

for idx, col in enumerate(numeric_cols):
    ax = axes[idx]
    ax.set_facecolor(CARD_BG)

    bp = ax.boxplot(df[col].dropna(), vert=True, patch_artist=True, notch=True,
                    widths=0.5,
                    boxprops=dict(facecolor=PALETTE[idx], alpha=0.6, edgecolor=TEXT_COLOR, linewidth=1.5),
                    whiskerprops=dict(color=TEXT_COLOR, linewidth=1.2),
                    capprops=dict(color=TEXT_COLOR, linewidth=1.2),
                    medianprops=dict(color=ACCENT_PINK, linewidth=2.5),
                    flierprops=dict(marker='o', markerfacecolor=ACCENT_PINK, markersize=4, alpha=0.5))

    q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
    iqr = q3 - q1
    lower_fence = q1 - 1.5 * iqr
    upper_fence = q3 + 1.5 * iqr
    outliers_count = ((df[col] < lower_fence) | (df[col] > upper_fence)).sum()

    stats_text = (f"Q1 = {q1:.1f}\nQ3 = {q3:.1f}\n"
                  f"IQR = {iqr:.1f}\n"
                  f"Outliers: {outliers_count}")
    ax.text(0.95, 0.95, stats_text, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=DARK_BG, edgecolor=PALETTE[idx], alpha=0.85),
            color=PALETTE[idx], family='monospace')

    ax.set_title(col, color=TEXT_COLOR, fontsize=14, fontweight='bold', pad=10)
    ax.tick_params(colors=TEXT_COLOR, labelsize=10)
    ax.set_xticks([])
    ax.grid(axis='y', color=GRID_COLOR, alpha=0.4)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)

plt.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig(OUTPUT_DIR / "2_boxplot_outliers.png", dpi=180, facecolor=DARK_BG, bbox_inches='tight')
plt.close(fig)
print("   -> Saved: 2_boxplot_outliers.png")


# ==============================================================
# 3. CORRELATION HEATMAP
# ==============================================================
print("[3/5] Correlation Heatmap ...")

# Encode categoricals for correlation
df_enc = df.copy()
df_enc['hour'] = df_enc['timestamp'].dt.hour
df_enc['month'] = df_enc['timestamp'].dt.month
df_enc['day_of_week'] = df_enc['timestamp'].dt.dayofweek

# Label-encode weather and intersection
weather_map = {'Clear': 0, 'Rain': 1, 'Snow': 2, 'Fog': 3}
df_enc['weather_enc'] = df_enc['weather'].map(weather_map)

intersection_map = {name: i for i, name in enumerate(df_enc['intersection_id'].unique())}
df_enc['intersection_enc'] = df_enc['intersection_id'].map(intersection_map)

corr_cols = ['vehicle_count', 'avg_speed_kmh', 'temperature_c', 'congestion_level',
             'is_weekend', 'is_peak_hour', 'accident_occurred',
             'hour', 'month', 'day_of_week', 'weather_enc', 'intersection_enc']

corr_matrix = df_enc[corr_cols].corr()

fig, ax = plt.subplots(figsize=(14, 11), facecolor=DARK_BG)
ax.set_facecolor(CARD_BG)
fig.suptitle("Correlation Heatmap - All Features (with Encoded Categoricals)",
             color=TEXT_COLOR, fontsize=18, fontweight='bold', y=0.97)

mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
cmap = sns.diverging_palette(230, 0, s=90, l=45, as_cmap=True)

sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f', cmap=cmap,
            center=0, vmin=-1, vmax=1,
            square=True, linewidths=0.8, linecolor=DARK_BG,
            cbar_kws={'shrink': 0.75, 'label': 'Pearson r'},
            annot_kws={'size': 9, 'color': TEXT_COLOR},
            ax=ax)

ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', color=TEXT_COLOR, fontsize=10)
ax.set_yticklabels(ax.get_yticklabels(), rotation=0, color=TEXT_COLOR, fontsize=10)
cbar = ax.collections[0].colorbar
cbar.ax.tick_params(colors=TEXT_COLOR)
cbar.set_label('Pearson r', color=TEXT_COLOR, fontsize=11)

plt.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(OUTPUT_DIR / "3_correlation_heatmap.png", dpi=180, facecolor=DARK_BG, bbox_inches='tight')
plt.close(fig)
print("   -> Saved: 3_correlation_heatmap.png")


# ==============================================================
# 4. CATEGORICAL ENCODING -- Value Distributions
# ==============================================================
print("[4/5] Categorical Encoding ...")
fig, axes = plt.subplots(2, 3, figsize=(20, 13), facecolor=DARK_BG)
fig.suptitle("Categorical Feature Analysis - Distribution & Encoding",
             color=TEXT_COLOR, fontsize=20, fontweight='bold', y=0.98)

# 4a) Intersection distribution
ax = axes[0][0]
ax.set_facecolor(CARD_BG)
counts = df['intersection_id'].value_counts()
bars = ax.barh(counts.index, counts.values, color=PALETTE[:len(counts)], edgecolor='none', height=0.6)
for bar, val in zip(bars, counts.values):
    ax.text(val + 50, bar.get_y() + bar.get_height()/2, f'{val:,}',
            va='center', color=TEXT_COLOR, fontsize=10, fontweight='bold')
ax.set_title('Intersection ID', color=TEXT_COLOR, fontsize=14, fontweight='bold')
ax.set_xlabel('Count', color=TEXT_COLOR)
ax.tick_params(colors=TEXT_COLOR, labelsize=9)
ax.grid(axis='x', color=GRID_COLOR, alpha=0.3)
for spine in ax.spines.values():
    spine.set_color(GRID_COLOR)

# 4b) Weather distribution
ax = axes[0][1]
ax.set_facecolor(CARD_BG)
weather_colors = {'Clear': ACCENT_AMBER, 'Rain': ACCENT_BLUE, 'Snow': '#E0E0E0', 'Fog': ACCENT_PURPLE}
counts = df['weather'].value_counts()
wedges, texts, autotexts = ax.pie(counts.values, labels=counts.index, autopct='%1.1f%%',
       colors=[weather_colors.get(w, ACCENT_CYAN) for w in counts.index],
       textprops={'color': TEXT_COLOR, 'fontsize': 11},
       wedgeprops={'edgecolor': DARK_BG, 'linewidth': 2},
       startangle=90)
for t in autotexts:
    t.set_fontsize(10)
    t.set_fontweight('bold')
ax.set_title('Weather Distribution', color=TEXT_COLOR, fontsize=14, fontweight='bold')

# 4c) is_weekend
ax = axes[0][2]
ax.set_facecolor(CARD_BG)
counts = df['is_weekend'].value_counts().sort_index()
labels = ['Weekday (0)', 'Weekend (1)']
bars = ax.bar(labels, counts.values, color=[ACCENT_BLUE, ACCENT_PINK],
              edgecolor='none', width=0.5)
for bar, val in zip(bars, counts.values):
    ax.text(bar.get_x() + bar.get_width()/2, val + 200, f'{val:,}',
            ha='center', color=TEXT_COLOR, fontsize=11, fontweight='bold')
ax.set_title('is_weekend', color=TEXT_COLOR, fontsize=14, fontweight='bold')
ax.set_ylabel('Count', color=TEXT_COLOR)
ax.tick_params(colors=TEXT_COLOR, labelsize=10)
ax.grid(axis='y', color=GRID_COLOR, alpha=0.3)
for spine in ax.spines.values():
    spine.set_color(GRID_COLOR)

# 4d) is_peak_hour
ax = axes[1][0]
ax.set_facecolor(CARD_BG)
counts = df['is_peak_hour'].value_counts().sort_index()
labels = ['Off-peak (0)', 'Peak (1)']
bars = ax.bar(labels, counts.values, color=[ACCENT_GREEN, ACCENT_AMBER],
              edgecolor='none', width=0.5)
for bar, val in zip(bars, counts.values):
    ax.text(bar.get_x() + bar.get_width()/2, val + 200, f'{val:,}',
            ha='center', color=TEXT_COLOR, fontsize=11, fontweight='bold')
ax.set_title('is_peak_hour', color=TEXT_COLOR, fontsize=14, fontweight='bold')
ax.set_ylabel('Count', color=TEXT_COLOR)
ax.tick_params(colors=TEXT_COLOR, labelsize=10)
ax.grid(axis='y', color=GRID_COLOR, alpha=0.3)
for spine in ax.spines.values():
    spine.set_color(GRID_COLOR)

# 4e) accident_occurred
ax = axes[1][1]
ax.set_facecolor(CARD_BG)
counts = df['accident_occurred'].value_counts().sort_index()
labels = ['No (0)', 'Yes (1)']
bars = ax.bar(labels, counts.values, color=[ACCENT_GREEN, ACCENT_PINK],
              edgecolor='none', width=0.5)
for bar, val in zip(bars, counts.values):
    ax.text(bar.get_x() + bar.get_width()/2, val + 200, f'{val:,}',
            ha='center', color=TEXT_COLOR, fontsize=11, fontweight='bold')
ax.set_title('accident_occurred', color=TEXT_COLOR, fontsize=14, fontweight='bold')
ax.set_ylabel('Count', color=TEXT_COLOR)
ax.tick_params(colors=TEXT_COLOR, labelsize=10)
ax.grid(axis='y', color=GRID_COLOR, alpha=0.3)
for spine in ax.spines.values():
    spine.set_color(GRID_COLOR)

# 4f) Encoding table summary
ax = axes[1][2]
ax.set_facecolor(CARD_BG)
ax.axis('off')

table_data = [
    ["Feature", "Encoding", "Values"],
    ["intersection_id", "Label Enc.", f"{df['intersection_id'].nunique()} classes"],
    ["weather", "Label Enc.", "Clear=0, Rain=1, Snow=2, Fog=3"],
    ["is_weekend", "Binary", "0 = Weekday, 1 = Weekend"],
    ["is_peak_hour", "Binary", "0 = Off-peak, 1 = Peak"],
    ["accident_occurred", "Binary", "0 = No, 1 = Yes"],
]

table = ax.table(cellText=table_data, loc='center', cellLoc='center',
                 colWidths=[0.3, 0.25, 0.45])
table.auto_set_font_size(False)
table.set_fontsize(10)
for (row, col), cell in table.get_celld().items():
    cell.set_edgecolor(GRID_COLOR)
    if row == 0:
        cell.set_facecolor(ACCENT_BLUE)
        cell.set_text_props(color='white', fontweight='bold', fontsize=11)
    else:
        cell.set_facecolor(CARD_BG)
        cell.set_text_props(color=TEXT_COLOR)
    cell.set_height(0.12)

ax.set_title('Encoding Summary', color=TEXT_COLOR, fontsize=14, fontweight='bold', pad=15)

plt.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(OUTPUT_DIR / "4_categorical_encoding.png", dpi=180, facecolor=DARK_BG, bbox_inches='tight')
plt.close(fig)
print("   -> Saved: 4_categorical_encoding.png")


# ==============================================================
# 5. MISSING VALUES ANALYSIS
# ==============================================================
print("[5/5] Missing Values ...")
fig, axes = plt.subplots(1, 2, figsize=(18, 8), facecolor=DARK_BG,
                          gridspec_kw={'width_ratios': [1.2, 1]})
fig.suptitle("Missing Values Analysis",
             color=TEXT_COLOR, fontsize=20, fontweight='bold', y=0.97)

all_cols = ['timestamp', 'intersection_id', 'vehicle_count', 'avg_speed_kmh',
            'weather', 'temperature_c', 'is_weekend', 'is_peak_hour',
            'accident_occurred', 'congestion_level']

missing_counts = df[all_cols].isnull().sum()
total = len(df)
missing_pct = (missing_counts / total * 100)

# 5a) Bar chart of missing values
ax = axes[0]
ax.set_facecolor(CARD_BG)
colors = [ACCENT_GREEN if v == 0 else ACCENT_PINK for v in missing_counts.values]
bars = ax.barh(all_cols, missing_counts.values, color=colors, edgecolor='none', height=0.6)

for bar, cnt, pct in zip(bars, missing_counts.values, missing_pct.values):
    label = f'{cnt:,}  ({pct:.1f}%)' if cnt > 0 else '0  (0.0%) OK'
    ax.text(max(missing_counts.values) * 0.02 + cnt, bar.get_y() + bar.get_height()/2,
            label, va='center', color=TEXT_COLOR, fontsize=10, fontweight='bold')

ax.set_title('Missing Count per Column', color=TEXT_COLOR, fontsize=14, fontweight='bold')
ax.set_xlabel('Missing Values', color=TEXT_COLOR)
ax.tick_params(colors=TEXT_COLOR, labelsize=10)
ax.grid(axis='x', color=GRID_COLOR, alpha=0.3)
for spine in ax.spines.values():
    spine.set_color(GRID_COLOR)

# 5b) Summary statistics table
ax = axes[1]
ax.set_facecolor(CARD_BG)
ax.axis('off')

total_cells = total * len(all_cols)
total_missing = missing_counts.sum()
completeness = (1 - total_missing / total_cells) * 100

summary_data = [
    ["Metric", "Value"],
    ["Total Rows", f"{total:,}"],
    ["Total Columns", f"{len(all_cols)}"],
    ["Total Cells", f"{total_cells:,}"],
    ["Total Missing", f"{total_missing:,}"],
    ["Completeness", f"{completeness:.2f}%"],
    ["Columns with NaN", f"{(missing_counts > 0).sum()}"],
    ["Status", "No Missing Values" if total_missing == 0 else "Has Missing Data"],
]

table = ax.table(cellText=summary_data, loc='center', cellLoc='center',
                 colWidths=[0.45, 0.45])
table.auto_set_font_size(False)
table.set_fontsize(11)
for (row, col), cell in table.get_celld().items():
    cell.set_edgecolor(GRID_COLOR)
    if row == 0:
        cell.set_facecolor(ACCENT_BLUE)
        cell.set_text_props(color='white', fontweight='bold', fontsize=12)
    elif row == len(summary_data) - 1:
        cell.set_facecolor('#1b3a1b' if total_missing == 0 else '#3a1b1b')
        cell.set_text_props(color=ACCENT_GREEN if total_missing == 0 else ACCENT_PINK,
                            fontweight='bold', fontsize=12)
    else:
        cell.set_facecolor(CARD_BG)
        cell.set_text_props(color=TEXT_COLOR)
    cell.set_height(0.09)

ax.set_title('Dataset Completeness Summary', color=TEXT_COLOR, fontsize=14, fontweight='bold', pad=15)

plt.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig(OUTPUT_DIR / "5_missing_values.png", dpi=180, facecolor=DARK_BG, bbox_inches='tight')
plt.close(fig)
print("   -> Saved: 5_missing_values.png")


# -- Done -------------------------------------------------------
print()
print("=" * 60)
print(f"[DONE] All 5 charts saved to: {OUTPUT_DIR.resolve()}")
print("=" * 60)
