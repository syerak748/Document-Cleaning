import json
import os
import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from datetime import datetime, timedelta

def load_config(config_path):
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    return config

def excel_date_to_date(excel_date):
    return datetime(1899, 12, 30) + timedelta(days=excel_date)

def write_to_files(config, app_num, file_path,sent_date, subject, classification, classification_desc):
    output_excel = config['output_excel']
    output_csv = config['output_csv']
    headers = config['headers']
    file_path = file_path
    file_name = os.path.basename(file_path)
    app_num  = app_num

    # Convert the date if it is in Excel serial format
    if isinstance(sent_date, (int, float)):
        sent_date = excel_date_to_date(sent_date).strftime('%Y-%m-%d')

    data = {
        "File Path": [file_path],
        "File Name": [file_name],
        #"File Type": [filetype],
        "Application Number": [app_num],
        "Event/Correspondence Date": [sent_date],
        "Correspondence Type": [classification],
        "Correspondence Type Description": [classification_desc],
        "Description": [subject],
        "Meaningful Summary": [subject]
    }

    df = pd.DataFrame(data)

    # Write to Excel file
    if not os.path.isfile(output_excel):
        df.to_excel(output_excel, index=False, header=headers)
    else:
        with pd.ExcelWriter(output_excel, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            existing_df = pd.read_excel(output_excel)
            startrow = len(existing_df) + 1
            df.to_excel(writer, index=False, header=False, startrow=startrow)

    # Write to CSV file
    if not os.path.isfile(output_csv):
        df.to_csv(output_csv, index=False, header=headers)
    else:
        df.to_csv(output_csv, mode='a', index=False, header=False)