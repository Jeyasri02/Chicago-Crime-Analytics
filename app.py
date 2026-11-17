from pathlib import Path

from flask import Flask

from config import Config

from extensions import db

from routes import main

from models import Crime

from data_loader import load_crime_data
from analysis import get_dataframe, generate_charts

from database import build_database_reporting



def create_app():

    app = Flask(
        __name__
    )

    app.config.from_object(
        Config
    )

    # Make directories

    Path(
        app.config["DATA_FOLDER"]
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    Path(
        app.config["REPORT_FOLDER"]
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    Path(
        app.config["CHART_FOLDER"]
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    Path(
        Path(app.config["SQLALCHEMY_DATABASE_URI"].replace(
            "sqlite:///",
            ""
        ))
    ).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Initialize database

    db.init_app(
        app
    )

    # Register routes

    app.register_blueprint(
        main
    )

    # Create database tables and load dataset

    with app.app_context():

        #db.drop_all()
        db.create_all()
        build_database_reporting()

        print("\n" + "=" * 80)
        print("DATABASE TABLES CREATED")
        print("=" * 80)

        try:

            metadata = load_crime_data()

            # Generate charts after loading the dataset
            df = get_dataframe()

            generate_charts(df)

            print("\n" + "=" * 80)
            print("DATASET LOADED SUCCESSFULLY")
            print("=" * 80)

            print("Rows:", metadata["cleaned_rows"])
            print("Columns:", metadata["cleaned_columns"])

            print("\nCharts generated successfully.")

        except Exception as error:

            print("\n" + "=" * 80)
            print("DATASET LOADING FAILED")
            print("=" * 80)

            print(error)
    return app


app = create_app()


if __name__ == "__main__":

    app.run(
        debug=True
    )
