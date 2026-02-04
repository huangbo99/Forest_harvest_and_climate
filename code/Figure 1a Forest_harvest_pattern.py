# Figure 1, forest harvest area percentage

import rasterio
import rioxarray as rxr # pyright: ignore[reportMissingImports]
import numpy as np
import xarray as xr
import cartopy.crs as ccrs # type: ignore
import matplotlib.pyplot as plt
import cartopy.feature as cfeature # type: ignore
from rasterio.warp import calculate_default_transform, reproject, Resampling
from matplotlib.colors import PowerNorm

# Define projection
laes_prj = "+proj=laea +lat_0=52 +lon_0=10 +x_0=4321000 +y_0=3210000 +ellps=GRS80 +units=m +no_defs"

# Load rasters
final_loss = rxr.open_rasterio("../data/FinalLoss_at_20km_2023.tif")
forest = rxr.open_rasterio("../data/Forest2000_at_20km_2023.tif")

# Convert land cover threshold
forest_frac = forest / 640000

# Calculate percentage of pixels
rho = (final_loss / forest.isel(band=0)) * 100
rho = rho.where(rho != 0, np.nan)

# Compute median and MAD
rho_median = rho.median(dim="band", skipna=True)
rho_mean = rho.mean(dim="band", skipna=True)
rho_mad = rho.reduce(np.median, dim="band", keep_attrs=True)  # Approximate MAD
rho_sd = rho.std(dim="band", skipna=True)



# Ensure rho and the mask have the same dimensions before applying the condition
outlier_condition = (rho > (rho_median + (3 * rho_mad))) & (rho > 3) & (forest_frac[0] > 0.1)



# Remove pixels with low forest cover and suspected windthrow
rho2 = rho.copy()
outlier_condition = (rho2 > (rho_median + (3 * rho_mad))) & (rho2 > 3) & (forest_frac[0] > 0.1)
rho2 = xr.where(outlier_condition, 100, np.nan)
rho2 = xr.where(rho2 > 0, 1, np.nan)
rho2 = rho2.max(dim="band", skipna=True)

# Update rho
rho = rho.where(~outlier_condition, np.nan)



# Select specific years (assuming band indices match year sequence)
final_loss_area = rho.isel(band=slice(3, 23))  # Selecting 2003-2022 bands

#forest_area = forest.rio.reproject(laes_prj)
#final_loss_area = final_loss_area.rio.reproject(laes_prj)

# Compute time sum of Final_loss_area
time_sum_final_loss = final_loss_area.sum(dim="band", skipna=True)

# Replace all 0 values with NaN in time_sum_final_loss
time_sum_final_loss = time_sum_final_loss.where(time_sum_final_loss != 0, np.nan)


# Define Lambert Conformal Conic projection
proj = ccrs.LambertConformal(central_longitude=10, standard_parallels=(44, 55))

# Define bounding box (EPSG:4326)
PLOT_BBOX = {"min_x": -8.5, "max_x": 28.0, "min_y": 34.0, "max_y": 72.0}

# Create a figure and axis with the specified projection
fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': proj})

# Set the extent (bounding box) for the plot
ax.set_extent([PLOT_BBOX["min_x"], PLOT_BBOX["max_x"], PLOT_BBOX["min_y"], PLOT_BBOX["max_y"]], crs=ccrs.PlateCarree())

# Plot the time sum of final loss on the Lambert Conformal Conic projection
norm = PowerNorm(gamma=0.5, vmin=0, vmax=30)

time_sum_final_loss = time_sum_final_loss.where(time_sum_final_loss > 2)  # not show the low harvest 
# Here, we assume that `time_sum_final_loss` has been converted to the correct coordinate system
time_sum_final_loss.plot(
    ax=ax,
    transform=ccrs.PlateCarree(),
    cmap="YlGn",
   # norm=norm,
    vmin=0, vmax=30,
    cbar_kwargs={
        "label": "Forest harvest area (%)",
        "shrink": 0.8
    }
)

# Add map features
ax.add_feature(cfeature.BORDERS, linewidth=0.5, edgecolor='black')
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.3)
ax.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.3)

# Add gridlines (curved latitudes)
gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False,
                  linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
gl.top_labels = False
gl.right_labels = False

# Add labels and title
ax.set_title("Time Sum of Final Loss Over Time", fontsize=16)

plt.savefig("../graph/Forest_loss_area_percentage.pdf", format='pdf', bbox_inches="tight")

# Show the plot
plt.show()
