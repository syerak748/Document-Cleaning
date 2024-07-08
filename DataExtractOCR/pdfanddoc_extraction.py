from metaDataExtractFn import classifyDoc, corrDate, extractApplicationNumber
from utility2 import getPDFPages, extractConfig
from ConfigFiles.config import GLOBAL_CONFIG, CLASSIFICATION_KEYWORD_SHEET, CONFIG_SHEET
from pprint import pprint
from pathlib import Path

def extractInfo(filepath, PagesText):
    #print(f"DOC : {filepath.name}")
    #PagesText = getPDFPages(filepath)
    filepathobj = Path(filepath)
    Application_Number = (extractApplicationNumber(PagesText))
    keywordData = extractConfig(GLOBAL_CONFIG, CLASSIFICATION_KEYWORD_SHEET)
    Classification = classifyDoc(PagesText, keywordData)
    if Classification == "External":
        ClassDesc = "Submitted"
    else:
        ClassDesc = "Not Submitted"
    Summary = classifyDoc(PagesText, keywordData, chooseFn="Summary")
    CorrDate = corrDate(PagesText)
    #print(Classification,'\n',Summary,'\n',CorrDate,'\n','-'*70,sep = "")
    dataDict = {
                'Filename' : filepathobj.name,
                'Application_Number' : Application_Number,
                'Classification' : Classification,
                'Classification_Description' : ClassDesc,
                'Correspondance_Date' : str(CorrDate),
                'Subject' : Summary,
                'Summary' : Summary,
            }   
    return dataDict['Application_Number'], dataDict['Classification'], dataDict['Classification_Description'], dataDict['Correspondance_Date'], dataDict['Subject'], dataDict['Summary'] 