import os 
import zipfile
import concurrent.futures


def unzip(src_dir, dst_dir, zip_name):
    print(src_dir, dst_dir, zip_name) 
    zip_path = os.sep.join([src_dir, zip_name])
    dst = os.sep.join([dst_dir, zip_name])
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        files = zip_ref.namelist()
        for file in files: 
            if not file.endswith('.ovr'):
                zip_ref.extract(file, dst)




if __name__ == "__main__":    

    zipped = './data/zipped'
    unzipped = './data/unzipped'

    for year in os.listdir(zipped):
        zipped_year = os.sep.join([zipped, year])
        unzipped_year = os.sep.join([unzipped, year])

        os.makedirs(unzipped_year, exist_ok=True)
        print('starting thread pool')
        with concurrent.futures.ThreadPoolExecutor(16) as pool: 

            for zip in os.listdir(zipped_year):
                pool.submit(unzip, zipped_year, unzipped_year, zip) 
            print('waiting for pool to shutdown')
            pool.shutdown(wait=True)
            print('pool done')

            
