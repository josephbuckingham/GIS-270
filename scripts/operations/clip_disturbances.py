import rasterio 
from rasterio.mask import mask
import geopandas as gpd
import matplotlib.pyplot as plt

def show_plot(tiff):
    with rasterio.open(tiff, 'r') as src:
        plt.imshow(src.read(1))
        plt.show()
    
def clip(in_tiff, clip_shp, out_tiff):
    clip_gdf = gpd.read_file(clip_shp)
    with rasterio.open(in_tiff) as src: 
        clip_gdf = clip_gdf.to_crs(src.crs)
        out_image, out_transform = mask(src, clip_gdf.geometry, crop=True)
        out_meta=src.meta.copy()

    out_meta.update({
        "driver":"Gtiff",
        "height":out_image.shape[1], # height starts with shape[1]
        "width":out_image.shape[2], # width starts with shape[2]
        "transform":out_transform
    })
                
    with rasterio.open(out_tiff,'w',**out_meta) as dst:
        dst.write(out_image)

    return out_tiff

if __name__ == '__main__':
    clip(r'input\CA_Forest_Fire_1985-2020\CA_Forest_Fire_1985-2020.tif',
         r'input\BC_Boundary\BC_Boundary.shp',
         r'processing\fire_clipped.tiff')
    clip(r'input\CA_Forest_Harvest_1985-2020\CA_Forest_Harvest_1985-2020.tif',
         r'input\BC_Boundary\BC_Boundary.shp',
         r'processing\harvest_clipped.tiff')


    