import pandas as pd
from pathlib import Path
import re
import spacy
import traceback
from collections import Counter
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

def clean_text(description, nlp): # pandas column as parameter

    # regular expressions
    reg_adversary = re.compile("(?:an )?adversar(?:y|ies) *(?:may|can)?", re.IGNORECASE)
    reg_citation = re.compile("\(citation: [a-zA-Z0-9 ]*\)", re.IGNORECASE)
    reg_link = re.compile("\[(?:[^\]]*)\]\(https:\/\/attack\.mitre\.org\/(?:software|techniques|tactics)\/(?:(?:S|T|TA)[0-9]{4})\/?(?:[0-9]{3})?\)", re.IGNORECASE)

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

    to_return =  " ".join(filtered)

    return "".join([char for char in to_return if char.isalnum() or char == " "])


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

    re_link = re.compile("\[([^\]]*)\]\(https:\/\/attack\.mitre\.org\/(?:software|techniques|tactics)\/((?:S|T|TA)[0-9]{4})\/?([0-9]{3})?\)", re.IGNORECASE)

    associated_techs = re_link.findall(description)

    # filter repeats
    filtered = [tech for tech in associated_techs if tech[1] != id]

    for tech in filtered:
        if tech[2] == '':
            to_return.append(tech[0] + " (" + tech[1] + ")")
        else:
            to_return.append(tech[0] + " (" + tech[1] + "." + tech[2] + ")")

    unique = list(set(to_return))

    return ", ".join(unique)

def to_sql_table(dataframe, table_name, engine):
    engine = create_engine(engine)

    try:
        dataframe.to_sql(name=table_name, con=engine, if_exists="replace", index=False)
    except Exception as e:
        print(e)


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

        mobile_techniques.insert(loc=13, column="is sub-technique", value=is_sub)
        mobile_techniques.insert(loc=14, column="sub-technique of", value=sub_id)

        # associated and follow-up techniques
        enterprise_techniques["associated and/or followup techniques"] = enterprise_techniques.apply(get_associated_techniques, axis=1)
        mobile_techniques["associated and/or followup techniques"] = mobile_techniques.apply(get_associated_techniques, axis=1)
        ics_techniques["associated and/or followup techniques"] = ics_techniques.apply(get_associated_techniques, axis=1)

        # associated codes, commands, programs
        enterprise_techniques["associated codes, commands, programs"] = enterprise_techniques["description"].map(get_codes_commands)
        mobile_techniques["associated codes, commands, programs"] = mobile_techniques["description"].map(get_codes_commands)
        ics_techniques["associated codes, commands, programs"] = ics_techniques["description"].map(get_codes_commands)

        # get more citations
        enterprise_techniques["relationship citations"] = enterprise_techniques.apply(get_more_citations, axis=1)
        mobile_techniques["relationship citations"] = mobile_techniques.apply(get_more_citations, axis=1)
        ics_techniques["relationship citations"] = ics_techniques.apply(get_more_citations, axis=1)

        # clean descriptions
        enterprise_techniques["cleaned description"] = enterprise_techniques["description"].apply(clean_text, args=(nlp,))
        mobile_techniques["cleaned description"] = mobile_techniques["description"].apply(clean_text, args=(nlp,))
        ics_techniques["cleaned description"] = ics_techniques["description"].apply(clean_text, args=(nlp,))
    
        # most common verbs and nouns
        enterprise_techniques["most common verbs"] = enterprise_techniques["cleaned description"].apply(most_common_words, args=(nlp,"verb"))
        mobile_techniques["most common verbs"] = mobile_techniques["cleaned description"].apply(most_common_words, args=(nlp,"verb"))
        ics_techniques["most common verbs"] = ics_techniques["cleaned description"].apply(most_common_words, args=(nlp,"verb"))

        enterprise_techniques["most common nouns"] = enterprise_techniques["cleaned description"].apply(most_common_words, args=(nlp,"noun"))
        mobile_techniques["most common nouns"] = mobile_techniques["cleaned description"].apply(most_common_words, args=(nlp,"noun"))
        ics_techniques["most common nouns"] = ics_techniques["cleaned description"].apply(most_common_words, args=(nlp,"noun"))

        # Add CVEs column (enterprise domain only)
        enterprise_techniques["CVEs that allow this technique"] = "The following common vulnerabilities allow this technique: \n"

        for row in kev_attack.itertuples():
            # combine CVE ID, name, comments
            CVE_string = row.capability_description + " (" + row.capability_id + "): " + row.comments + "\n"

            # find attack_object_id in enterprise_techniques
            current_tech = row.attack_object_id

            enterprise_techniques.loc[enterprise_techniques["ID"] == current_tech, "CVEs that allow this technique"] = enterprise_techniques.loc[enterprise_techniques["ID"] == current_tech, "CVEs that allow this technique"] + CVE_string

        enterprise_techniques.loc[enterprise_techniques["CVEs that allow this technique"] == "The following common vulnerabilities allow this technique: \n", "CVEs that allow this technique"] = "No listed CVEs in the KEV allow this technique"

        # drop first column
        enterprise_techniques.drop(enterprise_techniques.columns[0], axis=1, inplace=True)
        mobile_techniques.drop(mobile_techniques.columns[0], axis=1, inplace=True)
        ics_techniques.drop(ics_techniques.columns[0], axis=1, inplace=True)

        # reorder columns
        new_order_enterprise = ["ID","STIX ID","name","associated codes, commands, programs","associated and/or followup techniques","CVEs that allow this technique","platforms","tactics","detection","description","cleaned description","most common verbs","most common nouns", "is sub-technique","sub-technique of", "url","created","last modified", "domain","version","contributors","supports remote","impact type","relationship citations"]
        new_order_mobile = ["ID","STIX ID","name","associated codes, commands, programs","associated and/or followup techniques","platforms","tactics","detection","description","cleaned description","most common verbs","most common nouns", "is sub-technique","sub-technique of", "url","created","last modified", "domain","version","contributors","MTC ID","tactic type","relationship citations"]
        new_order_ics = ["ID","STIX ID","name","associated codes, commands, programs","associated and/or followup techniques","platforms","tactics","detection","description","cleaned description","most common verbs","most common nouns", "url","created","last modified", "domain","version","contributors","relationship citations"]

        enterprise_techniques = enterprise_techniques[new_order_enterprise]
        mobile_techniques = mobile_techniques[new_order_mobile]
        ics_techniques = ics_techniques[new_order_ics]

        # export to excel
        enterprise_techniques.to_excel(base_dir/"add-columns"/"enterprise_techniques_new.xlsx")
        mobile_techniques.to_excel(base_dir/"add-columns"/"mobile_techniques_new.xlsx")
        ics_techniques.to_excel(base_dir/"add-columns"/"ics_techniques_new.xlsx")

        # export to SQL
        load_dotenv()

        engine = os.getenv("DATABASE_URL")
        to_sql_table(enterprise_techniques, "enterprise_new", engine)
        to_sql_table(mobile_techniques, "mobile_new", engine)
        to_sql_table(ics_techniques, "ics_new", engine)

    except Exception as e:
        print("Error")
        traceback.print_exc()