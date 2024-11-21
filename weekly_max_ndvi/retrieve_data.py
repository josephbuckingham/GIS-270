from bs4 import BeautifulSoup
import requests
import shutil
import os



index = 'https://agriculture.canada.ca/atlas/data_donnees/calms/data_donnees/tif/mod_bestquality_maxndvi/'

years = [f"{year}" for year in range(2003, 2025)]

for year in years:
    year_index_html = requests.get(index + year + '/')
    year_folder = os.sep.join(['.', 'data', 'zipped', year]) 
    os.makedirs(year_folder, exist_ok=True)
    

    soup = BeautifulSoup(year_index_html.text, 'html.parser')
    for link in soup.find_all('a'):
        if link.get('href').endswith('.zip'):
            tiff_zip = link.get('href')
            get_link = index + year + '/' + tiff_zip
            tiff_zip_response = requests.get(get_link, stream=True)

            print(f'downloading {get_link}')
            tiff_dst = os.sep.join([year_folder, tiff_zip])
            with open(tiff_dst, 'wb') as out_zip:
                shutil.copyfileobj(tiff_zip_response.raw, out_zip)
            print(f'written to {tiff_dst}')

