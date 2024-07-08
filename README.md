# Document-Cleaning
A python application to generate a similarity score after comparing two documents. 
Use cases satisfied : 
1. Metadata Extraction from documents according to configurable set of regex 
2. Creating a model to compare two documents and give a similarity score and finally ascertain whether the two documents are to be grouped or not. 

- Raw Content was extracted from documents using Azure's Layout API utilising azure's OCR and document intelligence app then processed through code
- Similarity score model was made using difflib's SequenceMatcher and built on sklearn. Content was vectorised and then a cosine similarity score was obtained. Then the results were combined with the SequenceMatchers results to draft out a similarity score. 





