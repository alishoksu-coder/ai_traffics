"""
=============================================================
ML Model Analysis - AI Traffic Project
yesil_traffic_history_dataset.csv
=============================================================
RandomForestRegressor (n_estimators=50, random_state=42)
- Train/Test split
- Accuracy / R2 / MAE / RMSE / Z-Score
- Confusion Matrix (congestion_level -> classes)
=============================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    confusion_matrix, classification_report, accuracy_score,
    precision_score, recall_score, f1_score
)
from sklearn.preprocessing import LabelEncoder
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 0. CONFIG
# ============================================================
DATASET_PATH = "yesil_traffic_history_dataset.csv"
OUTPUT_DIR = "ml_analysis_charts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Dark theme
plt.rcParams.update({
    'figure.facecolor': '#1a1a2e',
    'axes.facecolor': '#16213e',
    'axes.edgecolor': '#e94560',
    'axes.labelcolor': '#e0e0e0',
    'xtick.color': '#e0e0e0',
    'ytick.color': '#e0e0e0',
    'text.color': '#e0e0e0',
    'font.size': 10,
    'axes.grid': True,
    'grid.color': '#2a2a4a',
    'grid.alpha': 0.3,
})

# ============================================================
# 1. LOAD & PREPARE DATA
# ============================================================
print("=" * 60)
print("  ML MODEL ANALYSIS")
print("  Dataset: yesil_traffic_history_dataset.csv")
print("  Model: RandomForestRegressor (n_estimators=50)")
print("=" * 60)

df = pd.read_csv(DATASET_PATH).sample(n=20000, random_state=42)
print(f"\nDataset: {df.shape[0]} rows x {df.shape[1]} columns")

# Encode categoricals
le_intersection = LabelEncoder()
le_weather = LabelEncoder()
df['intersection_enc'] = le_intersection.fit_transform(df['intersection_id'])
df['weather_enc'] = le_weather.fit_transform(df['weather'])

# Parse timestamp
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['hour'] = df['timestamp'].dt.hour
df['month'] = df['timestamp'].dt.month
df['day_of_week'] = df['timestamp'].dt.dayofweek

# Features & Target
feature_cols = [
    'intersection_enc', 'vehicle_count', 'avg_speed_kmh',
    'weather_enc', 'temperature_c', 'is_weekend',
    'is_peak_hour', 'accident_occurred', 'hour', 'day_of_week', 'month'
]
X = df[feature_cols]
y = df['congestion_level']

# ============================================================
# 2. TRAIN / TEST SPLIT
# ============================================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\nTrain set: {X_train.shape[0]} samples ({X_train.shape[0]/len(X)*100:.0f}%)")
print(f"Test set:  {X_test.shape[0]} samples ({X_test.shape[0]/len(X)*100:.0f}%)")

# ============================================================
# 3. TRAIN MODEL
# ============================================================
model = RandomForestRegressor(n_estimators=50, max_depth=15, n_jobs=1, random_state=42)
model.fit(X_train, y_train)
print("\nModel trained: RandomForestRegressor(n_estimators=50, max_depth=15, random_state=42)")

# Predictions
y_pred = model.predict(X_test)

# ============================================================
# 4. REGRESSION METRICS
# ============================================================
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mape = np.mean(np.abs((y_test - y_pred) / (y_test + 1e-8))) * 100
accuracy_like = (1 - mae / (y_test.max() - y_test.min())) * 100

print(f"\n--- Regression Metrics ---")
print(f"R2 Score:      {r2:.4f}")
print(f"MAE:           {mae:.4f}")
print(f"RMSE:          {rmse:.4f}")
print(f"MAPE:          {mape:.2f}%")
print(f"Accuracy-like: {accuracy_like:.2f}%")

# ============================================================
# 5. Z-SCORE ANALYSIS
# ============================================================
residuals = y_test.values - y_pred
z_scores = (residuals - residuals.mean()) / residuals.std()
outlier_count = np.sum(np.abs(z_scores) > 2)
normal_count = np.sum(np.abs(z_scores) <= 2)

print(f"\n--- Z-Score Analysis ---")
print(f"Mean residual: {residuals.mean():.6f}")
print(f"Std residual:  {residuals.std():.6f}")
print(f"Outliers (|Z|>2): {outlier_count} ({outlier_count/len(z_scores)*100:.1f}%)")
print(f"Normal (|Z|<=2):  {normal_count} ({normal_count/len(z_scores)*100:.1f}%)")

# ============================================================
# 6. CLASSIFICATION FOR CONFUSION MATRIX
# ============================================================
def level_to_class(val):
    if val < 0.3:
        return "Low"
    elif val < 0.6:
        return "Medium"
    elif val < 0.8:
        return "High"
    else:
        return "Critical"

y_test_classes = [level_to_class(v) for v in y_test]
y_pred_classes = [level_to_class(v) for v in y_pred]

class_labels = ["Low", "Medium", "High", "Critical"]
cm = confusion_matrix(y_test_classes, y_pred_classes, labels=class_labels)
cls_accuracy = accuracy_score(y_test_classes, y_pred_classes)
cls_precision = precision_score(y_test_classes, y_pred_classes, labels=class_labels, average='weighted', zero_division=0)
cls_recall = recall_score(y_test_classes, y_pred_classes, labels=class_labels, average='weighted', zero_division=0)
cls_f1 = f1_score(y_test_classes, y_pred_classes, labels=class_labels, average='weighted', zero_division=0)

# ============================================================
# CHART 1: TRAIN/TEST SPLIT VISUALIZATION
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle("1. Train / Test Split (80% / 20%)", fontsize=18, fontweight='bold', color='#e94560')

# Pie chart
sizes = [len(X_train), len(X_test)]
colors_pie = ['#00d2ff', '#e94560']
explode = (0.05, 0.05)
wedges, texts, autotexts = axes[0].pie(
    sizes, explode=explode, labels=['Train (80%)', 'Test (20%)'],
    autopct='%1.1f%%', colors=colors_pie, startangle=90,
    textprops={'fontsize': 11, 'fontweight': 'bold'}
)
for t in autotexts:
    t.set_color('white')
axes[0].set_title(f"Train: {len(X_train)} | Test: {len(X_test)}", fontsize=12, color='#00d2ff')

# Target distribution comparison
axes[1].hist(y_train, bins=30, alpha=0.7, color='#00d2ff', label=f'Train (n={len(y_train)})', edgecolor='white', linewidth=0.5)
axes[1].hist(y_test, bins=30, alpha=0.7, color='#e94560', label=f'Test (n={len(y_test)})', edgecolor='white', linewidth=0.5)
axes[1].set_xlabel("congestion_level", fontsize=11)
axes[1].set_ylabel("Count", fontsize=11)
axes[1].set_title("Target Distribution", fontsize=12, color='#00d2ff')
axes[1].legend(fontsize=10)

# Stats table
stats_data = [
    ["Metric", "Train", "Test"],
    ["Samples", f"{len(X_train):,}", f"{len(X_test):,}"],
    ["Mean", f"{y_train.mean():.4f}", f"{y_test.mean():.4f}"],
    ["Std", f"{y_train.std():.4f}", f"{y_test.std():.4f}"],
    ["Min", f"{y_train.min():.3f}", f"{y_test.min():.3f}"],
    ["Max", f"{y_train.max():.3f}", f"{y_test.max():.3f}"],
    ["Median", f"{y_train.median():.4f}", f"{y_test.median():.4f}"],
]
axes[2].axis('off')
tbl = axes[2].table(cellText=stats_data, cellLoc='center', loc='center', colWidths=[0.3, 0.35, 0.35])
tbl.auto_set_font_size(False)
tbl.set_fontsize(10)
tbl.scale(1.1, 1.8)
for (row, col), cell in tbl.get_celld().items():
    cell.set_edgecolor('#4a4a7a')
    if row == 0:
        cell.set_facecolor('#e94560')
        cell.get_text().set_color('white')
        cell.get_text().set_fontweight('bold')
    else:
        cell.set_facecolor('#1e2a4a')
        cell.get_text().set_color('#e0e0e0')
axes[2].set_title("Train vs Test Statistics", fontsize=12, color='#00d2ff')

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "1_train_test_split.png"), dpi=100, bbox_inches='tight')
plt.close()

# ============================================================
# CHART 2: MODEL ACCURACY & REGRESSION METRICS
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle("2. Model Performance - RandomForestRegressor", fontsize=18, fontweight='bold', color='#e94560')

# Actual vs Predicted scatter
sample_idx = np.random.RandomState(42).choice(len(y_test), size=min(3000, len(y_test)), replace=False)
y_test_sample = y_test.values[sample_idx]
y_pred_sample = y_pred[sample_idx]
axes[0].scatter(y_test_sample, y_pred_sample, alpha=0.3, s=8, c='#00d2ff', edgecolors='none')
axes[0].plot([0, 1], [0, 1], '--', color='#e94560', linewidth=2, label='Ideal (y=x)')
axes[0].set_xlabel("Actual congestion_level", fontsize=11)
axes[0].set_ylabel("Predicted congestion_level", fontsize=11)
axes[0].set_title(f"Actual vs Predicted (R2={r2:.4f})", fontsize=12, color='#00d2ff')
axes[0].legend(fontsize=9)
axes[0].set_xlim(-0.05, 1.05)
axes[0].set_ylim(-0.05, 1.05)

# Metrics bar chart
metric_names = ['R2\nScore', 'Accuracy\n(Custom)', 'Precision', 'Recall', 'F1 Score']
metric_values = [r2, accuracy_like / 100, cls_precision, cls_recall, cls_f1]
colors_bar = ['#00d2ff', '#0facf0', '#e94560', '#ff6b6b', '#ffd93d']

bars = axes[1].bar(metric_names, metric_values, color=colors_bar, edgecolor='white', linewidth=0.5)
for bar, val in zip(bars, metric_values):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                 f"{val:.3f}", ha='center', fontsize=9, fontweight='bold', color='#e0e0e0')
axes[1].set_ylim(0, 1.15)
axes[1].set_ylabel("Score", fontsize=11)
axes[1].set_title("Key Metrics", fontsize=12, color='#00d2ff')

# Error metrics table
err_data = [
    ["Metric", "Value", "Description"],
    ["R2 Score", f"{r2:.4f}", "Model accuracy"],
    ["MAE", f"{mae:.4f}", "Mean absolute err"],
    ["RMSE", f"{rmse:.4f}", "Root mean sq err"],
    ["MAPE", f"{mape:.2f}%", "Mean % error"],
    ["Accuracy", f"{accuracy_like:.2f}%", "1 - MAE/range"],
    ["Cls Acc.", f"{cls_accuracy*100:.2f}%", "Class prediction"],
    ["F1 Score", f"{cls_f1:.4f}", "Harmonic mean"],
]
axes[2].axis('off')
tbl2 = axes[2].table(cellText=err_data, cellLoc='center', loc='center', colWidths=[0.3, 0.25, 0.45])
tbl2.auto_set_font_size(False)
tbl2.set_fontsize(9)
tbl2.scale(1.1, 1.8)
for (row, col), cell in tbl2.get_celld().items():
    cell.set_edgecolor('#4a4a7a')
    if row == 0:
        cell.set_facecolor('#e94560')
        cell.get_text().set_color('white')
        cell.get_text().set_fontweight('bold')
    else:
        cell.set_facecolor('#1e2a4a')
        cell.get_text().set_color('#e0e0e0')
axes[2].set_title("Detailed Metrics", fontsize=12, color='#00d2ff')

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "2_model_accuracy.png"), dpi=100, bbox_inches='tight')
plt.close()

# ============================================================
# CHART 3: Z-SCORE ANALYSIS
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle("3. Z-Score Analysis (Residual Outlier Detection)", fontsize=18, fontweight='bold', color='#e94560')

axes[0].hist(z_scores, bins=80, color='#00d2ff', edgecolor='white', linewidth=0.3, alpha=0.8)
axes[0].axvline(x=-2, color='#e94560', linestyle='--', linewidth=2, label='Z = -2')
axes[0].axvline(x=2, color='#e94560', linestyle='--', linewidth=2, label='Z = +2')
axes[0].axvline(x=0, color='#ffd93d', linestyle='-', linewidth=2)
axes[0].fill_betweenx([0, axes[0].get_ylim()[1] if axes[0].get_ylim()[1] > 0 else 500], -2, 2, alpha=0.1, color='#00ff88')
axes[0].set_xlabel("Z-Score", fontsize=11)
axes[0].set_ylabel("Frequency", fontsize=11)
axes[0].set_title("Z-Score Distribution", fontsize=12, color='#00d2ff')

z_colors = np.where(np.abs(z_scores) > 2, '#e94560', '#00d2ff')
axes[1].scatter(y_test.values, z_scores, c=z_colors, s=5, alpha=0.4, edgecolors='none')
axes[1].axhline(y=-2, color='#e94560', linestyle='--', linewidth=1.5)
axes[1].axhline(y=2, color='#e94560', linestyle='--', linewidth=1.5)
axes[1].axhline(y=0, color='#ffd93d', linestyle='-', linewidth=1)
axes[1].set_xlabel("Actual congestion", fontsize=11)
axes[1].set_ylabel("Z-Score", fontsize=11)
axes[1].set_title("Z-Score vs Actual Value", fontsize=12, color='#00d2ff')

z_data = [
    ["Metric", "Value"],
    ["Mean Res.", f"{residuals.mean():.6f}"],
    ["Std Res.", f"{residuals.std():.6f}"],
    ["Normal |Z|<=2", f"{normal_count} ({normal_count/len(z_scores)*100:.1f}%)"],
    ["Outliers |Z|>2", f"{outlier_count} ({outlier_count/len(z_scores)*100:.1f}%)"],
]
axes[2].axis('off')
tbl3 = axes[2].table(cellText=z_data, cellLoc='center', loc='center', colWidths=[0.4, 0.5])
tbl3.auto_set_font_size(False)
tbl3.set_fontsize(10)
tbl3.scale(1.1, 2.0)
for (row, col), cell in tbl3.get_celld().items():
    cell.set_edgecolor('#4a4a7a')
    if row == 0:
        cell.set_facecolor('#e94560')
        cell.get_text().set_color('white')
        cell.get_text().set_fontweight('bold')
    else:
        cell.set_facecolor('#1e2a4a')
        cell.get_text().set_color('#e0e0e0')
axes[2].set_title("Z-Score Summary", fontsize=12, color='#00d2ff')

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "3_zscore_analysis.png"), dpi=100, bbox_inches='tight')
plt.close()

# ============================================================
# CHART 4: CONFUSION MATRIX
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(15, 5))
fig.suptitle("4. Confusion Matrix - Congestion Classes", fontsize=18, fontweight='bold', color='#e94560')

im = axes[0].imshow(cm, interpolation='nearest', cmap='YlOrRd')
axes[0].set_xticks(range(len(class_labels)))
axes[0].set_yticks(range(len(class_labels)))
axes[0].set_xticklabels(class_labels, fontsize=10)
axes[0].set_yticklabels(class_labels, fontsize=10)
axes[0].set_xlabel("Predicted Class", fontsize=11, fontweight='bold')
axes[0].set_ylabel("Actual Class", fontsize=11, fontweight='bold')
axes[0].set_title(f"Confusion Matrix (Acc: {cls_accuracy*100:.2f}%)", fontsize=12, color='#00d2ff')

thresh = cm.max() / 2.0
for i in range(len(class_labels)):
    for j in range(len(class_labels)):
        val = cm[i, j]
        axes[0].text(j, i, f"{val:,}", ha="center", va="center", fontsize=12, fontweight='bold',
                     color="white" if val > thresh else "black")
fig.colorbar(im, ax=axes[0], shrink=0.8)

report = classification_report(y_test_classes, y_pred_classes, labels=class_labels, output_dict=True, zero_division=0)
report_data = [["Class", "Precision", "Recall", "F1", "Support"]]
for label in class_labels:
    r = report[label]
    report_data.append([label, f"{r['precision']:.3f}", f"{r['recall']:.3f}", f"{r['f1-score']:.3f}", f"{int(r['support']):,}"])
report_data.append(["Avg", f"{report['weighted avg']['precision']:.3f}", f"{report['weighted avg']['recall']:.3f}", f"{report['weighted avg']['f1-score']:.3f}", f"{int(report['weighted avg']['support']):,}"])

axes[1].axis('off')
tbl4 = axes[1].table(cellText=report_data, cellLoc='center', loc='center', colWidths=[0.25, 0.18, 0.18, 0.18, 0.2])
tbl4.auto_set_font_size(False)
tbl4.set_fontsize(10)
tbl4.scale(1.1, 2.0)
for (row, col), cell in tbl4.get_celld().items():
    cell.set_edgecolor('#4a4a7a')
    if row == 0:
        cell.set_facecolor('#e94560')
        cell.get_text().set_color('white')
        cell.get_text().set_fontweight('bold')
    else:
        cell.set_facecolor('#1e2a4a')
        cell.get_text().set_color('#e0e0e0')
axes[1].set_title("Classification Report", fontsize=12, color='#00d2ff')

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "4_confusion_matrix.png"), dpi=100, bbox_inches='tight')
plt.close()

# ============================================================
# CHART 5: FEATURE IMPORTANCE
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(15, 5))
fig.suptitle("5. Feature Importance - RandomForestRegressor", fontsize=18, fontweight='bold', color='#e94560')

importances = model.feature_importances_
sorted_idx = np.argsort(importances)
sorted_features = [feature_cols[i] for i in sorted_idx]
sorted_importances = importances[sorted_idx]

colors_imp = plt.cm.RdYlGn(np.linspace(0.2, 0.9, len(sorted_features)))
bars = axes[0].barh(sorted_features, sorted_importances, color=colors_imp, edgecolor='white', linewidth=0.5)
for bar, val in zip(bars, sorted_importances):
    axes[0].text(val + 0.005, bar.get_y() + bar.get_height()/2, f"{val:.4f}", va='center', fontsize=9, color='#e0e0e0')
axes[0].set_xlabel("Importance", fontsize=11)
axes[0].set_title("Feature Importance (MDI)", fontsize=12, color='#00d2ff')

imp_data = [["Rank", "Feature", "Importance"]]
for rank, idx in enumerate(reversed(sorted_idx), 1):
    imp_data.append([f"#{rank}", feature_cols[idx], f"{importances[idx]*100:.2f}%"])

axes[1].axis('off')
tbl5 = axes[1].table(cellText=imp_data, cellLoc='center', loc='center', colWidths=[0.15, 0.5, 0.35])
tbl5.auto_set_font_size(False)
tbl5.set_fontsize(10)
tbl5.scale(1.1, 1.6)
for (row, col), cell in tbl5.get_celld().items():
    cell.set_edgecolor('#4a4a7a')
    if row == 0:
        cell.set_facecolor('#e94560')
        cell.get_text().set_color('white')
        cell.get_text().set_fontweight('bold')
    else:
        cell.set_facecolor('#1e2a4a')
        cell.get_text().set_color('#e0e0e0')
axes[1].set_title("Feature Ranking", fontsize=12, color='#00d2ff')

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "5_feature_importance.png"), dpi=100, bbox_inches='tight')
plt.close()
