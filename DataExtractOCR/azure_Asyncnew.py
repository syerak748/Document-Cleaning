from ConfigFiles.config import ENDPOINT, KEY, MODEL_ID, API_VERSION
import os
import sys
import time
import json
import fitz
import logging
from requests import get, post
#from PyPDF2 import PdfFileWriter, PdfFileReader
from output_utils import load_config

class AzureRunAnalysis:
    def __init__(self, file_type: str) -> None:
        self.file_type = file_type

    def initialize(self):

        self.endpoint = ENDPOINT
        self.apim_key = KEY
        self.model_id = MODEL_ID
            
        self.post_url = f"{self.endpoint}/documentintelligence/documentModels/{self.model_id}:analyze?_overload=analyzeDocument&api-version=2024-02-29-preview"
        '''
        self.params = {
            "includeTextDetails": True
        }
        '''

        self.headers = {
            #"Content-Type": "application/pdf",  # Adjust content type as needed # FOR PDF
            #"Content-Type":"application/vnd.openxmlformats-officedocument.wordprocessingml.document", #FOR DOCX
            "Content-Type":"application/octet-stream",        #BOTH FOR PDF AND DOCX
            "Ocp-Apim-Subscription-Key": self.apim_key
        }
        
    def post_method(self, input_file: str) -> str:
        post_url = f"{self.endpoint}/documentintelligence/documentModels/{self.model_id}:analyze?_overload=analyzeDocument&api-version=2024-02-29-preview"
        #print(self.post_url)
        
        params = {}
 
        try:
            with open(input_file, "rb") as f:
                data_bytes = f.read()
                #print(data_bytes)
        except IOError:
            print("Input file not accessible.")
            return ""
 
        try:
            print("Sending POST request to Form Recognizer API...")
            resp = post(url=post_url, data=data_bytes, headers=self.headers, params=params)
            if resp.status_code != 202:
                print("POST analyze failed:\n%s" % json.dumps(resp.json()))
                return ""
            get_url = resp.headers["operation-location"]
            print("POST request successful.")
            return get_url
        except Exception as e:
            print("POST analyze failed:", str(e))
            return ""

    def get_method(self, get_url: str) -> dict:
        n_try = 1
        n_tries = 80
        resp_json ={}
   
        try:
 
            while n_try <= n_tries:
 
       
                print(f"Attempt {n_try}")
                resp = get(url=get_url, headers={"Ocp-Apim-Subscription-Key": self.apim_key})
                resp_json = resp.json()
                if resp.status_code != 200:
                    print("GET analyze results failed:\n%s" % json.dumps(resp_json))
                status = resp_json["status"]
                if status == "succeeded":
                    #config_path=output_file_path+"/analsys.json"
                    '''
                    with open(output_file_path, "w") as f:
                        json.dump(resp_json, f, indent=4)
                    print("Analysis results saved to", output_file_path)'''
                    return resp_json
                if status == "failed":
                    print("Analysis failed:\n%s" % json.dumps(resp_json))
                time.sleep(1)
                n_try += 1
            return resp_json
        except Exception as e:
            print("GET analyze results failed:", str(e))
            return resp_json

def get_file_type(filename: str) -> str:
    try:

        fileExt = os.path.splitext(filename)[-1]
        if fileExt == ".pdf":
            return "application/pdf"
        elif fileExt == ".docx":
            return "application/docx"
        elif fileExt == ".msg":
            return "application/msg"
        elif fileExt == ".jpeg" or fileExt == ".jpg":
            return "image/jpeg"
        elif fileExt == ".png":
            return "image/png"
        elif fileExt == ".tiff":
            return "image/tiff"
        elif fileExt == ".bmp":
            return "image/bmp"
    except Exception as e: 
        print(e)
        return " "

def get_text_from_ocr(json_data: dict) -> dict:
    raw_data = json_data["analyzeResult"]["pages"]
    page_wise_ocr = {}
    for page in raw_data:
        page_wise_text_lst = []
        words = page["words"]
        for word in words:
            '''words = line["words"]
            for word in words:'''
            page_wise_text_lst.append(word["content"])
                # print(page_wise_text_lst)
        page_wise_ocr[page["pageNumber"]] = " ".join(page_wise_text_lst)
    return page_wise_ocr

