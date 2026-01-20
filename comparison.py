import pandas as pd
from pathlib import Path
import traceback
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

def to_sql_table(dataframe, table_name, engine):
    engine = create_engine(engine)

    dataframe.to_sql(name=table_name, con=engine, if_exists="replace", index=False)

def split_technique(technique):
    if "." in technique:
        return technique.split(".")[0]
    else:
        return technique

if __name__ == "__main__":
    try:
        base_dir = Path(__file__).resolve().parent

        # enterprise-attack dataframes
        enterprise_path = base_dir/"raw"/"enterprise-stix.xlsx"
        enterprise_techniques = pd.read_excel(enterprise_path, sheet_name=0)

        # mobile-attack dataframes
        mobile_path = base_dir/"raw"/"mobile-stix.xlsx"
        mobile_techniques = pd.read_excel(mobile_path, sheet_name=0)

        # dataframes
        enterprise_subset = pd.DataFrame(columns=["technique", "technique name", "description", "domain"])
        mobile_subset = pd.DataFrame(columns=["technique", "technique name", "description", "domain"])

        enterprise_subset["technique"] = enterprise_techniques["ID"]
        enterprise_subset["technique name"] = enterprise_techniques["name"]
        enterprise_subset["description"] = enterprise_techniques["description"]
        enterprise_subset["domain"] = enterprise_techniques["domain"]

        mobile_subset["technique"] = mobile_techniques["ID"]
        mobile_subset["technique name"] = mobile_techniques["name"]
        mobile_subset["description"] = mobile_techniques["description"]
        mobile_subset["domain"] = mobile_techniques["domain"]

        # make new columns
        enterprise_subset["parent technique"] = enterprise_subset["technique"].map(split_technique)
        mobile_subset["parent technique"] = mobile_subset["technique"].map(split_technique)

        enterprise_not_mobile = enterprise_subset[~enterprise_subset["parent technique"].isin(mobile_subset["parent technique"])]

        # find techniques in mobile-attack not in enterprise-attack
        mobile_not_enterprise = mobile_subset[~mobile_subset["parent technique"].isin(enterprise_subset["parent technique"])]

        # find common techniques
        enterprise_and_mobile = enterprise_subset[enterprise_subset["parent technique"].isin(mobile_subset["parent technique"])]

        # export
        with pd.ExcelWriter(base_dir/"comparison"/"comparison.xlsx") as writer:
            enterprise_not_mobile.to_excel(writer, sheet_name="Enterprise_not_Mobile")
            mobile_not_enterprise.to_excel(writer, sheet_name="Mobile_not_Enterprise")
            enterprise_and_mobile.to_excel(writer, sheet_name="Enterprise_and_Mobile")

        # export to SQL
        load_dotenv()

        engine = os.getenv("DATABASE_URL")
        to_sql_table(enterprise_not_mobile, "enterprise_not_mobile", engine)
        to_sql_table(mobile_not_enterprise, "mobile_not_enterprise", engine)
        to_sql_table(enterprise_and_mobile, "enterprise_and_mobile", engine)

    except Exception as e:
        print(e)