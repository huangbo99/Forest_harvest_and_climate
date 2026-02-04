import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

YEAR_START = 2004
YEAR_END = 2023

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

INDIR = "../data/DataGEE_FIRE_FORESTS/"

# Store data for all countries
data_list = []

# Process each country's forest data
for i, country_code in enumerate(list_countries):
    country_name = list_countries_REAL[i]

    # Define file paths
    file_broad = f"{INDIR}Country_Forest_Change_Compact_loss_broad_WIND_{country_code}.csv"
    file_needle = f"{INDIR}Country_Forest_Change_Compact_loss_Needle_WIND_{country_code}.csv"
    file_mix = f"{INDIR}Country_Forest_Change_Compact_loss_Mix_WIND_{country_code}.csv"

    try:
        # Read CSV files
        df_broad = pd.read_csv(file_broad)
        df_needle = pd.read_csv(file_needle)
        df_mix = pd.read_csv(file_mix)

        # Create dataframe with yearly values
        df = pd.DataFrame()
        df["Year"] = df_broad["year"]
        df["Broadleaf"] = df_broad["Forest Loss Total"] / 1e10  # Convert m2 to Mha
        df["Needleleaf"] = df_needle["Forest Loss Total"] / 1e10
        df["Mixed"] = df_mix["Forest Loss Total"] / 1e10
        df["Country"] = country_name

        # Append to data list
        data_list.append(df)
    except FileNotFoundError:
        print(f"Missing file for {country_name}, skipping...")

# Combine all country data
big_data_EU = pd.concat(data_list, ignore_index=True)


# Filter data for each subregion
def filter_region_data(region_list):
    return big_data_EU[big_data_EU['Country'].isin(region_list)]

western_data = filter_region_data(westernEuropeCountries)
northern_data = filter_region_data(northernEuropeCountries)
southern_data = filter_region_data(southernEuropeCountries)
eastern_data = filter_region_data(easternEuropeCountries)


# ---------- 1) Aggregate to region-year (sum across countries in that region) ----------
def region_year_sum(df_region: pd.DataFrame) -> pd.DataFrame:
    out = (
        df_region[
            (df_region["Year"] >= YEAR_START) &
            (df_region["Year"] <= YEAR_END)
        ]
        .groupby("Year", as_index=False)[["Broadleaf", "Needleleaf", "Mixed"]]
        .sum()
    )

    # Apply your correction factor
    out[["Broadleaf", "Needleleaf", "Mixed"]] = out[["Broadleaf", "Needleleaf", "Mixed"]] / 0.85
    return out

reg_data = {
    "Northern": region_year_sum(northern_data),
    "Western":  region_year_sum(western_data),
    "Southern": region_year_sum(southern_data),
    "Eastern":  region_year_sum(eastern_data),
}


# ---------- 2) Build a single "year x region" table per forest type ----------
# Determine all years present across regions (ensures consistent x-axis)
all_years = sorted(set().union(*[set(d["Year"]) for d in reg_data.values()]))
print(all_years)

# Create DataFrames indexed by Year with columns = Region for each forest type
forest_types = ["Broadleaf", "Needleleaf", "Mixed"]
tables = {}

for forest in forest_types:
    t = pd.DataFrame(index=all_years)
    for region, df in reg_data.items():
        t[region] = df.set_index("Year")[forest]
    # If some region missing some years, fill with 0 so stacking works
    t = t.fillna(0.0)
    tables[forest] = t

# ---------- 3) Plot: 3 subplots, one bar per year, stacked by region ----------
region_colors = {
    "Northern": '#228B22',
    "Western":  '#87CEEB',
    "Southern": '#E4A700',
    "Eastern":  '#8B4513',
}

# Map to your labels NF/BF/MF (assuming Needleleaf=NF, Broadleaf=BF, Mixed=MF)
forest_colors = {
    "Needleleaf": "#59A14F",  # muted blue
    "Broadleaf":  "#F28E2B",  # muted orange
    "Mixed":      "#4E79A7",  # muted green
}

forest_label = {
    "Needleleaf": "NF",
    "Broadleaf":  "BF",
    "Mixed":      "MF",
}

# Optional: hatch patterns so each forest type is distinguishable within same region color
forest_hatch = {
    "Needleleaf": "//",
    "Broadleaf": "",
    "Mixed": "\\",
}

forest_types = ["Needleleaf", "Broadleaf", "Mixed"]
regions_order = ["Northern", "Western", "Southern", "Eastern"]

# ---- Aggregate regions within each forest type ----
# Result: Year x ForestType
F = pd.DataFrame(index=all_years)

for forest in forest_types:
    F[forest] = tables[forest].sum(axis=1).reindex(all_years).fillna(0.0)

# Total harvest per year
total = F.sum(axis=1)

# Convert to percentages
P = F.div(total, axis=0).fillna(0.0) * 100.0

# ---- Plot ----
fig, ax = plt.subplots(figsize=(9, 6))  # shorter width = less empty space

x = np.arange(len(all_years))
bottom = np.zeros(len(all_years))

for forest in forest_types:
    vals = P[forest].values

    bars = ax.bar(
        x,
        vals,
        bottom=bottom,
        color=forest_colors[forest],
        edgecolor="white",
        linewidth=0.4,
        label=forest_label[forest],
        width=0.75,   # <-- key for reducing side gaps
    )

    # Optional labels
    for i, v in enumerate(vals):
        if v >= 50:
            ax.text(
                x[i],
                bottom[i] + v / 2,
                f"{v:.0f}%",
                ha="center",
                va="center",
                fontsize=8,
            )

    bottom += vals

# ---- Formatting ----
ax.set_ylim(0, 100)
ax.set_ylabel("Share of total harvest (%)")
ax.set_xlabel("Year")
ax.set_title("Harvest composition by forest type (all regions aggregated)")

ax.set_xticks(x)

# Reduce visual clutter for long time series
step = max(1, len(all_years) // 30)
tick_pos = np.arange(0, len(all_years), step)
ax.set_xticks(tick_pos)
ax.set_xticklabels([all_years[i] for i in tick_pos], rotation=45, ha="right")

ax.grid(axis="y", linestyle="--", alpha=0.5)
ax.legend(title="Forest type", ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.15))

# Tighten margins explicitly
ax.margins(x=0.01)

plt.tight_layout()
plt.savefig(
    "../graph/ForestHarvest_Yearly_100pct_ForestTypeOnly.pdf",
    format="pdf",
    bbox_inches="tight",
)
plt.show()