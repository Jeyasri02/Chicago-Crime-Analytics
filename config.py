from pathlib import Path


# =========================================================
# PROJECT DIRECTORIES
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

INSTANCE_DIR = BASE_DIR / "instance"
DATA_DIR = BASE_DIR / "data"
REPORT_DIR = BASE_DIR / "reports"
CHART_DIR = BASE_DIR / "static" / "charts"


# =========================================================
# APPLICATION CONFIGURATION
# =========================================================

class Config:

    # -----------------------------------------------------
    # Flask secret key
    # -----------------------------------------------------

    SECRET_KEY = "chicago-crime-analytics"

    # -----------------------------------------------------
    # SQLite database
    #
    # Database file:
    # instance/chicago_crime.db
    # -----------------------------------------------------

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///"
        + str((INSTANCE_DIR / "chicago_crime.db").resolve())
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # -----------------------------------------------------
    # Data directory
    # -----------------------------------------------------

    DATA_FOLDER = DATA_DIR

    # -----------------------------------------------------
    # Reports directory
    # -----------------------------------------------------

    REPORT_FOLDER = REPORT_DIR

    # -----------------------------------------------------
    # Chart directory
    # -----------------------------------------------------

    CHART_FOLDER = CHART_DIR
