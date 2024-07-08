import json
from requests import post, get
import time
from output_utils import load_config
from azure_Asyncnew import get_text_from_ocr
import json
from requests import post, get
import time
 
def post_method(input_file: str, endpoint: str, apim_key: str, model_id: str, API_version: str) -> str:
    post_url = f"{endpoint}/documentintelligence/documentModels/{model_id}:analyze?_overload=analyzeDocument&api-version=2024-02-29-preview"
    print(post_url)
    headers = {
        #"Content-Type": "application/pdf",  # Adjust content type as needed # FOR PDF
        #"Content-Type":"application/vnd.openxmlformats-officedocument.wordprocessingml.document", #FOR DOCX
        "Content-Type":"application/octet-stream",        #BOTH FOR PDF AND DOCX
        "Ocp-Apim-Subscription-Key": apim_key
    }
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
        resp = post(url=post_url, data=data_bytes, headers=headers, params=params)
        if resp.status_code != 202:
            print("POST analyze failed:\n%s" % json.dumps(resp.json()))
            return ""
        get_url = resp.headers["operation-location"]
        print("POST request successful.")
        return get_url
    except Exception as e:
        print("POST analyze failed:", str(e))
        return ""
 
def get_method(get_url: str, apim_key: str, output_file_path: str) -> dict:
    n_try = 1
    n_tries = 80
    resp_json ={}
   
    try:
 
        while n_try <= n_tries:
 
       
            print(f"Attempt {n_try}")
            resp = get(url=get_url, headers={"Ocp-Apim-Subscription-Key": apim_key})
            resp_json = resp.json()
            if resp.status_code != 200:
                print("GET analyze results failed:\n%s" % json.dumps(resp_json))
            status = resp_json["status"]
            if status == "succeeded":
                #config_path=output_file_path+"/analsys.json"
                with open(output_file_path, "w") as f:
                    json.dump(resp_json, f, indent=4)
                print("Analysis results saved to", output_file_path)
                return resp_json
            if status == "failed":
                print("Analysis failed:\n%s" % json.dumps(resp_json))
            time.sleep(1)
            n_try += 1
        return resp_json
    except Exception as e:
            print("GET analyze results failed:", str(e))
            return resp_json


if __name__ == "__main__":
    configOCRdict = load_config("configOCR.json")
    inputF = "Case 1/Approval Letter.pdf"
    #inputdocx = "Case 1/Meeting Minutes.docx"
    post_dict = {}
    post_dict[inputF] = post_method(inputF, configOCRdict['endpoint'], configOCRdict['apim_key'], configOCRdict['model_id'], configOCRdict['API_version'])
    print(post_dict)
    url = post_dict[inputF]
    raw_json = get_method(url, configOCRdict['apim_key'], "rawFile2.json")
    textDict = get_text_from_ocr(raw_json)
    with open("sample.txt", "w") as f:
        f.write("raw Json file as str\n")
        f.write(str(textDict))
    