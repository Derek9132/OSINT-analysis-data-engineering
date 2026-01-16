import re
import spacy
import requests
from pathlib import Path
import mitreattack.attackToExcel.attackToExcel as attackToExcel
import mitreattack.attackToExcel.stixToDf as stixToDf
import pandas as pd

print("checkpoint")

base_dir = Path(__file__).resolve().parent

# enterprise, mobile, or ics
def read_from_stix(domain):
    try:
        domain_string = domain + "-attack"
        data = attackToExcel.get_stix_data(domain_string)
        stix = stixToDf.techniquesToDf(data, domain_string)
        output = base_dir/"raw"/domain + "-stix.xlsx"

        with pd.ExcelWriter(output) as writer:
            sheetIndex = 0
            for df in stix.values():
                #print(df)
                df.to_excel(writer, sheet_name="sheet " + str(sheetIndex))
                sheetIndex = sheetIndex + 1
    except:
        print("Not a valid domain name!")


def clean_text(description): # pandas column as parameter
    # regular expressions
    reg1 = re.compile("(an )?adversar(y|ies) *(may|can)?")
    reg2 = re.compile("\(citation: [a-zA-Z0-9 ]*\)")

    # lowercase all
    description = description.lower()

    # replace
    description = description.replace("in order to", "to")
    description = description.replace("’", "'")

    # remove citation

    # remove "adversaries may"/"an adversary can"

    return

def make_subtechnique():
    return

def examples_mitigations_detections(techniques, examples, mitigations, detections): # 4 datasets as parameters
    # define new dataframe
    emd_dataset = pd.DataFrame(columns=["technique ID", "technique name", "number of examples", "number of mitigations", "number of detections"])

    # get all techniques, drop duplicates
    techniques_list = []

    # for each technique, find counts in examples, mitigations, detections


# Creating excel files so I don't have to deal with the querying time every time I run

"""# enterprise-attack
enterprise_data = attackToExcel.get_stix_data("enterprise-attack")
enterprise_techniques = stixToDf.techniquesToDf(enterprise_data, "enterprise-attack")
enterprise_output = base_dir/"raw"/"enterprise-stix.xlsx"

with pd.ExcelWriter(enterprise_output) as writer1:
    sheetIndexEnterprise = 0
    for df in enterprise_techniques.values():
        #print(df)
        df.to_excel(writer1, sheet_name="sheet " + str(sheetIndexEnterprise))
        sheetIndexEnterprise = sheetIndexEnterprise + 1"""

"""# mobile-attack
mobile_data = attackToExcel.get_stix_data("mobile-attack")
mobile_techniques = stixToDf.techniquesToDf(mobile_data, "mobile-attack")
mobile_output = base_dir/"raw"/"mobile-stix.xlsx"

with pd.ExcelWriter(mobile_output) as writer2:
    sheetIndexMobile = 0
    for df in mobile_techniques.values():
        #print(df)
        df.to_excel(writer2, sheet_name="sheet " + str(sheetIndexMobile))
        sheetIndexMobile = sheetIndexMobile + 1

# ics-attack
ics_data = attackToExcel.get_stix_data("ics-attack")
ics_techniques = stixToDf.techniquesToDf(ics_data, "ics-attack")
ics_output = base_dir/"raw"/"ics-stix.xlsx"

with pd.ExcelWriter(ics_output) as writer3:
    sheetIndexICS = 0
    for df in ics_techniques.values():
        #print(df)
        df.to_excel(writer3, sheet_name="sheet " + str(sheetIndexICS))
        sheetIndexICS = sheetIndexICS + 1"""

enterprise_path = base_dir/"raw"/"enterprise-stix.xlsx"
enterprise_techniques = pd.read_excel(enterprise_path, sheet_name=0)
enterprise_examples = pd.read_excel(enterprise_path, sheet_name=1)
enterprise_mitigations = pd.read_excel(enterprise_path, sheet_name=2)
enterprise_detections = pd.read_excel(enterprise_path, sheet_name=3)

