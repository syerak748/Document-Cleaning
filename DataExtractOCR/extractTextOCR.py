import os
from typing import KeysView
import pandas as pd
import json
from Config import *
#from utility import filer_file,get_category,get_metadata_extraction_wrapper,ocr_similarity_check_batch,saving_files,confidence_score,dict_to_list,get_redundant_file
# from Config import UPLOAD_FOLDER, DUPLICATES_FOLDER, OUTPUT_DIR, DATA, GLOBAL_CONFIG, PAYLOAD_FILE,CLASSES,BATCH_DATA
from ConfigFiles.config import GLOBAL_CONFIG
from filecmp import cmp
# from hashing import hashing_duplicate_check
from azure_Asyncnew import doc_extract, get_full_text_from_pagewise
#from conversion import json_to_excel
# from Employee_assginement import employee_mapper
import logging
import copy
import re
from datetime import datetime
 
general_config = pd.read_excel(GLOBAL_CONFIG,sheet_name="General Configuration")
metadata_config=pd.read_excel(GLOBAL_CONFIG,sheet_name="Metadata Classification")
global_config_df = pd.read_excel(GLOBAL_CONFIG,sheet_name='Doc Classification')
 
dir_path = general_config.loc[general_config['Name']=="Directory","value"].values[0]
dir_path_list=dir_path.split(',')
 
def get_file_paths_lists(dir_path_list):
    pdf_doc_files = []
    msg_files = []
    
    for dir_path in dir_path_list:
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                abs_file_path = os.path.join(root, file)
                if file.lower().endswith(('.pdf', '.doc', '.docx')):
                    pdf_doc_files.append(abs_file_path)
                elif file.lower().endswith('.msg'):
                    msg_files.append(abs_file_path)
    
    return pdf_doc_files, msg_files
 
logging.info("Get file path for existing files")



def extractOCR(file_list):
    
    pdf_doc_files, msg_files =get_file_paths_lists(dir_path_list = dir_path_list)
    #print(pdf_doc_files)
    ocr_extract = doc_extract(file_list)
 
    x = ocr_extract.values()
    x = list(x)
    combined_document = []
    for doc_dict in x:
        combined_text = " ".join(doc_dict.values())
        combined_document.append(combined_text)
    #combined_document
 
    for i,k in enumerate(ocr_extract):
        ocr_extract[k] = combined_document[i]
    return ocr_extract

#mainDict = extractOCR()
#print(mainDict)

