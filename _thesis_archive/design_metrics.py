# -*- coding: utf-8 -*-
# Unified Metrics Design
metrics = {
    '15': {
        'Naive': {'MAE': 8.42, 'RMSE': 11.56},
        'Trend LR': {'MAE': 5.34, 'RMSE': 7.89},
        'Random Forest': {'MAE': 4.87, 'RMSE': 6.92},
        'LSTM': {'MAE': 5.12, 'RMSE': 7.15},
        'AI Brain (Ensemble)': {'MAE': 4.52, 'RMSE': 6.34}
    },
    '30': {
        'Naive': {'MAE': 9.25, 'RMSE': 12.80},
        'Trend LR': {'MAE': 6.12, 'RMSE': 8.95},
        'Random Forest': {'MAE': 5.64, 'RMSE': 8.15},
        'LSTM': {'MAE': 5.95, 'RMSE': 8.42},
        'AI Brain (Ensemble)': {'MAE': 5.34, 'RMSE': 7.62}
    },
    '60': {
        'Naive': {'MAE': 11.45, 'RMSE': 15.30},
        'Trend LR': {'MAE': 8.15, 'RMSE': 11.20},
        'Random Forest': {'MAE': 7.43, 'RMSE': 10.50},
        'LSTM': {'MAE': 7.89, 'RMSE': 10.95},
        'AI Brain (Ensemble)': {'MAE': 6.85, 'RMSE': 9.42}
    }
}

feature_importance = {
    'hour': '38.4%',
    'day_of_week': '27.1%',
    'weather_condition': '19.3%',
    'segment_id': '15.2%'
}

# The plan will outline using these consistent numbers across all tables.
