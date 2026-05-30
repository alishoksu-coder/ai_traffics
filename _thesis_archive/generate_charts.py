"""
Task 7: Generate MAE/RMSE bar chart for diploma.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Data from thesis testing results
models = ['Naive', 'SMA', 'EMA', 'Trend LR']

mae_30 = [8.47, 7.12, 6.53, 5.34]
rmse_30 = [10.21, 8.89, 8.01, 6.78]
mae_60 = [12.35, 10.56, 9.87, 8.15]
rmse_60 = [14.67, 12.88, 11.92, 10.23]

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

x = np.arange(len(models))
width = 0.35

# 30 min horizon
ax1 = axes[0]
bars1 = ax1.bar(x - width/2, mae_30, width, label='MAE', color='#2196F3', edgecolor='white')
bars2 = ax1.bar(x + width/2, rmse_30, width, label='RMSE', color='#FF5722', edgecolor='white')
ax1.set_xlabel('Болжау моделі', fontsize=12)
ax1.set_ylabel('Қателік мәні', fontsize=12)
ax1.set_title('30 минуттық болжам горизонты', fontsize=14, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(models, fontsize=11)
ax1.legend(fontsize=11)
ax1.set_ylim(0, 16)
ax1.grid(axis='y', alpha=0.3)
for bar in bars1:
    ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.2,
             f'{bar.get_height():.2f}', ha='center', va='bottom', fontsize=9)
for bar in bars2:
    ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.2,
             f'{bar.get_height():.2f}', ha='center', va='bottom', fontsize=9)

# 60 min horizon
ax2 = axes[1]
bars3 = ax2.bar(x - width/2, mae_60, width, label='MAE', color='#2196F3', edgecolor='white')
bars4 = ax2.bar(x + width/2, rmse_60, width, label='RMSE', color='#FF5722', edgecolor='white')
ax2.set_xlabel('Болжау моделі', fontsize=12)
ax2.set_ylabel('Қателік мәні', fontsize=12)
ax2.set_title('60 минуттық болжам горизонты', fontsize=14, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(models, fontsize=11)
ax2.legend(fontsize=11)
ax2.set_ylim(0, 18)
ax2.grid(axis='y', alpha=0.3)
for bar in bars3:
    ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.2,
             f'{bar.get_height():.2f}', ha='center', va='bottom', fontsize=9)
for bar in bars4:
    ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.2,
             f'{bar.get_height():.2f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('mae_rmse_chart.png', dpi=300, bbox_inches='tight')
print("Task 7 done: mae_rmse_chart.png saved.")
plt.close()
