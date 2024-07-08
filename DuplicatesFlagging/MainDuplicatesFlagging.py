import os
from os import stat
import hashlib
import csv
from openpyxl import Workbook
from openpyxl.styles import Alignment
import logging
import configFiles.DuplicateTags as DuplicateTags
import extract_msg
from utilityFn import normalize_text
from utilityFn import fileType, fileName, extractConfig, fileSize
from configFiles.config import GLOBAL_CONFIG, USECASE3
import fitz
import re
from itertools import combinations
import argparse


logging.basicConfig(level = logging.INFO, format='%(asctime)s [%(levelname)s] : %(message)s')

def getHashCodePDF(filepath, hashAlgo = 'sha256'):
    """_summary_
    Gets hashcode for the content in a .pdf
    """
    hashFn = hashlib.new(hashAlgo)
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(256)
            if not data:
                break
            hashFn.update(data)
     
    hashCode = hashFn.hexdigest()
    return hashCode

def getHashCodeMSG(filepath, hashAlgo = 'sha256'): #creates hash from the whole text
    """_summary_
    Concatenates all components in a .msg file and then gets a Unique Hashcode for the whole content
    """
    hashFn = hashlib.new(hashAlgo)
    msg = extract_msg.Message(filepath)
    msgBody = msg.body
    msgSubj = msg.subject
    msgSender = msg.sender
    msgRec = msg.to
    msgDate = str(msg.date)
    if len(msg.attachments) > 0:#added new
        attachmentName = msg.attachments[0].longFilename
    else:
        attachmentName = "No attachment"
    data = msgSender+msgRec+msgDate+msgSubj+msgBody+attachmentName
    data = msg.body.encode('utf-8') #errors = 'ignore' maybe
    hashFn.update(data)
    hashCode = hashFn.hexdigest()
    return hashCode

def getFileMetadataPDF(filepath): #only for pdf to pdf check
    """_summary_
    Gets Relevant Metadata from a .pdf file like filesize, name. 
    Hashes the content of .pdf file to compare it to other .msg files
    """
    filenamebase = os.path.basename(filepath)
    filename = os.path.splitext(filenamebase)[0]
    filesize = os.path.getsize(filepath)//1024
    hashCode = getHashCodePDF(filepath)
    return {'fname' : filename, 'fsize': filesize, 'fhash': hashCode}

def getFileMetadataMSG(filepath): #only for msg to msg check
    """
    Gets Relevant Metadata from a .msg file like filesize, name. 
    Hashes the content of .msg file to compare it to other .msg files
    """
    filenamebase = os.path.basename(filepath)
    filename = os.path.splitext(filenamebase)[0]
    filesize = os.path.getsize(filepath)//1024
    hashCode = getHashCodeMSG(filepath)
    return {'fname' : filename, 'fsize': filesize, 'fhash': hashCode}

# normalise both bodies / subject is fine / normalise senders / receiver is fine but use membership(.to in pdf to) / date requires complex logic look later / attachment name is simple just use [0].longFilename in msg object part
def getAllDataMSG(filepath): #only for msg to pdf check
    """_summary_
    Extracts Relevant Data from a .msg file to be then compared to a pdf
    """
    filenamebase = os.path.basename(filepath)
    filename = os.path.splitext(filenamebase)[0]
    msg = extract_msg.Message(filepath)
    body = normalize_text(msg.body)
    subject = msg.subject
    sender = normalize_text(msg.sender)
    to = msg.to
    if len(msg.attachments) > 0:
        attachmentName = msg.attachments[0].longFilename
    else:
        attachmentName = "No attachment"
    return {
        'filename' : filename,
        'body' : body,
        'subject' : subject,
        'sender' : sender,
        'to' : to,
        'attachment' : attachmentName
    }

