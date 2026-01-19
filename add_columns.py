import pandas as pd
from pathlib import Path
import re
import spacy
import traceback
from collections import Counter

def clean_text(description, nlp): # pandas column as parameter

    # regular expressions
    reg_adversary = re.compile("(?:an )?adversar(?:y|ies) *(?:may|can)?")
    reg_citation = re.compile("\(citation: [a-zA-Z0-9 ]*\)")
    reg_link = re.compile("\[[^\]]*\]\(https:\/\/attack\.mitre\.org\/techniques\/T[0-9]{4}(?:\/[0-9]{3})?\)")

    # lowercase all
    description = description.lower()

    # replace
    description = description.replace("in order to", "to")
    description = description.replace("as a means for", "to")
    description = description.replace("’", "'")
    description = description.replace("<code>","")
    description = description.replace("</code>", "")
    description = description.replace("\n", "")

    # remove citation
    citations_list = reg_citation.findall(description)

    for citation in citations_list:
        description = description.replace(citation, "")

    # remove "adversaries may"/"an adversary can"
    adversary_phrases = reg_adversary.findall(description)

    for adversary in adversary_phrases:
        description = description.replace(adversary, "")

    # remove links
    links_list = reg_link.findall(description)

    for link in links_list:
        description = description.replace(link, "")

    doc = nlp(description)

    # remove punctuation and stopwords
    filtered = [token for token in doc if not token.is_stop and not token.is_punct]

    # lemmatize
    for i in range(len(filtered)):
        filtered[i] = filtered[i].lemma_

    #print("completed cleaning")

    return " ".join(filtered)


def most_common_words(description, nlp, pos): # verb or noun

    doc = nlp(description)
    pos = pos.lower().strip()

    if pos == "verb":
        word_list = [token.text for token in doc if token.pos_ == "VERB"]
    else:
        word_list = [token.text for token in doc if token.pos_ == "NOUN"]

    word_frequency = Counter(word_list)

    common = word_frequency.most_common(5)

    to_return = []

    for word in common:
        to_return.append(word[0])

    return ", ".join(to_return)
        

def get_codes_commands(description):
    reg_code = re.compile("\<code\>([^\<]*)\<\/code\>")

    get_codes = reg_code.findall(description)

    unique_codes = list(set(get_codes))

    return ", ".join(unique_codes)


def get_more_citations(row):
    citations = row["relationship citations"]

    citations = citations.replace(",,", "")

    if citations == "":
        citations = "No Citations"
    
    if citations[-1] == ",":
        citations = citations[:-1]

    existing_citations = citations.split(",")

    re_citation = re.compile("\(citation: [a-zA-Z0-9 ]*\)", re.IGNORECASE)
    description = row["description"]

    new_citations = re_citation.findall(description)

    for citation in new_citations:
        if citation not in existing_citations:
            existing_citations.append(citation)

    return ",".join(existing_citations)


def get_associated_techniques(row):
    id = row["ID"]
    description = row["description"]

    to_return = []

    re_link = re.compile("\[([^\]]*)\]\(https:\/\/attack\.mitre\.org\/techniques\/(T[0-9]{4})\/?([0-9]{3})?\)")

    associated_techs = re_link.findall(description)

    # filter repeats
    filtered = [tech for tech in associated_techs if tech[1] != id]

    for tech in filtered:
        if tech[2] == '':
            to_return.append(tech[0] + " (" + tech[1] + ")")
        else:
            to_return.append(tech[0] + " (" + tech[1] + "." + tech[2] + ")")

    return ", ".join(to_return)


