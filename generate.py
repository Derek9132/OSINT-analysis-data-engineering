from pathlib import Path
import mitreattack.attackToExcel.attackToExcel as attackToExcel
import mitreattack.attackToExcel.stixToDf as stixToDf
import pandas as pd


def download(domain): #ics, enterprise, or mobile in string form
    try:
        base_dir = str(Path(__file__).resolve().parent)

        domain = domain.lower().strip()

        tech_domain = domain + "-attack"

        print(tech_domain)

        data = attackToExcel.get_stix_data(tech_domain)
        stix = stixToDf.techniquesToDf(data, tech_domain)
        output_path = base_dir + "/raw/" + domain + "-stix.xlsx"

        with pd.ExcelWriter(output_path) as writer:
            sheetIndex = 0
            for df in stix.values():
                df.to_excel(writer, sheet_name="sheet " + str(sheetIndex))
                sheetIndex = sheetIndex + 1
    except Exception as e:
        print(e)

def download_all():
    try:
        download("ics")
        download("enterprise")
        download("mobile")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    print("generating files...")
    download_all()
    print("files generated")