#!/usr/bin/env python
"""Script to load data and generate charts"""

from app import app

from data_loader import load_crime_data
from analysis import get_dataframe, generate_charts
from database import build_database_reporting


def main():

    with app.app_context():

        print("\n========================================")
        print("CHICAGO CRIME ANALYTICS")
        print("========================================\n")

        # =================================================
        # 1. LOAD CRIME DATA
        # =================================================

        print("Loading crime data...")

        metadata = load_crime_data()

        cleaned_rows = metadata.get(
            "cleaned_rows",
            0
        )

        print(
            f"Loaded {cleaned_rows:,} crime records"
        )

        if cleaned_rows == 0:

            print(
                "\nNo crime records were loaded."
            )

            print(
                "Please check the data file and "
                "data_loader.py."
            )

            return

        # =================================================
        # 2. READ DATABASE INTO DATAFRAME
        # =================================================

        print("\nGetting dataframe...")

        df = get_dataframe()

        print(
            f"Dataframe shape: {df.shape}"
        )

        if df.empty:

            print(
                "\nThe database contains no crime records."
            )

            return

        print(
            f"Database records available for analysis: "
            f"{len(df):,}"
        )

        # =================================================
        # 3. GENERATE CHARTS AND CSV REPORTS
        # =================================================

        print("\nGenerating charts and analysis reports...")

        generate_charts(df)

        print(
            "Charts and analysis reports generated successfully!"
        )

        # =================================================
        # 4. BUILD DATABASE SUMMARY TABLES AND VIEWS
        # =================================================

        print(
            "\nBuilding database summary tables and views..."
        )

        build_database_reporting()

        print(
            "Database reports generated successfully!"
        )

        # =================================================
        # 5. COMPLETION MESSAGE
        # =================================================

        print(
            "\n========================================"
        )

        print(
            "ALL PROCESSING COMPLETED SUCCESSFULLY"
        )

        print(
            "========================================"
        )

        print(
            "\nCharts should now be available at:"
        )

        print(
            "http://127.0.0.1:5000/analysis"
        )

        print()


if __name__ == "__main__":
    main()