def pdfedMSGData(filepath): #pdf to msg compare only
    """_summary_
    Extracts Relevant Components of a .msg file that has been converted into a .pdf
    """
    try:
        filenamebase = os.path.basename(filepath)
        filename = os.path.splitext(filenamebase)[0]
        document = fitz.open(filepath)
        page = document[0]
        text = page.get_text("text")
        lines = text.split('\n')
 
        subject = lines[0].strip()
        fromLine = lines[1].strip()
        fromLine = normalize_text(fromLine)
        dateLine = lines[2].strip()
   
        toLines = []
        for i in range(4, len(lines)):
            if lines[i].startswith('1 attachments'):
                break
            toLines.append(lines[i].strip())
        toLine = " ".join(toLines)
        i += 1
        attachment = lines[i].strip()[:-1]
        if attachment == "":
            attachment = "No attachment"
        
   
        body_lines = []
        date_pattern = re.compile(r'\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2} (AM|PM)')
        for j in range(i + 1, len(lines)):
            if date_pattern.match(lines[j]):
                break
            body_lines.append(lines[j].strip())
        body = "\n".join(body_lines).strip()
        body = normalize_text(body)
 
        return {
            'filename' : filename,
            "subject": subject,
            "sender": fromLine,
            "to": toLine,
            "attachment" : attachment,
            "body": body
        }
    except IndexError as e:
        #logging.error('Not the file we want to be tested, its fine')
        pass


def getAllFilesFromDir(mainDir):
    """_summary_

    Gets all files from main directory to evaluate
    """
    filePathpdf = []
    filePathmsg = []
    allFiles = []
    for dirPath, _, filenames in os.walk(mainDir):
        try:
            for filename in filenames:
                filePath = os.path.join(dirPath, filename)
                fileType = os.path.splitext(filename)[1]
                if fileType == '.pdf':
                    filePathpdf.append(filePath)
                    allFiles.append(filePath)
                elif fileType == '.msg':
                    filePathmsg.append(filePath)
                    allFiles.append(filePath)
                else:
                    raise TypeError
        except TypeError:
            logging.error("INVALID FILE TYPE IN MAIN DIR")
   
    return filePathpdf, filePathmsg, allFiles

# normalise both bodies / subject is fine / normalise senders / receiver is fine but use membership(.to in pdf to) / date requires complex logic look later / attachment name is simple just use [0].longFilename in msg object part

def compareMsgPDF(msgData, pdfData):
    """_summary_
    Compares the different components of .msg to .pdf
    """
    bodyCheck = msgData['body'] == pdfData['body']
    subjCheck = msgData['subject'] == pdfData['subject']
    senderCheck= msgData['sender'] == pdfData['sender']
    receivCheck = msgData['to'] in pdfData['to']
    attachCheck = msgData['attachment'] == pdfData['attachment']
    return bodyCheck and subjCheck and senderCheck and receivCheck and attachCheck


