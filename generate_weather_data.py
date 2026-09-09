import pandas as pd
import numpy as np
import os

def generate_weather():
    raw_path = 'data/raw/Tamilnadu_and_Puducherry_weather_2022_cleaned.csv'
    print(f"Loading raw data from {raw_path}...")
    
    # We only need a few columns, so we specify usecols to save memory and parsing time
    usecols = ['time', 'TMP_2m', 'RH_2m', 'APCP_sfc']
    df_raw = pd.read_csv(raw_path, usecols=usecols)
    
    # Convert time to datetime
    df_raw['time'] = pd.to_datetime(df_raw['time'])
    
    # Group by date to get daily average across all cities
    print("Aggregating daily weather...")
    df_daily = df_raw.groupby('time').mean().reset_index()
    
    # Map columns
    df_daily = df_daily.rename(columns={
        'time': 'date',
        'RH_2m': 'humidity',
        'APCP_sfc': 'rainfall'
    })
    
    # Convert temperature from Kelvin to Celsius
    df_daily['temperature'] = df_daily['TMP_2m'] - 273.15
    df_daily = df_daily.drop(columns=['TMP_2m'])
    
    # Replicate for 2023 to 2026
    print("Replicating data for 2022-2026...")
    dfs = []
    
    # Include the original 2022 data as well
    dfs.append(df_daily.copy())
    
    for year in range(2023, 2027):
        df_year = df_daily.copy()
        # Safe to replace year as 2022 is not a leap year (no Feb 29 to worry about)
        df_year['date'] = df_year['date'].apply(lambda x: x.replace(year=year))
        dfs.append(df_year)
        
    df_final = pd.concat(dfs, ignore_index=True)
    df_final = df_final.sort_values('date')
    
    os.makedirs('data/processed', exist_ok=True)
    out_path = 'data/processed/weather_history.csv'
    df_final.to_csv(out_path, index=False)
    print(f"Saved aggregated and replicated weather data to {out_path}")

if __name__ == "__main__":
    generate_weather()
