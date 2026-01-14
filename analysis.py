import re
import nltk
import requests
from pathlib import Path
import mitreattack.attackToExcel.attackToExcel as attackToExcel
import mitreattack.attackToExcel.stixToDf as stixToDf
import pandas as pd


# Creating excel files so I don't have to deal with the querying time every time I run
base_dir = Path(__file__).resolve().parent

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


if __name__ == "main":
    # read in MITRE ATT&CK STIX from excel files
    

    pass