def checkDuplicates(pdfFilepath, msgFilepath, allFilepathsboth):
    """_summary_

    Main function which goes through each file and checks and flags duplicates and appends it to a dictionary with all relevant data
    """
    logging.info(f'Total Files Found : {(len(pdfFilepath) + len(msgFilepath))}')
    duplicateInferenceData = []
 
    # Create hashmaps for PDF and MSG files
    pdfMetadataMap = {}
    msgMetadataMap = {}
 
    # Populate PDF metadata hashmap
    for file_path in pdfFilepath:
        metadata = getFileMetadataPDF(file_path)
        pdfMetadataMap[file_path] = metadata
 
    # Populate MSG metadata hashmap
    for file_path in msgFilepath:
        metadata = getFileMetadataMSG(file_path)
        msgMetadataMap[file_path] = metadata
 
    # PDF to PDF check
    logging.info(f'Total PDF Files : {len(pdfFilepath)}')
    for (fileA, metadataA), (fileB, metadataB) in combinations(pdfMetadataMap.items(), 2):
        if metadataA['fname'] == metadataB['fname'] and metadataA['fsize'] != metadataB['fsize'] and metadataA['fhash'] != metadataB['fhash']:
            Inference = DuplicateTags.case1
        elif metadataA['fname'] != metadataB['fname'] and metadataA['fsize'] == metadataB['fsize'] and metadataA['fhash'] == metadataB['fhash']:
            Inference = DuplicateTags.case2
        elif metadataA['fname'] == metadataB['fname'] and metadataA['fsize'] == metadataB['fsize'] and metadataA['fhash'] == metadataB['fhash']:
            Inference = DuplicateTags.case3
        else:
            continue
        duplicateInferenceData.append({
            'basefile': metadataA['fname'] + '.pdf',
            'basefilesize': metadataA['fsize'],
            'basefilepath': fileA,
            
            'Inference': Inference,
            'testfile': metadataB['fname'] + '.pdf',
            'testfilesize': metadataB['fsize'],
            'testfilepath': fileB,
            
        })
 
    # MSG to MSG check
    logging.info(f'Total MSG Files : {len(msgFilepath)}')
    for (fileA, metadataA), (fileB, metadataB) in combinations(msgMetadataMap.items(), 2):
        if metadataA['fname'] == metadataB['fname'] and metadataA['fsize'] != metadataB['fsize'] and metadataA['fhash'] != metadataB['fhash']:
            Inference = DuplicateTags.case1
        elif metadataA['fname'] != metadataB['fname'] and metadataA['fsize'] == metadataB['fsize'] and metadataA['fhash'] == metadataB['fhash']:
            Inference = DuplicateTags.case2
        elif metadataA['fname'] == metadataB['fname'] and metadataA['fsize'] == metadataB['fsize'] and metadataA['fhash'] == metadataB['fhash']:
            Inference = DuplicateTags.case3
        else:
            continue
        duplicateInferenceData.append({
            'basefile': metadataA['fname'] + '.msg',
            'basefilesize': metadataA['fsize'],
            'basefilepath': fileA,
            
            'Inference': Inference,
            'testfile': metadataB['fname'] + '.msg',
            'testfilesize': metadataB['fsize'],
            'testfilepath': fileB,
            
        })
 
    # MSG to PDF check
    for fileA, metadataA in msgMetadataMap.items():
        for fileB, metadataB in pdfMetadataMap.items():
            if fileType(fileA) == fileType(fileB):
                continue
 
            if fileType(fileA) == '.pdf':
                fileDataA = pdfedMSGData(fileA)
                fileDataB = getAllDataMSG(fileB)
                if fileDataA is None:
                    if fileName(fileA) == fileName(fileB):
                        Inference = DuplicateTags.case1
                        duplicateInferenceData.append({
                            'basefile': fileName(fileA)+'.pdf',
                            'basefilesize': fileSize(fileA),
                            'basefilepath': fileA,
                            
                            'Inference': Inference,
                            'testfile': fileName(fileB)+'.msg',
                            'testfilesize': fileSize(fileB),
                            'testfilepath': fileB,
                            
                        })
                        continue
                    else:
                        continue
 
                if fileDataA['filename'] == fileDataB['filename'] and not compareMsgPDF(fileDataB, fileDataA):
                    Inference = DuplicateTags.case1
                elif fileDataA['filename'] != fileDataB['filename'] and compareMsgPDF(fileDataB, fileDataA):
                    Inference = DuplicateTags.case2
                elif fileDataA['filename'] == fileDataB['filename'] and compareMsgPDF(fileDataB, fileDataA):
                    Inference = DuplicateTags.case3
                else:
                    continue
                duplicateInferenceData.append({
                    'basefile': fileDataA['filename']+'.pdf',
                    'basefilesize': fileSize(fileA),
                    'basefilepath': fileA,
                    
                    'Inference': Inference,
                    'testfile': fileDataB['filename']+'.msg',
                    'testfilesize': fileSize(fileB),
                    'testfilepath': fileB,
                    
                })
            elif fileType(fileA) == '.msg':
                fileDataA = getAllDataMSG(fileA)
                fileDataB = pdfedMSGData(fileB)
                if fileDataB is None:
                    if fileName(fileB) == fileName(fileA):
                        Inference = DuplicateTags.case1
                        duplicateInferenceData.append({
                            'basefile': fileName(fileA) + '.pdf',
                            'basefilesize': fileSize(fileA),
                            'basefilepath': fileA,
                            
                            'Inference': Inference,
                            'testfile': fileName(fileB) + '.msg',
                            'testfilesize': fileSize(fileB),
                            'testfilepath': fileB,
                            
                        })
                        continue
                    else:
                        continue
 
                if fileDataA['filename'] == fileDataB['filename'] and not compareMsgPDF(fileDataA, fileDataB):
                    Inference = DuplicateTags.case1
                elif fileDataA['filename'] != fileDataB['filename'] and compareMsgPDF(fileDataA, fileDataB):
                    Inference = DuplicateTags.case2
                elif fileDataA['filename'] == fileDataB['filename'] and compareMsgPDF(fileDataA, fileDataB):
                    Inference = DuplicateTags.case3
                else:
                    continue
                duplicateInferenceData.append({
                    'basefile': fileDataA['filename']+'.msg',
                    'basefilesize': fileSize(fileA),
                    'basefilepath': fileA,
                    
                    'Inference': Inference,
                    'testfile': fileDataB['filename']+'.pdf',
                    'testfilesize': fileSize(fileB),
                    'testfilepath': fileB,
                    
                })
 
    return duplicateInferenceData

