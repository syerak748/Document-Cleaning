import extract_msg
from datetime import datetime
import re
from metaDataExtractFn import classifyDoc
from ConfigFiles.config import CLASSIFICATION_KEYWORD_SHEET, GLOBAL_CONFIG, CONFIG_SHEET
from utility2 import extractConfig



def extract_msg_info(file_path, InternalDomains):
    msg = extract_msg.Message(file_path)
    sent_date = msg.date
    Sender = msg.sender
    
    #Sender = "<kshitij748@gmail.co.in>"
    senderdomain = Sender[:-1].split('@')[1].strip()
    
    #print(Sender, senderdomain)
    Receiver = msg.to
    recdomain = Receiver[:-1].split('@')[1].strip()
    #print(Receiver, recdomain)
    # Remove timezone information
    if sent_date.tzinfo is not None:
        sent_date = sent_date.replace(tzinfo=None)

    # Format date to ISO 8601 format (YYYY-MM-DD)
    formatted_date = sent_date.strftime('%Y-%m-%d')

    subject = msg.subject
    keywordsData = extractConfig(GLOBAL_CONFIG, CLASSIFICATION_KEYWORD_SHEET)
    print(InternalDomains)
    
    if str(senderdomain) in InternalDomains:
        classification = "Internal" 
    else:
        classification = "External"
    #classification = classifyDoc(Sender, keywordsData)
    #if classification != "Internal":
        #classification = "External"
    # Extract body text from the .msg file
    body = msg.body

    # Extract application number with potential 3-letter code prefix
    app_num_pattern = re.compile(r'[A-Z]{3} \d+')
    app_number_match = app_num_pattern.search(body)
    #classification = ""
    classification_description = ""
    if app_number_match:
        app_number = app_number_match.group(0)
    else:
        app_number = 'Application number not found'
    
    if classification == "External":
        ClassDesc = "Submitted"
    else:
        ClassDesc = "Not Submitted"
    
    return app_number, formatted_date, subject, classification, ClassDesc

