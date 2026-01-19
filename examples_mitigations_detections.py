import pandas as pd
import traceback
from pathlib import Path

def style():
    pass

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
        print(tech)
        examples_count = examples["target ID"].value_counts().get(tech, 0)
        num_examples.append(examples_count)

        mitigations_count = mitigations["target ID"].value_counts().get(tech,0)
        num_mitigations.append(mitigations_count)

        detections_count = detections["target ID"].value_counts().get(tech,0)
        num_detections.append(detections_count)

    # build dataframe
    emd_dataset["technique ID"] = techniques["ID"]
    emd_dataset["technique name"] = techniques["name"]
    emd_dataset["number of examples"] = num_examples
    emd_dataset["number of mitigations"] = num_mitigations
    emd_dataset["number of detections"] = num_detections

    return emd_dataset

if __name__ == "__main__":
    try:
        base_dir = Path(__file__).resolve().parent

        output_path = base_dir/"examples-mitigations-detections"/"examples_mitigations_detections.xlsx"

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

        emd_enterprise = examples_mitigations_detections(enterprise_techniques, enterprise_examples, enterprise_mitigations, enterprise_detections)
        emd_mobile = examples_mitigations_detections(mobile_techniques,mobile_examples, mobile_mitigations, mobile_detections)
        emd_ics = examples_mitigations_detections(ics_techniques, ics_examples, ics_mitigations, ics_detections)

        print(emd_enterprise)

        with pd.ExcelWriter(output_path) as writer:
            emd_enterprise.to_excel(writer, sheet_name="enterprise counts")
            emd_mobile.to_excel(writer, sheet_name="mobile counts")
            emd_ics.to_excel(writer, sheet_name="ICS count")

    except Exception as e:
        print("Error")
        traceback.print_exc()