def exportToExcel(dupliDict, outputFPath, headers):
    """_summary_
    exports all data to excel
    """
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "DuplicateInfo"
   
   
    #headers = ["File A Name", "File A Size(KB)", "File A Path", "Inference", "File B Name", "File B size", "File B Path"]
    sheet.append(headers)
   
    for duplicate in dupliDict:
        row = [
            duplicate["basefile"],
            duplicate["basefilesize"],
            duplicate["basefilepath"],
            
            duplicate["Inference"],
            duplicate["testfile"],
            duplicate["testfilesize"],
            duplicate["testfilepath"],
            
        ]
        sheet.append(row)
   
    workbook.save(outputFPath)

def exportToCSV(dupliDict, outputFPath, headers):
    """
    Exports all data to CSV
    """
    #headers = ["Base File Name", "Base File Size(KB)", "Base File Path", "Inference", "Test File", "Test File size", "Test File Path"]
   
    with open(outputFPath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
       
        for duplicate in dupliDict:
            row = [
                duplicate["basefile"],
                duplicate["basefilesize"],
                duplicate["basefilepath"],
                
                duplicate["Inference"],
                duplicate["testfile"],
                duplicate["testfilesize"],
                duplicate["testfilepath"],
                
            ]
            writer.writerow(row)


def mainFn(mainDir, headers, outputPath):
    """_summary_
    Runs everything finally
    """
    print(f'directory : {mainDir}')
    pdffilepaths, msgfilepaths, allFilesboth = getAllFilesFromDir(mainDir)
    duplicateData = checkDuplicates(pdffilepaths, msgfilepaths, allFilesboth)
    exportToExcel(duplicateData, outputPath+'/duplicatesData.xlsx', headers)
    exportToCSV(duplicateData, outputPath+'/duplicatesData.csv', headers)
    logging.info(f'No of Duplicates Found : {len(duplicateData)}')
    logging.info(f'Duplicate Data can be found at : {outputPath}/')

if __name__ == "__main__":
    data = extractConfig(GLOBAL_CONFIG, USECASE3)
    inputDir = data[0]['Input_Directory']
    Headers = data[1]['Output_Headers']
    outputPath = data[2]['Output_Directory']
    mainFn(inputDir, Headers, outputPath)
