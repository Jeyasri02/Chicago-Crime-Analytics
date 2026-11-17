from pathlib import Path

import pandas as pd
import numpy as np
from flask import current_app

from extensions import db
from models import Crime


# ============================================================
# FIND MASTER CSV
# ============================================================

def find_master_csv():
    """
    Find the main Chicago crime CSV inside the configured
    data folder.
    """

    data_folder = Path(
        current_app.config["DATA_FOLDER"]
    )

    if not data_folder.exists():
        raise FileNotFoundError(
            f"Data folder does not exist: {data_folder}"
        )

    possible_names = [
        "chicago crime dataset.csv",
        "chicago_crime_dataset.csv",
        "Chicago Crime Dataset.csv",
        "Chicago_Crime_Dataset.csv",
    ]

    for name in possible_names:

        file_path = data_folder / name

        if file_path.exists():
            return file_path

    csv_files = list(
        data_folder.glob("*.csv")
    )

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in {data_folder}"
        )

    for file_path in csv_files:

        name = file_path.name.lower()

        if (
            "crime" in name
            or "chicago" in name
        ):
            return file_path

    return csv_files[0]


# ============================================================
# NORMALIZE COLUMN NAME
# ============================================================

def normalize_column_name(column):
    """
    Convert CSV column names into standard snake_case.

    Examples:
        Case Number -> case_number
        Primary Type -> primary_type
        IUCR Code -> iucr_code
    """

    column = str(column).strip().lower()

    column = (
        column
        .replace(" ", "_")
        .replace("-", "_")
        .replace(".", "_")
        .replace("/", "_")
    )

    while "__" in column:
        column = column.replace(
            "__",
            "_"
        )

    return column.strip("_")


# ============================================================
# RENAME CSV COLUMNS
# ============================================================

