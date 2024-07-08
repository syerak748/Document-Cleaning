import re
import os
import openpyxl
import pandas as pd
from configFiles.config import GLOBAL_CONFIG, USECASE3
from pprint import pprint
def normalize_text(text):
    """_summary_
    Removes all whitespaces from the text
    """
    text = re.sub(r'\W+', '', text)
    text = text.lower()
    return text

def fileType(filepath):
    """_summary_
    Gets File Type
    """
    filenamebase = os.path.basename(filepath)
    return os.path.splitext(filenamebase)[1]

def fileName(filepath):
    """_summary_
    Gets File Name
    """
    filenamebase = os.path.basename(filepath)
    return os.path.splitext(filenamebase)[0]

def fileSize(filepath):
    """_summary_
    Gets File Size
    """
    filesize = os.path.getsize(filepath)//1024
    return filesize

def extractConfig(excelPath, sheetName):
    """_summary_
    Extracts all the data from the Global_Config
    """
    workbook = openpyxl.load_workbook(excelPath)
    sheet = workbook[sheetName]

    # Create a list to hold the data
    data_list = []

    # Iterate over the rows in the sheet starting from the second row
    for row in sheet.iter_rows(min_row=2, values_only=True):
        if row[0] is not None and row[1] is not None:
            if row[0] == 'Output_Headers':
                row_dict = {row[0] : eval(row[1])}
                data_list.append(row_dict)
                continue
            row_dict = {row[0]: row[1]}
            data_list.append(row_dict)
    
    
    return data_list
