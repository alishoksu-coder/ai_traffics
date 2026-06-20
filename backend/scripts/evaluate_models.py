import os
import sys
import pandas as pd
import numpy as np

# Add backend directory to sys.path so we can import app modules
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.ml.baselines import NaiveForecast, MovingAverageForecast, LinearRegressionForecast, RandomForestForecast
from app.ml.lstm_model import TrafficLSTM
from app.ml.metrics import mae_rmse, mape
from app.ml.plots import plot_prediction_vs_actual, plot_model_comparison, plot_lstm_loss

PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, ".."))
DATASET_PATH = os.path.join(PROJECT_ROOT, "yesil_traffic_history_dataset.csv")
REPORTS_DIR = os.path.join(BACKEND_DIR, "reports")

def main():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    print("Loading dataset...")
    if not os.path.exists(DATASET_PATH):
        print(f"Error: Dataset not found at {DATASET_PATH}")
        return
        
    df = pd.read_csv(DATASET_PATH)
    
    # Preprocessing
    df['dt'] = pd.to_datetime(df['timestamp'])
    df['value'] = df['congestion_level'] * 100.0
    
    # Filter to one intersection to evaluate pure time series performance
    intersection_id = df['intersection_id'].iloc[0]
    df = df[df['intersection_id'] == intersection_id].sort_values('dt')
    
    print(f"Total rows for {intersection_id}: {len(df)}")
    
    # Train / Test split (80/20)
    split_idx = int(len(df) * 0.8)
    train_df = df.iloc[:split_idx].copy()
    test_df = df.iloc[split_idx:].copy()
    print(f"Train size: {len(train_df)}, Test size: {len(test_df)}")
    
    # Initialize Models
    models = {
        "Naive": NaiveForecast(),
        "Moving Average (1h)": MovingAverageForecast(window_size=4),
        "Linear Regression": LinearRegressionForecast(),
        "Random Forest": RandomForestForecast(),
    }
    
    # Train baselines
    print("Training baselines...")
    for name, model in models.items():
        print(f"  Training {name}...")
        model.fit(train_df)
        
    # Train LSTM
    print("Training LSTM...")
    lstm_model = TrafficLSTM(model_path="data/lstm_eval.pth")
    # For evaluation, we force a quick retrain on train_df
    lstm_model.train_on_dataset(df=train_df, epochs=10, batch_size=32)
    models["LSTM"] = lstm_model
    
    if hasattr(lstm_model, 'loss_history') and lstm_model.loss_history:
        plot_lstm_loss(lstm_model.loss_history, os.path.join(REPORTS_DIR, "lstm_loss_curve.png"))
        print("Saved lstm_loss_curve.png")
    
    # Evaluation configuration
    horizons = {"30m": 2, "60m": 4} # 1 step = 15 min
    results = []
    
    # We will also collect predictions for a visual plot for 60m horizon
    plot_actuals = []
    plot_preds = {name: [] for name in models.keys()}
    
    # Rolling origin evaluation on Test set
    # We use a sliding window of recent data to predict the future
    print("Evaluating on test set...")
    lookback = 24 # Use last 6 hours as context
    
    # Pre-extract values for fast access
    test_dts = test_df['dt'].values
    test_vals = test_df['value'].values
    
    for h_name, steps_ahead in horizons.items():
        print(f"Evaluating horizon {h_name}...")
        
        y_true_all = []
        y_preds_all = {name: [] for name in models.keys()}
        
        for i in range(lookback, len(test_df) - steps_ahead):
            # The "current" time is i
            recent_data = test_df.iloc[i-lookback:i+1].copy()
            
            # The target time is i + steps_ahead
            target_val = test_vals[i + steps_ahead]
            y_true_all.append(target_val)
            
            # Predict
            for name, model in models.items():
                preds = model.predict_future(recent_data, steps_ahead=steps_ahead)
                pred_val = preds[-1] # We want the value exactly at steps_ahead
                y_preds_all[name].append(pred_val)
                
                # If evaluating 60m, save for plotting (only need to do this once per step)
                if h_name == "60m":
                    plot_preds[name].append(pred_val)
                    
        if h_name == "60m":
            plot_actuals = y_true_all.copy()
            
        # Calculate Metrics
        for name in models.keys():
            m_rmse = mae_rmse(y_true_all, y_preds_all[name])
            m_mape = mape(y_true_all, y_preds_all[name])
            
            results.append({
                "Model": name,
                "Horizon_min": 30 if h_name == "30m" else 60,
                "MAE": m_rmse["mae"],
                "RMSE": m_rmse["rmse"],
                "MAPE": m_mape["mape"]
            })
            
    # Save metrics
    results_df = pd.DataFrame(results)
    metrics_path = os.path.join(REPORTS_DIR, "metrics_summary.csv")
    results_df.to_csv(metrics_path, index=False)
    print(f"Saved {metrics_path}")
    
    # Generate Plots
    print("Generating plots...")
    # 1. Actual vs Predicted (take a slice of 100 points for readability)
    slice_end = min(200, len(plot_actuals))
    sliced_actuals = plot_actuals[:slice_end]
    sliced_preds = {name: preds[:slice_end] for name, preds in plot_preds.items()}
    plot_prediction_vs_actual(sliced_actuals, sliced_preds, os.path.join(REPORTS_DIR, "prediction_vs_actual.png"))
    
    # 2. Model comparison MAE
    plot_model_comparison(results_df, "MAE", os.path.join(REPORTS_DIR, "model_comparison_mae.png"))
    
    # 3. Model comparison RMSE
    plot_model_comparison(results_df, "RMSE", os.path.join(REPORTS_DIR, "model_comparison_rmse.png"))
    
    print("Evaluation completed successfully.")

if __name__ == "__main__":
    main()
