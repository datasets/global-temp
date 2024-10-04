# -*- coding: utf-8 -*-
import os
import csv
import shutil
import requests

GISTEMP_URL = 'https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv'
GCAG_URL_monthly = 'https://www.metoffice.gov.uk/hadobs/hadcrut5/data/HadCRUT.5.0.2.0/analysis/diagnostics/HadCRUT.5.0.2.0.analysis.summary_series.global.monthly.csv'
GCAG_URL_annual = 'https://www.metoffice.gov.uk/hadobs/hadcrut5/data/HadCRUT.5.0.2.0/analysis/diagnostics/HadCRUT.5.0.2.0.analysis.summary_series.global.annual.csv'

data = 'data/'
tmp = 'tmp/'

annual_gistemp = 'annual_gistemp.csv'
monthly_gistemp = 'monthly_gistemp.csv'
monthly_gcag = 'monthly_gcag.csv'
annual_gcag = 'annual_gcag.csv'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

def merge_csv_sorted(data1, data2, filename):
    """
        Merges two CSV files and sorts the data by year
    """
    merged_data = []
    with open(data1, 'r') as csv1, open(data2, 'r') as csv2:
        csv1_reader = csv.reader(csv1)
        csv2_reader = csv.reader(csv2)
        header = next(csv1_reader)
        # Skip the header of the second file since we already got it from the first file
        next(csv2_reader)
        merged_data.extend(csv1_reader)
        merged_data.extend(csv2_reader)
    merged_data.sort(key=lambda x: x[1])
    with open(os.path.join(data, filename), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(merged_data)

def round_to_4(value):
    return round(float(value), 4)

def convert_gcag_to_csv(gcagDictMonthly, gcagDictAnnual):
    """
        Converts the gcag data to CSV format
    """
    source = 'gcag'
    dict_temp_annual = {'Source': [], 'Year': [], 'Mean': []}
    dict_temp_monthly = {'Source': [], 'Year': [], 'Mean': []}
    for elem in gcagDictAnnual:
        dict_temp_annual['Source'].append(source)
        dict_temp_annual['Year'].append(elem[0])
        dict_temp_annual['Mean'].append(round_to_4(elem[1]))
    for elem in gcagDictMonthly:
        dict_temp_monthly['Source'].append(source)
        dict_temp_monthly['Year'].append(elem[0])
        dict_temp_monthly['Mean'].append(round_to_4(elem[1]))
    
    for csv_files, dataset in zip(['annual_gcag.csv', 'monthly_gcag.csv'], [dict_temp_annual, dict_temp_monthly]):
        with open(os.path.join(tmp, csv_files), "w", newline="\n") as f:
            w = csv.DictWriter(f, fieldnames=dataset.keys())
            w.writeheader()
            for row in zip(*dataset.values()):
                w.writerow(dict(zip(dataset.keys(), row)))

def convert_gistemp_to_csv(gistempDict):
    """
        Converts the GISTEMP data to CSV format
    """
    source = 'GISTEMP'
    dict_temp_annual = {'Source': [], 'Year': [], 'Mean': []}
    dict_temp_monthly = {'Source': [], 'Year': [], 'Mean': []}
    for elem in gistempDict:
        if '***' in elem:
            break
        # Annual_parsing
        dict_temp_annual['Source'].append(source)
        dict_temp_annual['Year'].append(elem[0])
        annual_mean = round_to_4(sum([float(s) for s in elem[1:13]]) / 12)
        dict_temp_annual['Mean'].append(annual_mean)

        # Monthly_parsing
        month = 1
        for value in elem[1:13]:
            if '***' in elem:
                break
            dict_temp_monthly['Source'].append(source)
            dict_temp_monthly['Year'].append(elem[0] + '-' + str(month).zfill(2))
            dict_temp_monthly['Mean'].append(float(value))
            month += 1
    
    for csv_files, dataset in zip(['annual_gistemp.csv', 'monthly_gistemp.csv'], [dict_temp_annual, dict_temp_monthly]):
        with open(os.path.join(tmp, csv_files), "w", newline="\n") as f:
            w = csv.DictWriter(f, fieldnames=dataset.keys())
            w.writeheader()
            for row in zip(*dataset.values()):
                w.writerow(dict(zip(dataset.keys(), row)))

def process_csv(url):
    """
        Fetches and processes the CSV data from the URL
    """
    try:
        with requests.Session() as s:
            download = s.get(url, headers=headers)
            decoded_content = download.content.decode('utf-8')

            cr = csv.reader(decoded_content.splitlines(), delimiter=',')

            my_list = list(cr)

            return my_list
    except requests.exceptions.RequestException as e:
        print(f"Error message: {e}")
        return None

def process_gistemp():
    if not os.path.exists(tmp):
        os.makedirs(tmp)
    
    #Step 1: Fetch and process the GISTEMP data from the URL
    print('Step 1: Fetching and processing GISTEMP data...')
    temp_data = process_csv(GISTEMP_URL)
        
    # Step 2: Extract the first 13 elements of each list and remove unnecessary headers
    print('Step 2: Extracting relevant data...')
    processed_data = [elem[:13] for elem in temp_data if len(elem) > 12][1:]
        
    # Step 3: Convert the processed data to CSV format
    print('Step 3: Converting processed data to CSV format...')
    convert_gistemp_to_csv(processed_data)
        
    print('GISTEMP data processing and conversion complete!')
    
    #Step 4: Fetch and process the HADCRUT data from the URL
    print('Step 4: Fetching and processing HADCRUT data...')
    gcag_monthly = process_csv(GCAG_URL_monthly)
    gcag_annual = process_csv(GCAG_URL_annual)
        
    # Step 5: Extract the first 2 elements of each list and remove unnecessary headers
    print('Step 5: Extracting relevant data...')
    processed_gcag_monthly = [elem[:2] for elem in gcag_monthly if len(elem) > 2][1:]
    processed_gcag_annual = [elem[:2] for elem in gcag_annual if len(elem) > 2][1:]

    # Step 6: Convert the processed data to CSV format
    print('Step 6: Converting processed data to CSV format...')
    convert_gcag_to_csv(processed_gcag_monthly, processed_gcag_annual)
        
    print('GISTEMP data processing and conversion complete!')

    # Step 7: Merge the GISTEMP and HADCRUT data into a single CSV file
    print('Step 7: Merging GISTEMP and HADCRUT data...')
    merge_csv_sorted(os.path.join(tmp, annual_gistemp), os.path.join(tmp, annual_gcag), 'annual.csv')
    merge_csv_sorted(os.path.join(tmp, monthly_gistemp), os.path.join(tmp, monthly_gcag), 'monthly.csv')

    print('Data merging complete!')

    # Step 8: Remove unnecessary files
    print('Step 8: Removing unnecessary files...')
    shutil.rmtree(tmp)
        
if __name__ == '__main__':
    process_gistemp()