import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
from flask import current_app

from extensions import db


def generate_crime_year_chart():

    # Get chart folder
    chart_folder = Path(
        current_app.config["CHART_FOLDER"]
    )

    # Make sure folder exists
    chart_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    # Read database VIEW into Pandas DataFrame
    with db.engine.connect() as conn:

        df = pd.read_sql(
            "SELECT * FROM vw_crime_yearly ORDER BY year",
            conn
        )

    print(df)

    # Generate graph
    plt.figure(figsize=(10, 6))

    plt.plot(
        df["year"],
        df["crime_count"],
        marker="o"
    )

    plt.xlabel("Year")
    plt.ylabel("Crime Count")
    plt.title("Crime Count per Year")

    plt.xticks(
        df["year"],
        rotation=45
    )

    plt.tight_layout()

    # Save inside CHART_FOLDER
    plt.savefig(
        chart_folder / "crime_by_year.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()
