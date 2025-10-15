import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, r2_score
from scipy.stats import pearsonr
import base64
import json
from io import BytesIO
from pathlib import Path
import plotly.express as px
import plotly.io as pio, json



def nse(observed, simulated):
    return 1 - np.sum((observed - simulated) ** 2) / np.sum((observed - np.mean(observed)) ** 2)

def kge(observed, simulated):
    r, _ = pearsonr(observed, simulated)
    beta = np.mean(simulated) / np.mean(observed)
    alpha = np.std(simulated) / np.std(observed)
    return 1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)

def mse(observed, simulated):
    return mean_squared_error(observed, simulated)

def rmse(observed, simulated):
    return np.sqrt(mse(observed, simulated))

def calculate_metrics(observed, simulated):
    return {
        'NSE': nse(observed, simulated),
        'KGE': kge(observed, simulated),
        'R²': r2_score(observed, simulated),
        'MSE': mse(observed, simulated),
        'RMSE': rmse(observed, simulated)
    }


def load_data(simulation_path: Path,
    observation_path: Path | None = None,
    *,
    index_column: str,
    observation_column: str,
    simulation_column: str) -> dict[str, pd.DataFrame]:
    data = {}
    
    sim_files = list(simulation_path.parent.glob(simulation_path.name))
    obs_files = list(observation_path.parent.glob(observation_path.name)) if observation_path else []

    if obs_files:
        # Case: Separate files for observation and simulation
        obs_data = {file.stem.split('_')[-1]: pd.read_csv(file, parse_dates=[index_column]) for file in obs_files}
        sim_data = {file.stem.split('_')[-1]: pd.read_csv(file, parse_dates=[index_column]) for file in sim_files}

        common_catchments = set(obs_data.keys()) & set(sim_data.keys())
        for catchment in common_catchments:
            df_obs = obs_data[catchment][[index_column, observation_column]]
            df_sim = sim_data[catchment][[index_column, simulation_column]]
            df = df_obs.merge(df_sim, on=index_column, how='inner')
            data[catchment] = df
    else:
        # Case: Single file containing both observation and simulation data
        for file in sim_files:
            catchment_name = file.stem.split('_')[-1]
            df = pd.read_csv(file, parse_dates=[index_column])
            if observation_column in df.columns and simulation_column in df.columns:
                data[catchment_name] = df
            else:
                print(f"Skipping {file.name} - required columns missing.")

    return data

def generate_matplotlib_plot(catchment, df, index_column, observation_column, simulation_column):
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x=index_column, y=observation_column, label='Observed')
    sns.lineplot(data=df, x=index_column, y=simulation_column, label='Simulated', linestyle='--')
    plt.title(f'Time Series - {catchment}')
    plt.xlabel('Date')
    plt.ylabel('Discharge Volume')
    plt.legend()
    plt.xticks(rotation=45)
    
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return img_base64

#def generate_plotly_plot(catchment, df, index_column, observation_column, simulation_column):
#    fig = px.line(df, x=index_column, y=[observation_column, simulation_column], title=f'Time Series - {catchment}')
#    fig.update_xaxes(tickangle=45)
#    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    
#    fig_json = json.loads(fig.to_json())
#    return fig_json


def _downsample(df, max_points=1000):
    n = len(df)
    if n <= max_points:
        return df
    step = max(1, n // max_points)
    return df.iloc[::step].copy()

def generate_plotly_plot(catchment, df, index_column, observation_column, simulation_column, max_points=1000):
    df_plot = _downsample(df[[index_column, observation_column, simulation_column]], max_points=max_points)
    fig = px.line(
        df_plot,
        x=index_column,
        y=[observation_column, simulation_column],
        title=f'Time Series - {catchment}',
        render_mode="webgl",
    )
    fig.update_xaxes(tickangle=45)
    fig.update_layout(legend=dict(orientation="h", y=1.02, x=1, yanchor="bottom", xanchor="right"))
    return fig.to_plotly_json()   

def generate_metrics_table(metrics):
    table_html = '<table class="table table-bordered table-striped">'
    table_html += '<thead><tr><th>Metric</th><th>Value</th></tr></thead><tbody>'
    for metric, value in metrics.items():
        table_html += f'<tr><td>{metric}</td><td>{value:.4f}</td></tr>'
    table_html += '</tbody></table>'
    return table_html

def process_all(data: dict[str, pd.DataFrame], index_column, observation_column, simulation_column):
    results = []
    catchment_plots = {}
    #catchment_tables = {}
    catchment_metrics = {}
    
    for name, df in data.items():
        df.dropna(subset=[observation_column, simulation_column], inplace=True)
        observed = df[observation_column]
        simulated = df[simulation_column]
        
        metrics = calculate_metrics(observed, simulated)
        results.append({'Catchment': name, **metrics})
        
        #plot_base64 = generate_matplotlib_plot(name, df, observation_column=observation_column, simulation_column=simulation_column)
        #metrics_table_html = generate_metrics_table(metrics)
        plot_json = generate_plotly_plot(name, df, index_column, observation_column=observation_column, simulation_column=simulation_column, max_points=1000)
        catchment_plots[name] = plot_json
        #catchment_plots[name] = plot_base64
        #catchment_tables[name] = metrics_table_html
        catchment_metrics[name] = metrics
    
    results_df = pd.DataFrame(results)
    results_df.to_csv("/out/metrics_summary.csv", index=False)
    results_df.to_json("/out/metrics_summary.json", orient="records", indent=4)
    
    #return catchment_plots, catchment_tables, catchment_metrics
    return catchment_plots, catchment_metrics

