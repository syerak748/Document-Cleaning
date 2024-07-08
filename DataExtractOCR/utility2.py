import re
import os
import openpyxl
import pandas as pd
from ConfigFiles.config import GLOBAL_CONFIG, CLASSIFICATION_KEYWORD_SHEET, CONFIG_SHEET
from pprint import pprint
import fitz
def normalize_text(text):
    """
    removes all whitespaces from text
    """
    text = re.sub(r'\W+', '', text)
    text = text.lower()
    return text

def normalize_text2(text):
    """_summary_
    removes all special character from string
    """
    normalized_text = re.sub(r'[/\-_,]', ' ', text.lower())
    return normalized_text
 
def fileType(filepath):
    """_summary_

    returns filetype
    """
    filenamebase = os.path.basename(filepath)
    return os.path.splitext(filenamebase)[1]

def fileName(filepath):
    """_summary_

    returns Filename
    """
    filenamebase = os.path.basename(filepath)
    return os.path.splitext(filenamebase)[0]

def extractConfig(excelPath, sheetName):
    """_summary_

    Extracts data from globalConfig
    """
    if sheetName == CLASSIFICATION_KEYWORD_SHEET:
        
        # Create a list to hold the data
        data_list = []
        # Iterate over the rows in the sheet starting from the second row
        df = pd.read_excel(excelPath, sheet_name=sheetName)
         #Convert the DataFrame to a list of dictionaries
        data_list = df.to_dict(orient='records')
        # Print the result
        return data_list
    elif sheetName == CONFIG_SHEET:
        data_list = []
        workbook = openpyxl.load_workbook(excelPath)
        sheet = workbook[sheetName]
        # Iterate over the rows in the sheet starting from the second row
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row[0] is not None and row[1] is not None:
                row_dict = {row[0]: row[1]}
                data_list.append(row_dict)
    
    
        return data_list

#inputConfig = extractConfig(GLOBAL_CONFIG, CLASSIFICATION_KEYWORD_SHEET)

#pprint(inputConfig)
#print(inputConfig[0]['Input_Directory'])
#print(inputConfig[1]['Receipt_FileTypes'])
#print(inputConfig[2]['Validation_Reports_FileTypes'])

def dataNormalisationForExport(missingDirectories, main_folder):
    """_summary_
    Prepares data for it to be exported to csv and excel
    """
    data = []
    for firstLevelPath, missings in missingDirectories.items():
        firstLevelName = os.path.basename(firstLevelPath)
        existingDirs = [d for d in os.listdir(firstLevelPath) if os.path.isdir(os.path.join(firstLevelPath, d)) and d.isdigit()]
        existingDirs.sort()
        
        
        if len(missings)>1:
            missingStr = ', '.join(str(subdir) for subdir in missings)  
        elif len(missings) == 1:
            missingStr = str(missings[0])+','
        else:
            missingStr = 'None'
        existingStr = ', '.join(existingDirs)
        data.append([firstLevelName, firstLevelPath, existingStr, len(existingDirs), missingStr, len(missings)])
                                #add a logging.info statement

    return data

def getPDFPages(filepath):
    pdfdoc = fitz.open(filepath)
    all_text = ""
    for page_num in range(len(pdfdoc)):
        page = pdfdoc.load_page(page_num)
        all_text += page.get_text("text")
    return all_text