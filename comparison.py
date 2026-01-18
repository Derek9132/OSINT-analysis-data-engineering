import pandas as pd
from pathlib import Path
from generate import download

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

        enterprise_not_mobile = enterprise_techniques[~enterprise_techniques["ID"].isin(mobile_techniques["ID"])]

        # find techniques in mobile-attack not in enterprise-attack
        mobile_not_enterprise = mobile_techniques[~mobile_techniques["ID"].isin(enterprise_techniques["ID"])]

        # find common techniques
        enterprise_and_mobile = enterprise_techniques[enterprise_techniques["ID"].isin(mobile_techniques["ID"])]

        # export

    except Exception as e:
        print(e)
        # redownload files