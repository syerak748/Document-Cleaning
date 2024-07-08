# Document-Cleaning
A python application containing multiple python scripts to clean up folders by satisfying various use cases specified by the user. 
Use cases satisfied : \
1. Identify duplicate files in a folder, files may be of different types : .docx or .pdf \
2. Metadata Extraction from documents according to configurable set of regex \
3. Creating a model to compare two documents and give a similarity score and finally ascertain whether the two documents are to be grouped or not. \

Duplicates were flagged by hashing the content of the two files and comparing the hash code, sha 256 algo was used \
Metadata Extraction is pretty straight forward \
Similarity score model was made using difflib's SequenceMatcher and built on sklearn. Content was vectorised and then a cosine similarity score was obtained. Then the results were combined with the SequenceMatchers results to draft out a similarity score. \





