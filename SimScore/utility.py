import json

def load_json(jsonPath):
    with open(jsonPath, 'r') as f:
        jsonDict = json.load(f)
    return jsonDict

def get_text_from_json(jsonData : dict):
    return jsonData["analyzeResult"]["content"]