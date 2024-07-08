from pathlib import Path

# Environment
ENDPOINT = "https://order-processing-form-recognizer.cognitiveservices.azure.com/"
KEY = "fed96b9eec534f878abd425a0a350b85"
MODEL_ID = "prebuilt-layout"
API_VERSION = "2024-02-29-preview"


UPLOAD_FOLDER = Path('Uploads')
DUPLICATES_FOLDER = Path("Duplicates_hash")
OUTPUT_DIR = Path("Output")
DATA = "Uploads"
GLOBAL_CONFIG = "ConfigFiles/Global_Config.xlsx"
# EMPLOYEE_INFO = "Employee_info.xlsx"
# PAYLOAD_FILE = "payload.txt"
# CLASSES=Path("Classes")
# BATCH_DATA="C:/Users/a826190/OneDrive - Atos/Desktop/novartis/v1code/Novartis-Doc-Comparator/Data"
BATCH_DATA="/Users/rxnkshitij748/Novartis Eviden/Novartis5_POC/Data/Case 1"