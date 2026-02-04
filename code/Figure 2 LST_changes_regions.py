# barchart 

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob

# Forests: NF, BF, MF, TOT
forest = "TOT" # change forest type here
# Patch, cells
patch = "220"
# Variables for file types
lstDay_variable = "lstDay"
lstNight_variable = "lstNight"

# Define the seasons to plot
seasons_to_plot = ['Spring', 'Summer', 'Fall', 'Winter', 'Annual']

# Set the file paths (update the directory path as needed)
day_file_pattern = f'/home/bohuang/Work/Code/Biomass/data/LST_Diff/{lstDay_variable}_Diff_Statistics_noFire_noWind_{forest}_{patch}cells_*.csv'
night_file_pattern = f'/home/bohuang/Work/Code/Biomass/data/LST_Diff/{lstNight_variable}_Diff_Statistics_noFire_noWind_{forest}_{patch}cells_*.csv'

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
    day_df['Daytime LST'] = day_df['LST_Day_1km_mean'] * 0.02
    night_df['Nighttime LST'] = night_df['LST_Night_1km_mean'] * 0.02
    
    day_df['effectYear'] = day_df['analysisYear'] - day_df['lossYear']
    night_df['effectYear'] = night_df['analysisYear'] - night_df['lossYear']
    
    # Filter data: set LST to NaN if count is less than 50
    day_df.loc[day_df['LST_Day_1km_count'] < 40, 'Daytime LST'] = np.nan
    night_df.loc[night_df['LST_Night_1km_count'] < 40, 'Nighttime LST'] = np.nan

    # Select relevant columns
    relevant_day_columns = day_df[['Daytime LST', 'season', 'effectYear', 'region']]
    relevant_night_columns = night_df[['Nighttime LST', 'season', 'effectYear', 'region']]
    
    # Append the dataframes to their respective lists
    day_data_frames.append(relevant_day_columns)
    night_data_frames.append(relevant_night_columns)

# Concatenate all dataframes into single dataframes for day and night
combined_day_data = pd.concat(day_data_frames, ignore_index=True)
combined_night_data = pd.concat(night_data_frames, ignore_index=True)

# Merge day and night dataframes on 'season', 'effectYear', and 'region'
combined_data = pd.merge(combined_day_data, combined_night_data, on=['season', 'effectYear', 'region'])

# Calculate daily mean as (LST_Day_1km_mean + LST_Night_1km_mean) / 2
combined_data['Daily LST'] = (combined_data['Daytime LST'] + combined_data['Nighttime LST']) / 2

# Filter the data for effectYear from 1 to 20
filtered_data = combined_data[(combined_data['effectYear'] >= 1) & (combined_data['effectYear'] <= 20)]

# Define the regions and seasons
regions = filtered_data['region'].unique()
seasons = filtered_data['season'].unique()

# Calculate the average for every effect year
effect_year_avg = filtered_data.groupby(['region', 'season', 'effectYear']).agg(
    daytime_avg=('Daytime LST', 'mean'),
    nighttime_avg=('Nighttime LST', 'mean'),
    daily_avg=('Daily LST', 'mean')
).reset_index()


# Loop through each region and season to create separate plots
for region in regions:
    region_data = effect_year_avg[effect_year_avg['region'] == region]
    
    
    # Calculate means and standard errors for each season
    summary = region_data.groupby('season').agg(
        daytime_mean=('daytime_avg', 'mean'),
        daytime_std=('daytime_avg', 'std'),
        daytime_count=('daytime_avg', 'count'),
        nighttime_mean=('nighttime_avg', 'mean'),
        nighttime_std=('nighttime_avg', 'std'),
        nighttime_count=('nighttime_avg', 'count'),
        daily_mean=('daily_avg', 'mean'),
        daily_std=('daily_avg', 'std'),
        daily_count=('daily_avg', 'count')
    ).reindex(seasons_to_plot)  # Ensure correct seasonal order
    
    # Print the daily count for debugging or verification
    print(f"\nDaily count for region '{region}':")
    print(summary['daily_count'])

    # Calculate standard error
    summary['daytime_se'] = summary['daytime_std'] / np.sqrt(summary['daytime_count'])
    summary['nighttime_se'] = summary['nighttime_std'] / np.sqrt(summary['nighttime_count'])
    summary['daily_se'] = summary['daily_std'] / np.sqrt(summary['daily_count'])
    
    summary.to_csv(f'../data/Forest_change_LST_diff_barchart_{forest}_{patch}cells_{region}.csv')
    
    # Plot
    fig, ax = plt.subplots(figsize=(12, 8))
    x = np.arange(len(seasons_to_plot))  # X-axis positions
    bar_width = 0.20  # Width of each bar
    
    # Plot Daytime, Nighttime, and Daily Mean bars

    ax.bar(
        x, summary['nighttime_mean'], width=bar_width,
        yerr=summary['nighttime_se'], label='Nighttime LST', capsize=5
    )
    ax.bar(
        x - bar_width, summary['daytime_mean'], width=bar_width,
        yerr=summary['daytime_se'], label='Daytime LST', capsize=5
    )
    ax.bar(
        x + bar_width, summary['daily_mean'], width=bar_width,
        yerr=summary['daily_se'], label='Daily Mean LST', capsize=5
    )
     
    plt.axhline(y=0, linestyle='--', color='black')
    
    # Set the custom x-ticks labels
    ax.set_xticks(x)  # Set tick positions
    ax.set_xticklabels(['Spring', 'Summer', 'Autumn', 'Winter', 'Annual'])  # Set labels


    # Save the plot or display it
    plt.tight_layout()
 
    # Add legend
    plt.legend(loc='upper right')
    
    # Save the plot or show it
    
#    plt.savefig(f'LST_Daily_Mean_{region}.png', dpi=300)  # Save each plot as a PNG file
    pltname = f'Forest_change_LST_diff_barchart_{forest}_{patch}cells_{region}.pdf'

    plt.savefig("../graph/"+ pltname,format='pdf')
 
    plt.show()
    
