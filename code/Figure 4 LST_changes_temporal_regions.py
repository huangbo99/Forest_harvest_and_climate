## Pairwise analysis
## effectyears  dailymean, NEW

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob

# Forests: NF, BF, MF, TOT
forest = "BF" # change forest type here
# Patch, cells
patch = "220"
# Variables for file types
lstDay_variable = "LST_Day"
lstNight_variable = "LST_Night"

# Set the file paths (update the directory path as needed)
day_file_pattern = f'../data/LST_Diff/{lstDay_variable}_{patch}cell_{forest}_*.csv'
night_file_pattern = f'../data/LST_Diff/{lstNight_variable}_{patch}cell_{forest}_*.csv'

# Get the list of files
day_csv_files = glob.glob(day_file_pattern)
night_csv_files = glob.glob(night_file_pattern)


# Initialize empty lists to store data from each file
day_data_frames = []
night_data_frames = []

# Read and process each day and night file
for day_file, night_file in zip(day_csv_files, night_csv_files):
    # Read the CSV files
    day_df = pd.read_csv(day_file)
    night_df = pd.read_csv(night_file)
    
    # Multiply the LST_Day_1km_mean and LST_Night_1km_mean by 0.02
    day_df['Daytime LST'] = day_df['LST_Day_mean'] 
    night_df['Nighttime LST'] = night_df['LST_Night_mean'] 
    
    day_df.loc[day_df['lossYear'] < 2003, 'Daytime LST'] = np.nan
    night_df.loc[night_df['lossYear'] < 2003, 'Nighttime LST'] = np.nan

    day_df['effectYear'] = day_df['analysisYear'] - day_df['lossYear']
    night_df['effectYear'] = night_df['analysisYear'] - night_df['lossYear']
    
    # Filter data: set LST to NaN if count is less than 50
    day_df.loc[day_df['LST_Day_count'] < 50, 'Daytime LST'] = np.nan
    night_df.loc[night_df['LST_Night_count'] < 50, 'Nighttime LST'] = np.nan

    
    # Select relevant columns
    relevant_day_columns = day_df[['Daytime LST', 'season', 'effectYear', 'region','lossYear', 'analysisYear']]
    relevant_night_columns = night_df[['Nighttime LST', 'season', 'effectYear', 'region','lossYear', 'analysisYear']]
    
    # Append the dataframes to their respective lists
    day_data_frames.append(relevant_day_columns)
    night_data_frames.append(relevant_night_columns)

# Concatenate all dataframes into single dataframes for day and night
combined_day_data = pd.concat(day_data_frames, ignore_index=True)
combined_night_data = pd.concat(night_data_frames, ignore_index=True)

# Merge day and night dataframes on 'season', 'effectYear', and 'region'
combined_data = pd.merge(combined_day_data, combined_night_data, on=['season', 'effectYear', 'region', 'lossYear', 'analysisYear'])

# Calculate daily mean as (LST_Day_1km_mean + LST_Night_1km_mean) / 2
combined_data['Daily LST'] = (combined_data['Daytime LST'] + combined_data['Nighttime LST']) / 2

# Filter the data for effectYear from 1 to 20
filtered_data = combined_data[(combined_data['effectYear'] >= 1) & (combined_data['effectYear'] <= 20)]

filtered_data = filtered_data.dropna()

filtered_data.to_csv(f'{forest}_{patch}cell.csv')
# Define the regions and seasons
regions = filtered_data['region'].unique()
seasons = filtered_data['season'].unique()

# Define season colors (natural tones)
season_colors = {
    'Spring': '#66c2a5',  # Fresh Green
    'Summer': '#fc8d62',  # Warm Orange
    'Autumn': '#8da0cb',  # Cool Blue
    'Winter': '#e78ac3',  # Soft Pink
    'Annual': '#a6d854'   # Bright Green
}


# Loop through each region and season to create separate plots
for region in regions:
    region_data = filtered_data[filtered_data['region'] == region]
    
    # Create a figure for each region
    plt.figure(figsize=(12, 8))
    
    # Define the seasons to plot
    seasons_to_plot = ['Spring', 'Summer', 'Autumn', 'Winter', 'Annual']
    
    # Initialize a list to store data for this region
    region_results = []
    
    for season in seasons_to_plot:
        # Filter data for the specific season
        season_data = region_data[region_data['season'] == season]

        
        # Calculate mean, standard deviation, and standard error for Daily LST
        mean_daily = season_data.groupby('effectYear')['Daily LST'].mean()
        std_daily = season_data.groupby('effectYear')['Daily LST'].std()
        count_daily = season_data.groupby('effectYear')['Daily LST'].count()
        
        se_daily = std_daily / np.sqrt(count_daily)
        
        # Get season color
        color = season_colors.get(season, '#000000')

        
        # Plot Daily LST with standard error shading
        plt.plot(mean_daily.index, mean_daily, label=f'{season} Daily LST', color=color, linestyle='-', marker='o')
       # plt.fill_between(mean_daily.index, mean_daily - std_daily, mean_daily + std_daily, alpha=0.2, label=f'{season} SE')
        plt.fill_between(mean_daily.index, mean_daily - se_daily, mean_daily + se_daily, color=color, alpha=0.2, label=f'{season} SE')
    
        # Store mean and SE data for this season
        for year in mean_daily.index:
            region_results.append({
                'region': region,
                'season': season,
                'effectYear': year,
                'mean_daily': mean_daily.loc[year],
                'se_daily': se_daily.loc[year]
            })
            
    # Customize the plot
    plt.title(f'Daily Mean LST by Effect Year for {region}')
    plt.xlabel('Years after forest harvesting')
    plt.ylabel('Daily LST (°C)')
    plt.xticks(range(1, 21))  # Effect years from 1 to 20
    plt.legend()
 #   plt.grid(True)
    plt.axhline(y=0, linestyle='--', color='black')
    
    # Save the plot or show it
#    plt.savefig(f'LST_Daily_Mean_{region}.png', dpi=300)  # Save each plot as a PNG file
    pltname = f'Forest_change_LST_diff_effectyears_dailymean_{forest}_{patch}cells_{region}.pdf'

    plt.savefig("../graph/"+ pltname,format='pdf')
 
    plt.show()  
    
    # Convert collected data to DataFrame and save as CSV
    results_df = pd.DataFrame(region_results)
    csv_filename = f'../data/LST_Daily_Mean_{forest}_{patch}cells_{region}.csv'
    results_df.to_csv(csv_filename, index=False)