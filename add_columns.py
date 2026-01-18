import pandas as pd
from pathlib import Path
import re
import spacy



if __name__ == "__main__":
    try:
        base_dir = Path(__file__).resolve().parent

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

        # KEV

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

        #print(mobile_techniques[["ID", "is_subtechnique", "subtechnique of:"]])

        # Add CVEs column (enterprise domain only)



    except Exception as e:
        print(e)