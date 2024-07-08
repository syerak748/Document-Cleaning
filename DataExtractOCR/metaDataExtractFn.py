import fitz
import datefinder
import re
#from shortPythonScript import getKeyWords
import json
from ConfigFiles.config import GLOBAL_CONFIG, CLASSIFICATION_KEYWORD_SHEET, CONFIG_SHEET, dirPath
from utility2 import extractConfig, normalize_text2, getPDFPages
from pathlib import Path
from datetime import datetime
from pprint import pprint

#pdfdoc = fitz.open("Case 1/20180820_FDA-AAA_Cou_Approval of S0068 Dotatate DMF update NETSPOT.pdf")
'''
allText = ""
for pagenum in range(len(pdfdoc)):
    page = pdfdoc.load_page(pagenum)
    text = page.get_text("text")
    allText += text
    print("extracted text :", text)'''
    
#print("All text from pdf \n", allText)

def extractApplicationNumber(text):
    appNumPattern = r'\b[A-Z]{3}\s*\d{6}\b'
    #firstLine = text.split('\n')[0]
    match = re.search(appNumPattern, text)
    if match:
        appNum = match[0]
        #print(f'Found Application Number : {appNum}')
    else:
        pass
        #print(f'No application number found')
    return match.group() if match else None

def classifyDoc(text, keyWordsData, chooseFn = "classification"):
    """_summary_
    Classifies doc and can also return subject/summary
    Args:
        chooseFn (str, optional): Just choose what you want the function to return; summary or classification. Defaults to "classification". 

    Returns:
        _type_: returns string of summary or returns external/internal
    """
    text = normalize_text2(text)
    for row in keyWordsData:
        #print(row['Keywords'])
        if normalize_text2(row['Keywords']) in text:
            #print(row)
            #print("Found : ",row['Keywords'])
            docClassification = row['Category']
            #print("Category : ", row['Category'])
            if chooseFn == "classification":
                return docClassification
            elif chooseFn == "Summary":
                return row['Keywords']
         


def corrDate(text):
    date_patterns = [
        r'\b(\d{1,2}/\d{1,2}/\d{4})(?:[^\d]|$)',  # MM/DD/YYYY or M/DD/YYYY
        r'\b(\d{4})-(\d{2})-(\d{2})(?:[^\d]|$)',  # YYYY-MM-DD
        r'\b(\d{2})-(\d{2})-(\d{4})(?:[^\d]|$)',  # DD-MM-YYYY
        r'\b(\d{4})/(\d{2})/(\d{2})(?:[^\d]|$)',  # YYYY/MM/DD
        r'\b(\w+ \d{1,2}, \d{4})(?:[^\d]|$)',     # Month DD, YYYY
    ]

    combined_pattern = '|'.join(date_patterns)
    date_pattern = re.compile(combined_pattern)

    matches = date_pattern.findall(text)
    if matches:
        # Parse the dates and keep the last valid one
        for match in reversed(matches):
            date_str = ' '.join(filter(None, match)).strip()
            #print(f"Trying to parse date: {date_str}")
            for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d', '%B %d, %Y'):
                try:
                    parsed_date = datetime.strptime(date_str, fmt).date()
                    #print(f"Successfully parsed date: {parsed_date}")
                    return parsed_date
                except ValueError:
                    continue
    return None
#filepaths = ('Case 1/20180820_FDA-AAA_Cou_Approval of S0068 Dotatate DMF update NETSPOT.pdf', 'Case 1/20201120_CDER contact.pdf', 'Case 1/20230104 Final FDA Minutes for Dec082022 Type C.pdf', 'Case 1/Colorado_Advice-Information Request IND 123456 final_Advice-information request.pdf', 'Case 1/IND 123456 ACK Letter.pdf', 'Case 1/IND 123456 clinical hold letter.pdf')

'''
def dataExtractCombined(folderPath):
    mainData = []
    
    for filepath in folderPath.iterdir():
        if filepath.is_file():
            #print(f"DOC : {filepath.name}")
            PagesText = getPDFPages(filepath)
            pdfdoc = fitz.open(filepath)
            firstPage = pdfdoc.load_page(0)
            firstPageText = firstPage.get_text("text")
            lastPage = pdfdoc.load_page(-1)
            lastPageText = lastPage.get_text("text")
            Application_Number = (extractApplicationNumber(PagesText))
            keywordData = extractConfig(GLOBAL_CONFIG, CLASSIFICATION_KEYWORD_SHEET)
            Classification = classifyDoc(PagesText, keywordData)
            Summary = classifyDoc(PagesText, keywordData, chooseFn="Summary")
            CorrDate = corrDate(PagesText)
            #print(Classification,'\n',Summary,'\n',CorrDate,'\n','-'*70,sep = "")
            dataDict = {
                'Filename' : filepath.name,
                'Application_Number' : Application_Number,
                'Classification' : Classification,
                'Correspondance Date' : str(CorrDate),
                'Subject' : Summary,
                'Summary' : Summary,
                #'Delimiter' : '-------------------------------------------------------------------'
            }   
            mainData.append(dataDict)
        else:
            raise FileNotFoundError("Not the correct folder doesnt have files in it")
    return mainData

      
#metaData = dataExtractCombined(dirPath)

for dict in metaData:
    print('-'*70)
    pprint(dict)'''
#IND 123456 ACK, NO MATCHING KEYWORD
#IND CLINICAL HOLD NO MATCHING KEYWORD