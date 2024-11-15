# %%
import rasterio 
from rasterio.mask import mask
import geopandas as gpd
import matplotlib.pyplot as plt

# %%
intiff = './CA_Forest_Harvest_1985-2020/CA_Forest_Harvest_1985-2020.tif'
inshp = './BC_Boundary(1)/BC_Boundary.shp'
outtiff = './outputs/forest_Harvest.tif'
bc = gpd.read_file(inshp)
bc

# %%
with rasterio.open(intiff) as src: 
    bc = bc.to_crs(src.crs)
    out_image, out_transform = mask(src, bc.geometry, crop=True)
    out_meta=src.meta.copy()

out_meta.update({
    "driver":"Gtiff",
    "height":out_image.shape[1], # height starts with shape[1]
    "width":out_image.shape[2], # width starts with shape[2]
    "transform":out_transform
})
              
with rasterio.open(outtiff,'w',**out_meta) as dst:
    dst.write(out_image)

# %%
with rasterio.open('./outputs/forest_Harvest.tif') as src:
    plt.imshow(src.read(1))
    plt.savefig('outputs/forest_harvest.png')



# %%