def rename_columns(df):
    """
    Rename CSV columns so that they exactly match models.py.
    """

    rename_map = {}

    for column in df.columns:

        normalized = normalize_column_name(
            column
        )

        # ----------------------------------------------------
        # ID
        # ----------------------------------------------------

        if normalized == "id":

            rename_map[column] = "id"

        # ----------------------------------------------------
        # CASE NUMBER
        # ----------------------------------------------------

        elif normalized in [
            "case_number",
            "casenumber",
        ]:

            rename_map[column] = "case_number"

        # ----------------------------------------------------
        # DATE
        # ----------------------------------------------------

        elif normalized in [
            "date",
            "crime_date",
        ]:

            rename_map[column] = "date"

        # ----------------------------------------------------
        # BLOCK
        # ----------------------------------------------------

        elif normalized == "block":

            rename_map[column] = "block"

        # ----------------------------------------------------
        # IUCR
        # ----------------------------------------------------

        elif normalized in [
            "iucr",
            "iucr_code",
        ]:

            rename_map[column] = "iucr"

        # ----------------------------------------------------
        # PRIMARY TYPE
        # ----------------------------------------------------

        elif normalized in [
            "primary_type",
            "primarytype",
        ]:

            rename_map[column] = "primary_type"

        # ----------------------------------------------------
        # DESCRIPTION
        # ----------------------------------------------------

        elif normalized == "description":

            rename_map[column] = "description"

        # ----------------------------------------------------
        # LOCATION DESCRIPTION
        # ----------------------------------------------------

        elif normalized in [
            "location_description",
            "location_desc",
        ]:

            rename_map[column] = "location_desc"

        # ----------------------------------------------------
        # ARREST
        # ----------------------------------------------------

        elif normalized == "arrest":

            rename_map[column] = "arrest"

        # ----------------------------------------------------
        # DOMESTIC
        # ----------------------------------------------------

        elif normalized == "domestic":

            rename_map[column] = "domestic"

        # ----------------------------------------------------
        # BEAT
        # ----------------------------------------------------

        elif normalized in [
            "beat",
            "beat_num",
            "beat_number",
        ]:

            rename_map[column] = "beat_num"

        # ----------------------------------------------------
        # DISTRICT
        # ----------------------------------------------------

        elif normalized in [
            "district",
            "district_code",
            "district_name",
        ]:

            rename_map[column] = "district_name"

        # ----------------------------------------------------
        # WARD
        # ----------------------------------------------------

        elif normalized in [
            "ward",
            "ward_no",
            "ward_number",
        ]:

            rename_map[column] = "ward_no"

        # ----------------------------------------------------
        # COMMUNITY
        # ----------------------------------------------------

        elif normalized in [
            "community_area",
            "community_code",
            "community",
        ]:

            rename_map[column] = "community_code"

        # ----------------------------------------------------
        # FBI CODE
        # ----------------------------------------------------

        elif normalized in [
            "fbi_code",
            "fbi",
        ]:

            rename_map[column] = "fbi_code"

        # ----------------------------------------------------
        # X COORDINATE
        # ----------------------------------------------------

        elif normalized in [
            "x_coordinate",
            "x_coordinate_",
        ]:

            rename_map[column] = "x_coordinate"

        # ----------------------------------------------------
        # Y COORDINATE
        # ----------------------------------------------------

        elif normalized in [
            "y_coordinate",
            "y_coordinate_",
        ]:

            rename_map[column] = "y_coordinate"

        # ----------------------------------------------------
        # YEAR
        # ----------------------------------------------------

        elif normalized == "year":

            rename_map[column] = "year"

        # ----------------------------------------------------
        # DATE OF UPDATE
        # ----------------------------------------------------

        elif normalized in [
            "date_of_update",
            "updated_on",
            "updated",
            "date_of_update_",
        ]:

            rename_map[column] = "date_of_update"

        # ----------------------------------------------------
        # LATITUDE
        # ----------------------------------------------------

        elif normalized == "latitude":

            rename_map[column] = "latitude"

        # ----------------------------------------------------
        # LONGITUDE
        # ----------------------------------------------------

        elif normalized == "longitude":

            rename_map[column] = "longitude"

        # ----------------------------------------------------
        # LOCATION
        # ----------------------------------------------------

        elif normalized == "location":

            rename_map[column] = "location"

    return df.rename(
        columns=rename_map
    )


# ============================================================
# BOOLEAN CONVERSION
# ============================================================

def convert_boolean(value):
    """
    Convert boolean-like CSV values into Python booleans.
    """

    if pd.isna(value):
        return None

    if isinstance(value, bool):
        return value

    value = str(value).strip().lower()

    if value in [
        "true",
        "1",
        "yes",
        "y",
    ]:
        return True

    if value in [
        "false",
        "0",
        "no",
        "n",
    ]:
        return False

    return None


# ============================================================
# CLEAN DATABASE VALUE
# ============================================================

def clean_database_value(value):
    """
    Convert pandas values into SQLite/SQLAlchemy-safe
    Python values.
    """

    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()

    if hasattr(value, "item"):

        try:
            return value.item()

        except (
            ValueError,
            AttributeError
        ):
            pass

    return value


# ============================================================
# LOAD CRIME DATA
# ============================================================

