import pandas as pd
from pathlib import Path

def examples_mitigations_detections(techniques, examples, mitigations, detections): # 4 datasets as parameters
    # define new dataframe
    emd_dataset = pd.DataFrame(columns=["technique ID", "technique name", "number of examples", "number of mitigations", "number of detections"])
    num_examples = []
    num_mitigations = []
    num_detections = []

    # get all techniques
    techniques_list = techniques["ID"]

    # for each technique, find counts in examples, mitigations, detections
    for tech in techniques_list:
        #examples_count = 
        pass

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

        # ics-attack dataframes
        ics_path = base_dir/"raw"/"ics-stix.xlsx"
        ics_techniques = pd.read_excel(ics_path, sheet_name=0)
        ics_examples = pd.read_excel(ics_path, sheet_name=1)
        ics_mitigations = pd.read_excel(ics_path, sheet_name=2)
        ics_detections = pd.read_excel(ics_path, sheet_name=4)


    except Exception as e:
        print(e)