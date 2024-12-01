import rasterio 
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
import geopandas as gpd
import matplotlib.pyplot as plt
import os 
import glob
from concurrent.futures import ProcessPoolExecutor

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

def reproject_clip(in_tiff, clip_gdf, out_tiff):
    dst_crs = clip_gdf.geometry.crs

    with rasterio.open(in_tiff) as src: 
        transform, width, height = calculate_default_transform(src.crs, dst_crs, src.width, src.height, *src.bounds)

        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs, 
            'transform': transform, 
            'width': width, 
            'height': height
        })

        with rasterio.open(out_tiff, 'w+', **kwargs) as dst:
            reproject(
                source=rasterio.band(src, 1),
                destination=rasterio.band(dst, 1), 
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=dst_crs,
                resampling= Resampling.nearest)
        
            out_image, out_transform = mask(dst, clip_gdf.geometry, crop=True)
            out_meta = dst.meta.copy()
            out_meta.update({
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform
            })
        
        with rasterio.open(out_tiff, 'w', **out_meta) as dst: 
            dst.write(out_image)

        print('written', out_tiff)
        return True




def ndvi_reproject_clip():
    
    tifs = glob.glob('weekly_max_ndvi/data/unzipped/*/*/*.tif')
    
    clip_gdf = gpd.read_file('input/BC_Boundary/BC_Boundary.shp')

    os.makedirs('weekly_max_ndvi/data/clipped', exist_ok=True)

    pool = ProcessPoolExecutor(10)

    return_status = []

    for tif in tifs: 
        out_tiff = os.path.join('weekly_max_ndvi/data/clipped', os.path.basename(tif).lower())

        return_status.append(pool.submit(reproject_clip, tif, clip_gdf, out_tiff))
    print('waiting for pool to shutdown')
    pool.shutdown(wait=True)

    assert(all([status.result for status in return_status]))



if __name__ == '__main__':
    # clip(r'input\CA_Forest_Fire_1985-2020\CA_Forest_Fire_1985-2020.tif',
    #      r'input\BC_Boundary\BC_Boundary.shp',
    #      r'processing\fire_clipped.tiff')
    # clip(r'input\CA_Forest_Harvest_1985-2020\CA_Forest_Harvest_1985-2020.tif',
    #      r'input\BC_Boundary\BC_Boundary.shp',
    #      r'processing\harvest_clipped.tiff')
    ndvi_reproject_clip()


