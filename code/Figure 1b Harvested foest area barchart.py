import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Define subregions
westernEuropeCountries = ['France', 'Germany', 'Belgium', 'Netherlands', 'Luxembourg', 'Switzerland', 'Austria', 'Monaco', 'United Kingdom', 'Ireland']
northernEuropeCountries = ['Denmark', 'Sweden', 'Norway', 'Finland', 'Iceland', 'Estonia', 'Latvia', 'Lithuania']
southernEuropeCountries = ['Italy', 'Spain', 'Portugal', 'Greece', 'Malta', 'Cyprus', 'Slovenia', 'Serbia', 'Croatia', 'Bulgaria', 'Albania', 'Macedonia', 'Kosovo','Montenegro', 'Bosnia & Herzegovina']
easternEuropeCountries = ['Poland', 'Czechia', 'Slovakia', 'Hungary', 'Romania']

# Define country codes and names
list_countries = ['AU','HU','PL','IT','FR', 'LO','GM','EZ','RO','HR','SW','FI','UK','EI','SP','PO',
                  'LH','LG','EN','GR','BU','BE','LU','SI','DA','NL']
list_countries_REAL = ['Austria','Hungary','Poland','Italy','France', 'Slovakia','Germany',
                       'Czech Republic','Romania','Croatia','Sweden','Finland','UK','Ireland','Spain','Portugal',
                       'Lithuania','Latvia','Estonia','Greece','Bulgaria','Belgium', 
                       'Luxembourg','Slovenia', 'Denmark','Netherlands']

# Initialize an empty list to store data
data_list = []

# Loop through each country to read and process its data
for i, country_code in enumerate(list_countries):
    country_name = list_countries_REAL[i]
    
    # Define file paths (update these paths as per your data location)
    base_path = "../data/"
    file_loss = os.path.join(base_path, f"DataGEE_FIRE_MED/Country_Forest_Change_loss_{country_code}.csv")
    file_total_loss = os.path.join(base_path, f"DataGEE_FIRE_MED/Country_Forest_Change_TOTAL_loss_{country_code}.csv")
    file_wind_loss = os.path.join(base_path, f"DataGEE_FIRE_TOT/Country_Forest_Change_loss_WIND__{country_code}.csv")
    file_wind_icl_loss = os.path.join(base_path, f"DataGEE_FIRE_TOT/Country_Forest_Change_loss_WIND_ICL_{country_code}.csv")
    
    try:
        # Read CSV files
        df_loss = pd.read_csv(file_loss)
        df_total_loss = pd.read_csv(file_total_loss)
        df_wind_loss = pd.read_csv(file_wind_loss)
        df_wind_icl_loss = pd.read_csv(file_wind_icl_loss)
        
        # Create a new dataframe to store processed values
        df = pd.DataFrame()
        df['Year'] = df_loss['year']
        df['TotalLoss'] = df_total_loss['Forest Loss Total'] / 1e10  # Convert m2 to Mha
        df['PartialLoss'] = df_loss['Forest Loss Total'] / 1e10
        df['TotalLoss2'] = df_wind_loss['Forest Loss Total'] / 1e10
        df['TotalLoss3'] = df_wind_icl_loss['Forest Loss Total'] / 1e10
        df['Country'] = country_name

        # Append to data list
        data_list.append(df)
    except FileNotFoundError:
        print(f"Missing file for {country_name}, skipping...")

# Combine all country data into one DataFrame
big_data_EU = pd.concat(data_list, ignore_index=True)

# Assuming big_data_EU already exists
# Filter data for each subregion
def filter_region_data(region_list):
    return big_data_EU[big_data_EU['Country'].isin(region_list)]

western_data = filter_region_data(westernEuropeCountries)
northern_data = filter_region_data(northernEuropeCountries)
southern_data = filter_region_data(southernEuropeCountries)
eastern_data = filter_region_data(easternEuropeCountries)

# Aggregate Harvest data for each region by year
western_data_grouped = western_data.groupby('Year')['TotalLoss2'].sum().reset_index()
northern_data_grouped = northern_data.groupby('Year')['TotalLoss2'].sum().reset_index()
southern_data_grouped = southern_data.groupby('Year')['TotalLoss2'].sum().reset_index()
eastern_data_grouped = eastern_data.groupby('Year')['TotalLoss2'].sum().reset_index()

# Create a DataFrame to hold the aggregated values
region_data = pd.DataFrame({
    'Year': western_data_grouped['Year'],
    'Northern Europe': northern_data_grouped['TotalLoss2'],
    'Western Europe': western_data_grouped['TotalLoss2'],
    'Southern Europe': southern_data_grouped['TotalLoss2'],
    'Eastern Europe': eastern_data_grouped['TotalLoss2']
})


# Filter for years >= 2004
region_data = region_data[region_data['Year'] >= 2004]

'''
# Set colors and order
colors = ['#009E73', '#F0E442', '#0072B2']  # Blue (Harvest), Yellow (Fires), Green (Wind)
labels = ["Harvest", "Fires", "Wind"]

# Define x-axis ticks
x_ticks = [2004, 2008, 2012, 2016, 2020]

# Plot stacked bars
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(region_data["Year"], counts_EU["Harvest"], color=colors[0], label=labels[0])
ax.bar(region_data["Year"], counts_EU["Fires"], bottom=counts_EU["Harvest"], color=colors[1], label=labels[1])
ax.bar(counts_EU["Year"], counts_EU["Wind"], bottom=counts_EU["Harvest"] + counts_EU["Fires"], color=colors[2], label=labels[2])
'''

colors = ['#228B22', '#87CEEB','#E4A700', '#8B4513']
#colors = ['#009E73', '#0072B2','#F0E442', '#B4B6B6']
# Plotting
fig, ax = plt.subplots(figsize=(9, 6))

# Plot each region in one column
region_data.set_index('Year').plot(kind='bar', stacked=True, ax=ax, color=colors, width=0.75)

# Formatting
ax.set_xlabel("Year")
#ax.set_xticks(x_ticks)
ax.set_ylabel("Forest Harvest Area (Mha)")
ax.set_title("Forest Harvest in Europe by Region")
ax.legend(title="Region", loc="upper left")
ax.grid(axis="y", linestyle="--", alpha=0.7)
#ax.set_xticklabels(region_data['Year'], rotation=45)


# Show plot
plt.tight_layout()
plt.savefig("../graph/Stacked_ForestHarvestByRegion.pdf", format='pdf', bbox_inches="tight")
plt.show()
