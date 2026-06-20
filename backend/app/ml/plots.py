import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

def set_style():
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({'font.size': 12, 'figure.figsize': (10, 6)})

def plot_prediction_vs_actual(y_true, y_pred_dict, save_path):
    set_style()
    plt.figure()
    plt.plot(y_true, label='Actual Traffic', color='black', linewidth=2)
    
    colors = sns.color_palette("husl", len(y_pred_dict))
    for (model_name, y_pred), color in zip(y_pred_dict.items(), colors):
        plt.plot(y_pred, label=f'{model_name} Prediction', linestyle='--', alpha=0.8, color=color)
        
    plt.title("Actual vs Predicted Traffic Congestion")
    plt.xlabel("Time Steps (15 min intervals)")
    plt.ylabel("Congestion Level (0-100)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

def plot_model_comparison(metrics_df, metric_name, save_path):
    set_style()
    plt.figure()
    
    # metrics_df has columns: 'Model', 'Horizon_min', 'MAE', 'RMSE', 'MAPE'
    ax = sns.barplot(data=metrics_df, x='Model', y=metric_name, hue='Horizon_min')
    
    plt.title(f"Model Comparison by {metric_name}")
    plt.ylabel(metric_name)
    plt.xlabel("Model")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

def plot_lstm_loss(loss_history, save_path):
    set_style()
    plt.figure()
    plt.plot(loss_history, marker='o', color='blue', linewidth=2)
    plt.title("LSTM Training Loss Curve")
    plt.xlabel("Epochs")
    plt.ylabel("MSE Loss")
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
