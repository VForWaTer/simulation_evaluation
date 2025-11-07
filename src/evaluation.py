import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score
from scipy.stats import pearsonr
from pathlib import Path



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

def process_data_and_metrics(
    data: dict[str, pd.DataFrame], 
    index_column: str,
    observation_column: str,
    simulation_column: str,
    # Future parameters for downsampling/extent cutting will be added here
    # max_points: int | None = None,
    # date_range: tuple[str, str] | None = None,
) -> tuple[dict[str, dict], dict[str, pd.DataFrame]]:
    """
    Process catchment data to calculate metrics and prepare datasets for visualization.
    
    This function separates data processing from plot generation, allowing for
    future flexibility in downsampling, date range filtering, or other data transformations.
    """
    catchment_metrics = {}
    catchment_datasets = {}
    
    for name, df in data.items():
        # Create a copy to avoid modifying original data
        df_processed = df.copy()
        
        # Remove rows with missing values in key columns
        df_processed.dropna(subset=[observation_column, simulation_column], inplace=True)
        
        # Extract series for metric calculation
        observed = df_processed[observation_column]
        simulated = df_processed[simulation_column]
        
        # Calculate metrics
        metrics = calculate_metrics(observed, simulated)
        catchment_metrics[name] = metrics
        
        # Store processed dataset (will be used for plot generation later)
        # Future: Apply downsampling/extent cutting here before storing
        catchment_datasets[name] = df_processed
    
    return catchment_metrics, catchment_datasets