if __name__ == "__main__":
    try:
        base_dir = Path(__file__).resolve().parent

        nlp = spacy.load("en_core_web_sm")

        # enterprise-attack dataframes
        enterprise_path = base_dir/"raw"/"enterprise-stix.xlsx"
        enterprise_techniques = pd.read_excel(enterprise_path, sheet_name=0)

        # mobile-attack dataframes
        mobile_path = base_dir/"raw"/"mobile-stix.xlsx"
        mobile_techniques = pd.read_excel(mobile_path, sheet_name=0)

        # ics-attack dataframes
        ics_path = base_dir/"raw"/"ics-stix.xlsx"
        ics_techniques = pd.read_excel(ics_path, sheet_name=0)

        # KEV
        kev_path = base_dir/"raw"/"kev-mitre.csv"
        kev_attack = pd.read_csv(kev_path)

        # add subtechniques to mobile-attack
        mobile_techniques["sort_column"] = (mobile_techniques["ID"].str.replace("T", "")).astype('float')
        mobile_techniques.sort_values(by="sort_column", inplace=True)
        mobile_techniques.drop(columns=["sort_column"], inplace=True)

        is_sub = []
        sub_id = []
        for row in mobile_techniques.itertuples(index=False):
            id_split = (row.ID).split(".")
            if len(id_split) == 2:
                is_sub.append("TRUE")
                sub_id.append(id_split[0])
            else:
                is_sub.append("FALSE")
                sub_id.append("")

        mobile_techniques.insert(loc=13, column="is_subtechnique", value=is_sub)
        mobile_techniques.insert(loc=14, column="subtechnique of:", value=sub_id)

        # associated and follow-up techniques
        enterprise_techniques["Associated and/or follow-up techniques"] = enterprise_techniques.apply(get_associated_techniques, axis=1)
        mobile_techniques["Associated and/or follow-up techniques"] = mobile_techniques.apply(get_associated_techniques, axis=1)
        ics_techniques["Associated and/or follow-up techniques"] = ics_techniques.apply(get_associated_techniques, axis=1)

        # associated codes, commands, programs
        enterprise_techniques["Associated codes, commands, programs"] = enterprise_techniques["description"].map(get_codes_commands)
        mobile_techniques["Associated codes, commands, programs"] = mobile_techniques["description"].map(get_codes_commands)
        ics_techniques["Associated codes, commands, programs"] = ics_techniques["description"].map(get_codes_commands)

        # get more citations
        enterprise_techniques["relationship citations"] = enterprise_techniques.apply(get_more_citations, axis=1)
        mobile_techniques["relationship citations"] = mobile_techniques.apply(get_more_citations, axis=1)
        ics_techniques["relationship citations"] = ics_techniques.apply(get_more_citations, axis=1)

        # clean descriptions
        print("starting cleaning")
        enterprise_techniques["cleaned_description"] = enterprise_techniques["description"].apply(clean_text, args=(nlp,))
        print("enterprise cleaned")
        mobile_techniques["cleaned_description"] = mobile_techniques["description"].apply(clean_text, args=(nlp,))
        print("mobile cleaned")
        ics_techniques["cleaned_description"] = ics_techniques["description"].apply(clean_text, args=(nlp,))
        print("ics cleaned")
        # most common verbs and nouns
        enterprise_techniques["most_common_verbs"] = enterprise_techniques["cleaned_description"].apply(most_common_words, args=(nlp,"verb"))
        mobile_techniques["most_common_verbs"] = mobile_techniques["cleaned_description"].apply(most_common_words, args=(nlp,"verb"))
        ics_techniques["most_common_verbs"] = ics_techniques["cleaned_description"].apply(most_common_words, args=(nlp,"verb"))

        enterprise_techniques["most_common_nouns"] = enterprise_techniques["cleaned_description"].apply(most_common_words, args=(nlp,"noun"))
        mobile_techniques["most_common_nouns"] = mobile_techniques["cleaned_description"].apply(most_common_words, args=(nlp,"noun"))
        ics_techniques["most_common_nouns"] = ics_techniques["cleaned_description"].apply(most_common_words, args=(nlp,"noun"))

        # Add CVEs column (enterprise domain only)
        enterprise_techniques["CVEs that allow this technique:"] = "The following common vulnerabilities allow this technique: \n"

        for row in kev_attack.itertuples():
            # combine CVE ID, name, comments
            CVE_string = row.capability_group + " (" + row.capability_id + "): " + row.comments + "\n"

            # find attack_object_id in enterprise_techniques
            current_tech = row.attack_object_id

            enterprise_techniques.loc[enterprise_techniques["ID"] == current_tech, "CVEs that allow this technique:"] = enterprise_techniques.loc[enterprise_techniques["ID"] == current_tech, "CVEs that allow this technique:"] + CVE_string

        # export
        enterprise_techniques.to_excel(base_dir/"add-columns"/"enterprise_techniques_new.xlsx")
        mobile_techniques.to_excel(base_dir/"add-columns"/"mobile_techniques_new.xlsx")
        ics_techniques.to_excel(base_dir/"add-columns"/"ics_techniques_new.xlsx")

    except Exception as e:
        print("Error")
        traceback.print_exc()