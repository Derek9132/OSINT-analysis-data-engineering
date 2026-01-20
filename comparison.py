import pandas as pd
from pathlib import Path
import traceback
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

def to_sql_table(dataframe, table_name, engine):
    engine = create_engine(engine)

    dataframe.to_sql(name=table_name, con=engine, if_exists="replace", index=False)

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