def get_full_text_from_pagewise(page_wise_ocr: dict) -> str:
    full_text = " ".join([value for key, value in page_wise_ocr.items() if key !="metadata_info"])
    return full_text
'''
def doc_extract_old(file_list : list) -> dict:
    start_time = time.time()
    post_dict = {}
    OCR_dict = {}
    for entry in file_list:
        res = os.path.basename(entry)
        file_type = get_file_type(res)

        azure_analysis = AzureRunAnalysis(file_type)
        azure_analysis.initialize()
        
        # post_dict[entry] = azure_analysis.post_method(entry)
        
    for filename, url in post_dict.items():
        # full_text = []
        resp_json = azure_analysis.get_method(url)
        
        # for read_result in resp_json["analyzeResult"]["readResults"]:
            
        #     for line in read_result["lines"]:
        #         # full_text.append(line["text"])
        pagewise_ocr = get_text_from_ocr(resp_json)
        
        OCR_dict[filename] = pagewise_ocr
    # print("ocr dict", OCR_dict)
    # print("page wise", pagewise_ocr)
    print("Doc extracts --- %s seconds ---" % (time.time() - start_time))
    return OCR_dict
    # return OCR_dict
    
  '''  
def doc_extract(file_list : list) -> dict:
    start_time = time.time()
    post_dict = {}
    OCR_dict = {}
    for entry in file_list:
        res = os.path.basename(entry)
        file_type = get_file_type(res)
        # print(file_type)
        azure_analysis = AzureRunAnalysis(file_type)
        azure_analysis.initialize()
        
        post_dict[entry] = azure_analysis.post_method(entry) #api_calling post fn
        
    for filename, url in post_dict.items():
        # full_text = []
        resp_json = azure_analysis.get_method(url) #api_calling get function
        # print('resp_json Done')
        # for read_result in resp_json["analyzeResult"]["readResults"]:
            
        #     for line in read_result["lines"]:
        #         # full_text.append(line["text"])
        #print(resp_json)
        pagewise_ocr = get_text_from_ocr(resp_json)
        # print("page wise", pagewise_ocr)
        # print('pagewise_ocr:/n',pagewise_ocr)
        OCR_dict[filename] = pagewise_ocr
    # print("ocr dict", OCR_dict)
    
    #print("Doc extracts --- %s seconds ---" % (time.time() - start_time))
    #print('OCR_dict:\n',OCR_dict)
    return OCR_dict
    # return OCR_dict

def doc_extract_single(file_path) -> dict:
    start_time = time.time()
    post_dict = {}
    OCR_dict = {}
    
       
    res = os.path.basename(file_path)
    file_type = get_file_type(res)

    azure_analysis = AzureRunAnalysis(file_type)
    azure_analysis.initialize()
    
    post_dict[file_path] = azure_analysis.post_method(file_path)

    for filename, url in post_dict.items():
        # full_text = []
        resp_json = azure_analysis.get_method(url)
        #return resp_json
       
        # for read_result in resp_json["analyzeResult"]["readResults"]:
            
        #     for line in read_result["lines"]:
        #         # full_text.append(line["text"])
        pagewise_ocr = get_text_from_ocr(resp_json)
        
        OCR_dict[filename] = pagewise_ocr
    # print("ocr dict", OCR_dict)
    # print("page wise", pagewise_ocr)
    print("Doc extracts --- %s seconds ---" % (time.time() - start_time))
    with open("sample.json", "w") as outfile:
        json.dump(OCR_dict, outfile)
    return OCR_dict
    # return OCR_dict
    
'''jsondict = load_config("Colorado_Advice-Information Request IND 123456 final_Advice-information request.pdf.json")
text = get_text_from_ocr(jsondict)
with open("sample.txt", "w") as f:
    f.write(str(text))
print(text)'''