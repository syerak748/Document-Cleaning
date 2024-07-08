from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from difflib import SequenceMatcher
from utility import get_text_from_json, load_json
jsonDict1 = load_json("samplepdf.json")
jsonDict2 = load_json("sampledocx.json")
text1 = get_text_from_json(jsonDict1)
with open('samplepdftext.txt','w') as f:
    f.write(text1)
text2 = get_text_from_json(jsonDict2)
with open('sampledoctext.txt','w') as f:
    f.write(text2)

dict1 = {
    1: 'IND 123456 ADVICE/INFORMATION REQUEST Atos-Syntel Attention: Eva Adam, MD Director (Acting), Division of Imaging and Radiation Medicine (DIRM) FDA/CDER Plot No. B-1 Software, Atos-Syntel Link Rd, MIDC Technology Park, Talawade, Pimpri-Chinchwad, Maharashtra 411062, Dear Dr. Adam: Please refer to your investigational new drug application (IND) submitted under section 505 of the Federal Food, Drug, and Cosmetic Act for xxxXXX We also refer to your amendment(s) dated November 13, 2020; November 20, 2020; December 18, 2020; December 22, 2020; and January 8, 2021. We have the following comments and requests for additional information. Please note that these requests are not clinical hold issues. However, response to them is requested: Item#1: Based on your submitted protocol CO-0000-001and XXXXXXX Sub-protocol, it appears that you are pursuing a pathway intended to leverage XYXYXYXY investigation in support of new patient selection indication for XXXXXXXX. In approaching the design of downstream studies, we recommend that you focus on at least the following four high level considerations: SECURE EMAIL Secure email is required for all email communications from FDA when confidential information (e.g., trade secrets, manufacturing, or patient information) is included in the message. To receive email communications from FDA that include confidential information (e.g., information requests, labeling revisions, courtesy copies of letters), you must establish secure email. To establish secure email with FDA, send an email request to SecureEmail@fda.hhs.gov. Please note that secure email may not be used for formal regulatory submissions to applications. Sincerely, {See appended electronic signature page} Libo M., MD, PhD Director Division of Imaging and Radiation Medicine Office of Specialty Medicine Center for Drug Evaluation and Research U.S. Food and Drug Administration Silver Spring, MD 20993 www.fda.gov',
    2: 'U.S. Food and Drug Administration Silver Spring, MD 20993 www.fda.gov'
}

dict2 = {
    1: 'IND 123456 REQUEST FOR INFORMATION Atos-Syntel Attention: Eva Adam, MD Acting Director, Division of Imaging and Radiation Medicine (DIRM) FDA/CDER Plot No. B-1 Software, Atos-Syntel Link Rd, MIDC Technology Park, Talawade, Pimpri-Chinchwad, Maharashtra 411062, Dear Dr. Adam: Please refer to your IND submitted under section 505 of the Federal Food, Drug, and Cosmetic Act for YYYXXX. We also refer to your amendments dated November 13, 2020; November 20, 2020; December 18, 2020; December 22, 2020; and January 8, 2021. We have the following comments and requests for additional information. Please note that these requests are not clinical hold issues. However, a response to them is requested: Item#1: Based on your submitted protocol CO-0000-001 and XYZ Sub-protocol, it appears that you are pursuing a pathway intended to leverage ABC investigation in support of new patient selection indication for XYZ. In approaching the design of downstream studies, we recommend that you focus on at least the following high level considerations: SECURE EMAIL Secure email is required for all email communications from FDA when confidential information (e.g., trade secrets, manufacturing, or patient information) is included in the message. To receive email communications from FDA that include confidential information (e.g., information requests, labeling revisions, courtesy copies of letters), you must establish secure email. To establish secure email with FDA, send an email request to SecureEmail@fda.hhs.gov. Please note that secure email may not be used for formal regulatory submissions to applications. Sincerely, {See appended electronic signature page} John M., MD, PhD Acting Director Division of Imaging and Radiation Medicine Office of Specialty Medicine Center for Drug Evaluation and Research U.S. Food and Drug Administration Silver Spring, MD 20993 www.fda.gov',
    2: 'U.S. Food and Drug Administration Silver Spring, MD 20993 www.fda.gov'
}


def compare_pages(text1, text2): #page comparision
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])

    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

    print(f"Similarity score with sklearn: {similarity[0][0]}")

    feature_names = vectorizer.get_feature_names_out()

    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), index=['Text1', 'Text2'], columns=feature_names).T
    print("\nTF-IDF Matrix:")
    print(tfidf_df)

    differences = tfidf_df.T.diff().iloc[1].abs().sort_values(ascending=False)
    print("\nTerm Discrepancies (sorted by absolute difference):")
    print(differences)

def compare_pagesSequence(text1, text2):
    matcher = SequenceMatcher(None, text1, text2)
    similarity = matcher.ratio()
    matches = matcher.get_matching_blocks()
    data = []
    for i, match in enumerate(matches):
        if i < len(matches) - 1:
            non_matching = text1[match.a + match.size:matches[i + 1].a]
            if non_matching:
                data.append({"Type": "Non-Matching (Text1)", "Text": non_matching, "SequenceMatcher Similarity": similarity})
            non_matching = text2[match.b + match.size:matches[i + 1].b]
            if non_matching:
                data.append({"Type": "Non-Matching (Text2)", "Text": non_matching, "SequenceMatcher Similarity": similarity})
        if match.size > 0:
            matching = text1[match.a:match.a + match.size]
            data.append({"Type": "Matching", "Text": matching, "SequenceMatcher Similarity": similarity})
    return pd.DataFrame(data)

def export_to_excel(discrepancies_df):
    with pd.ExcelWriter('text_comparison_results.xlsx', engine='xlsxwriter') as writer:
        discrepancies_df.to_excel(writer, sheet_name='Discrepancies', index=False)
    print("Results have been exported to 'text_comparison_results.xlsx'.")
'''
for page in dict1.keys():
    print(f"\ncomparing page {page} of both docs:")
    compare_pages(dict1[page], dict2[page])
    discrepancies = []
    for page in dict1.keys():
        print(f"\nComparing page {page}:")
        df_discrepancies = compare_pagesSequence(dict1[page], dict2[page])
        discrepancies.append(df_discrepancies)

    discrepancies_df = pd.concat(discrepancies, ignore_index=True)
    export_to_excel(discrepancies_df)
'''


print(f"\ncomparing using sklearn ")
compare_pages(text1, text2)
discrepancies = []
print(f"\ncomparing using SequenceMatcher")
df_discrepancies = compare_pagesSequence(text1, text2)
discrepancies.append(df_discrepancies)

discrepancies_df = pd.concat(discrepancies, ignore_index=True)
export_to_excel(discrepancies_df)