print(list(enterprise_techniques.columns))

if __name__ == "main":
    try: # reading from excel files
        print("excel files found")

        # enterprise-attack dataframes
        enterprise_path = base_dir/"raw"/"enterprise-stix.xlsx"
        enterprise_techniques = pd.read_excel(enterprise_path, sheet_name=0)
        enterprise_examples = pd.read_excel(enterprise_path, sheet_name=1)
        enterprise_mitigations = pd.read_excel(enterprise_path, sheet_name=2)
        enterprise_detections = pd.read_excel(enterprise_path, sheet_name=3)

        # mobile-attack dataframes
        mobile_path = base_dir/"raw"/"mobile-stix.xlsx"
        mobile_techniques = pd.read_excel(mobile_path, sheet_name=0)
        mobile_examples = pd.read_excel(mobile_path, sheet_name=1)
        mobile_mitigations = pd.read_excel(mobile_path, sheet_name=2)
        mobile_detections = pd.read_excel(mobile_path, sheet_name=3)

        # ics-attack dataframes
        ics_path = base_dir/"raw"/"ics-stix.xlsx"
        ics_techniques = pd.read_excel(ics_path, sheet_name=0)
        ics_examples = pd.read_excel(ics_path, sheet_name=1)
        ics_mitigations = pd.read_excel(ics_path, sheet_name=2)
        ics_detections = pd.read_excel(ics_path, sheet_name=4)

        # find techniques in enterprise-attack not in mobile-attack
        enterprise_not_mobile = enterprise_techniques[~enterprise_techniques["ID"].isin(mobile_techniques["ID"])]

        # find techniques in mobile-attack not in enterprise-attack
        mobile_not_enterprise = mobile_techniques[~mobile_techniques["ID"].isin(enterprise_techniques["ID"])]

        # find common techniques
        enterprise_and_mobile = enterprise_techniques[enterprise_techniques["ID"].isin(mobile_techniques["ID"])]

        # add subtechniques to mobile-attack

        # clean description texts for each techniques dataset

        # build examples, mitigations, detections dataframes

        # export
        
    except: # excel files don't exist, make new ones
        enterprise_data = attackToExcel.get_stix_data("enterprise-attack")
        enterprise_stix = stixToDf.techniquesToDf(enterprise_data, "enterprise-attack")
        enterprise_output = base_dir/"raw"/"enterprise-stix.xlsx"

        with pd.ExcelWriter(enterprise_output) as writer1:
            sheetIndexEnterprise = 0
            for df in enterprise_stix.values():
                #print(df)
                df.to_excel(writer1, sheet_name="sheet " + str(sheetIndexEnterprise))
                sheetIndexEnterprise = sheetIndexEnterprise + 1

        # mobile-attack
        mobile_data = attackToExcel.get_stix_data("mobile-attack")
        mobile_stix = stixToDf.techniquesToDf(mobile_data, "mobile-attack")
        mobile_output = base_dir/"raw"/"mobile-stix.xlsx"

        with pd.ExcelWriter(mobile_output) as writer2:
            sheetIndexMobile = 0
            for df in mobile_stix.values():
                #print(df)
                df.to_excel(writer2, sheet_name="sheet " + str(sheetIndexMobile))
                sheetIndexMobile = sheetIndexMobile + 1

        # ics-attack
        ics_data = attackToExcel.get_stix_data("ics-attack")
        ics_stix = stixToDf.techniquesToDf(ics_data, "ics-attack")
        ics_output = base_dir/"raw"/"ics-stix.xlsx"

        with pd.ExcelWriter(ics_output) as writer3:
            sheetIndexICS = 0
            for df in ics_stix.values():
                #print(df)
                df.to_excel(writer3, sheet_name="sheet " + str(sheetIndexICS))
                sheetIndexICS = sheetIndexICS + 1

        print("excel files made")