def load_crime_data():
    """
    Load and clean the Chicago crime CSV and insert it
    into the Crime table.

    The original dataset ID is preserved and inserted
    directly into the database.

    Final database structure:

        24 columns INCLUDING id

        22 original dataset columns
        + month
        + date_of_week

    The ID is NOT auto-generated.
    """

    print("\n")
    print("=" * 80)
    print("CHICAGO CRIME DATA INGESTION")
    print("=" * 80)

    # ========================================================
    # 1. FIND CSV
    # ========================================================

    csv_path = find_master_csv()

    print("\nCSV FILE:")
    print(csv_path)

    # ========================================================
    # 2. READ CSV
    # ========================================================

    print("\nReading CSV...")

    df = pd.read_csv(
        csv_path,
        low_memory=False
    )

    # ========================================================
    # 3. BEFORE CLEANING
    # ========================================================

    print("\n")
    print("=" * 80)
    print("BEFORE CLEANING")
    print("=" * 80)

    print(
        f"Rows    : {df.shape[0]:,}"
    )

    print(
        f"Columns : {df.shape[1]}"
    )

    print("\nFirst 10 rows:")

    print(
        df.head(10)
    )

    print(
        "\nSchema and Data Types BEFORE cleaning:"
    )

    print(
        df.dtypes
    )

    print(
        "\nOriginal Column Names:"
    )

    print(
        list(df.columns)
    )

    # ========================================================
    # 4. STANDARDIZE COLUMN NAMES
    # ========================================================

    df = rename_columns(df)

    print("\n")
    print("=" * 80)
    print("STANDARDIZED COLUMN NAMES")
    print("=" * 80)

    print(
        list(df.columns)
    )

    # ========================================================
    # 5. VERIFY ID COLUMN
    # ========================================================

    if "id" not in df.columns:

        raise ValueError(
            "The dataset does not contain an 'id' column. "
            "The original dataset ID is required."
        )

    # ========================================================
    # 6. MISSING VALUES
    # ========================================================

    missing_percentage = pd.Series(
        np.round(
            np.mean(df.isnull().to_numpy(), axis=0) * 100,
            2
        ),
        index=df.columns
    )

    # ========================================================
    # 7. SAVE MISSING VALUE REPORT
    # ========================================================

    report_folder = Path(
        current_app.config["REPORT_FOLDER"]
    )

    report_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    missing_report = pd.DataFrame(
        {
            "column_name":
                missing_percentage.index,

            "missing_count":
                df.isnull().sum().values,

            "missing_percentage":
                missing_percentage.values
        }
    )

    missing_report.to_csv(
        report_folder /
        "missing_values_report.csv",
        index=False
    )

    # ========================================================
    # 8. DROP COLUMNS > 50% MISSING
    # ========================================================

    columns_to_drop = (
        missing_percentage[
            missing_percentage > 50
        ]
        .index
        .tolist()
    )

    # Never drop the ID column.
    if "id" in columns_to_drop:
        columns_to_drop.remove("id")

    if columns_to_drop:

        print(
            "\nColumns with more than 50% missing:"
        )

        print(
            columns_to_drop
        )

        df = df.drop(
            columns=columns_to_drop
        )

    else:

        print(
            "\nNo columns have more than 50% missing values."
        )

    # ========================================================
    # 9. CONVERT DATE
    # ========================================================

    if "date" in df.columns:

        print(
            "\nConverting Date column..."
        )

        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

    # ========================================================
    # 10. GENERATE DATE FEATURES
    # ========================================================

    if "date" in df.columns:

        # ----------------------------------------------------
        # YEAR
        # ----------------------------------------------------

        df["year"] = (
            df["date"]
            .dt.year
        )

        # ----------------------------------------------------
        # MONTH
        # ----------------------------------------------------

        df["month"] = (
            df["date"]
            .dt.month
        )

        # ----------------------------------------------------
        # DATE OF WEEK
        # ----------------------------------------------------

        df["date_of_week"] = (
            df["date"]
            .dt.day_name()
        )

    # ========================================================
    # 11. STANDARDIZE CATEGORICAL COLUMNS
    # ========================================================

    categorical_columns = [
        "case_number",
        "block",
        "iucr",
        "primary_type",
        "description",
        "location_desc",
        "beat_num",
        "district_name",
        "ward_no",
        "community_code",
        "fbi_code",
        "date_of_update",
        "date_of_week",
        "location"
    ]

    for column in categorical_columns:

        if column in df.columns:

            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
            )

    # ========================================================
    # 12. BOOLEAN CONVERSION
    # ========================================================

    if "arrest" in df.columns:

        df["arrest"] = (
            df["arrest"]
            .apply(convert_boolean)
        )

    if "domestic" in df.columns:

        df["domestic"] = (
            df["domestic"]
            .apply(convert_boolean)
        )

    # ========================================================
    # 13. NUMERIC CONVERSION
    # ========================================================

    numeric_columns = [
        "id",
        "x_coordinate",
        "y_coordinate",
        "latitude",
        "longitude",
        "month",
        "year"
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # ========================================================
    # 14. VALIDATE DATASET IDs
    # ========================================================

    if df["id"].isna().any():

        missing_id_count = int(
            df["id"].isna().sum()
        )

        raise ValueError(
            f"The dataset contains "
            f"{missing_id_count:,} rows without an ID. "
            f"Every crime record must have an ID."
        )

    # Check duplicate IDs.

    duplicate_id_count = int(
        df["id"].duplicated().sum()
    )

    if duplicate_id_count > 0:

        raise ValueError(
            f"The dataset contains "
            f"{duplicate_id_count:,} duplicate IDs. "
            f"IDs must be unique because ID is the primary key."
        )

    # ========================================================
    # 15. INTEGER COLUMNS
    # ========================================================

    df["id"] = (
        df["id"]
        .round()
        .astype("Int64")
    )

    if "year" in df.columns:

        df["year"] = (
            df["year"]
            .round()
            .astype("Int64")
        )

    if "month" in df.columns:

        df["month"] = (
            df["month"]
            .round()
            .astype("Int64")
        )

    # ========================================================
    # 16. AFTER CLEANING
    # ========================================================

    print("\n")
    print("=" * 80)
    print("AFTER CLEANING AND FEATURE GENERATION")
    print("=" * 80)

    print(
        f"Rows    : {df.shape[0]:,}"
    )

    print(
        f"Columns : {df.shape[1]}"
    )

    print(
        "\nSchema and Data Types AFTER cleaning:"
    )

    print(
        df.dtypes
    )

    print(
        "\nColumns AFTER feature generation:"
    )

    print(
        list(df.columns)
    )

    print(
        "\nFirst 10 cleaned rows:"
    )

    print(
        df.head(10)
    )

    # ========================================================
    # 17. ID VALIDATION DISPLAY
    # ========================================================

    print("\n")
    print("=" * 80)
    print("DATASET ID VALIDATION")
    print("=" * 80)

    print(
        f"Minimum ID : {df['id'].min()}"
    )

    print(
        f"Maximum ID : {df['id'].max()}"
    )

    print(
        f"Unique IDs : {df['id'].nunique():,}"
    )

    print(
        "IDs will be preserved from the original dataset."
    )

    # ========================================================
    # 18. DATE FEATURES DISPLAY
    # ========================================================

    print("\n")
    print("=" * 80)
    print("DATE-DERIVED FEATURES")
    print("=" * 80)

    date_feature_columns = [
        "date",
        "date_of_week",
        "month",
        "year"
    ]

    existing_date_features = [
        column
        for column in date_feature_columns
        if column in df.columns
    ]

    if existing_date_features:

        print(
            df[
                existing_date_features
            ].head(10)
        )

    # ========================================================
    # 19. UNIQUE CRIME TYPES
    # ========================================================

    if "primary_type" in df.columns:

        unique_crimes = (
            df["primary_type"]
            .nunique(
                dropna=True
            )
        )

        print("\n")
        print("=" * 80)
        print("UNIQUE CRIME TYPES")
        print("=" * 80)

        print(
            unique_crimes
        )

    # ========================================================
    # 20. DATE VALIDATION
    # ========================================================

    if "date" in df.columns:

        invalid_dates = (
            df["date"]
            .isna()
            .sum()
        )

        print("\n")
        print("=" * 80)
        print("DATE VALIDATION")
        print("=" * 80)

        print(
            f"Invalid / missing dates: "
            f"{invalid_dates:,}"
        )

        valid_dates = (
            df["date"]
            .dropna()
        )

        if not valid_dates.empty:

            print(
                "Minimum date:",
                valid_dates.min()
            )

            print(
                "Maximum date:",
                valid_dates.max()
            )

    # ========================================================
    # 21. DATABASE COLUMNS
    #
    # IMPORTANT:
    #
    # The original dataset ID is included here.
    #
    # Therefore the ID from the CSV will be inserted
    # directly into the Crime table.
    #
    # Total:
    #
    # 22 original dataset columns
    # + 2 derived columns
    # = 24 database columns
    # ========================================================

    database_columns = [

        # ----------------------------------------------------
        # ORIGINAL DATASET COLUMNS
        # ----------------------------------------------------

        "id",

        "case_number",

        "date",

        "block",

        "iucr",

        "primary_type",

        "description",

        "location_desc",

        "arrest",

        "domestic",

        "beat_num",

        "district_name",

        "ward_no",

        "community_code",

        "fbi_code",

        "x_coordinate",

        "y_coordinate",

        "year",

        "date_of_update",

        "latitude",

        "longitude",

        "location",

        # ----------------------------------------------------
        # DERIVED DATE COLUMNS
        # ----------------------------------------------------

        "month",

        "date_of_week"
    ]

    # ========================================================
    # 22. ADD MISSING DATABASE COLUMNS
    # ========================================================

    for column in database_columns:

        if column not in df.columns:

            if column == "id":

                raise ValueError(
                    "The required 'id' column is missing."
                )

            df[column] = None

    # ========================================================
    # 23. PREPARE DATABASE DATAFRAME
    # ========================================================

    database_df = df[
        database_columns
    ].copy()

    # Convert pandas missing values to None.

    database_df = database_df.astype(
        object
    )

    database_df = database_df.where(
        pd.notna(database_df),
        None
    )

    # ========================================================
    # 24. CONVERT RECORDS TO DICTIONARIES
    # ========================================================

    records = []

    for row in database_df.to_dict(
        orient="records"
    ):

        cleaned_row = {
            column: clean_database_value(
                row.get(column)
            )
            for column in database_columns
        }

        records.append(
            cleaned_row
        )

    # ========================================================
    # 25. INSERT INTO SQLITE
    # ========================================================

    print("\n")
    print("=" * 80)
    print("INSERTING DATA INTO SQLITE")
    print("=" * 80)

    # --------------------------------------------------------
    # Delete previous records
    # --------------------------------------------------------

    db.session.query(
        Crime
    ).delete()

    db.session.commit()

    # ========================================================
    # 26. INSERT IN CHUNKS
    # ========================================================

    chunk_size = 5000

    total_records = len(
        records
    )

    for start in range(
        0,
        total_records,
        chunk_size
    ):

        chunk = records[
            start:start + chunk_size
        ]

        objects = [
            Crime(**row)
            for row in chunk
        ]

        db.session.bulk_save_objects(
            objects
        )

        db.session.commit()

        inserted_count = min(
            start + chunk_size,
            total_records
        )

        print(
            f"Inserted {inserted_count:,} "
            f"/ {total_records:,}"
        )

    # ========================================================
    # 27. FINAL INFORMATION
    # ========================================================

    print("\n")
    print("=" * 80)
    print("DATA LOADING COMPLETED")
    print("=" * 80)

    print(
        f"Total records inserted: "
        f"{total_records:,}"
    )

    print(
        "Original dataset columns: 22"
    )

    print(
        "Derived columns added: 2"
    )

    print(
        f"Total database columns: "
        f"{len(database_columns)}"
    )

    print(
        "Dataset IDs preserved: YES"
    )

    # ========================================================
    # 28. RETURN METADATA
    # ========================================================

    return {

        "rows": int(
            len(df)
        ),

        "cleaned_rows": int(
            len(database_df)
        ),

        "columns": int(
            len(df.columns)
        ),

        "cleaned_columns": int(
            len(database_df.columns)
        ),

        "database_columns": int(
            len(database_columns)
        ),

        "unique_crime_types": (
            int(
                df["primary_type"]
                .nunique()
            )
            if "primary_type" in df.columns
            else 0
        ),

        "csv_path": str(
            csv_path
        )
    }
