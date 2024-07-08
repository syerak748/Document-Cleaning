from extractTextOCR import extractOCR, get_file_paths_lists
from pdfanddoc_extraction import extractInfo
from output_utils import write_to_files, load_config
from ConfigFiles.config import GLOBAL_CONFIG, CONFIG_SHEET
import pandas as pd
from msg_extraction import extract_msg_info
from utility2 import extractConfig
import os


def extractPDFandDoc(pdf_doc_filepaths):
    ocr_extract = extractOCR(pdf_doc_filepaths)
    config_path = 'config.json'
    config = load_config(config_path)
    for item in ocr_extract.items():
        appnum, classification, classdesc, corrDate, subject, summary = extractInfo(item[0], item[1])
        write_to_files(config,appnum, item[0], corrDate, subject, classification, classdesc)

def extractMSG(msg_filepaths, internal_domains):
    config_path = 'config.json'
    config = load_config(config_path)
    for msgFile in msg_filepaths:
       app_num,sent_date, subject, classification, classdesc = extract_msg_info(msgFile, internal_domains)
       write_to_files(config,app_num, msgFile, str(sent_date), subject, classification, classdesc)
        

if __name__ == "__main__":
    general_config = pd.read_excel(GLOBAL_CONFIG,sheet_name="General Configuration")
    configData = extractConfig(GLOBAL_CONFIG, CONFIG_SHEET)
    Internal_Domains = configData[1]['Internal_Domains'].split(',')
    dir_path = general_config.loc[general_config['Name']=="Directory","value"].values[0]
    dir_path_list=dir_path.split(',')
    pdf_doc_filepaths, msg_filepaths = get_file_paths_lists(dir_path_list)
    config_path = 'config.json'
    config = load_config(config_path)
    output_csv = config['output_csv']
    output_excel = config['output_excel']
    try:
        os.remove(output_excel)
        os.remove(output_csv)
    except FileNotFoundError:
        pass
    
    extractPDFandDoc(pdf_doc_filepaths)
    extractMSG(msg_filepaths, Internal_Domains)
    
    