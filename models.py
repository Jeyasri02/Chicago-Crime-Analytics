from datetime import datetime

from extensions import db


class Crime(db.Model):
    """
    Chicago Crime database model.

    Total database columns:
        24

    Original dataset columns:
        22

    Additional derived columns:
        month
        date_of_week

    The original year column is retained.
    """

    __tablename__ = "crime"

    # =========================================================
    # PRIMARY KEY
    # =========================================================

    id = db.Column(
        db.Integer,
        primary_key=True,
        
    )

    # =========================================================
    # ORIGINAL DATASET COLUMNS
    # =========================================================

    case_number = db.Column(
        db.String(50),
        nullable=True
    )

    date = db.Column(
        db.DateTime,
        nullable=True
    )

    block = db.Column(
        db.String(150),
        nullable=True
    )

    iucr = db.Column(
        db.String(20),
        nullable=True
    )

    primary_type = db.Column(
        db.String(100),
        nullable=True
    )

    description = db.Column(
        db.String(255),
        nullable=True
    )

    location_desc = db.Column(
        db.String(255),
        nullable=True
    )

    arrest = db.Column(
        db.Boolean,
        nullable=True
    )

    domestic = db.Column(
        db.Boolean,
        nullable=True
    )

    beat_num = db.Column(
        db.String(20),
        nullable=True
    )

    district_name = db.Column(
        db.String(100),
        nullable=True
    )

    ward_no = db.Column(
        db.String(20),
        nullable=True
    )

    community_code = db.Column(
        db.String(20),
        nullable=True
    )

    fbi_code = db.Column(
        db.String(20),
        nullable=True
    )

    x_coordinate = db.Column(
        db.Float,
        nullable=True
    )

    y_coordinate = db.Column(
        db.Float,
        nullable=True
    )

    year = db.Column(
        db.Integer,
        nullable=True
    )

    date_of_update = db.Column(
        db.String(100),
        nullable=True
    )

    latitude = db.Column(
        db.Float,
        nullable=True
    )

    longitude = db.Column(
        db.Float,
        nullable=True
    )

    location = db.Column(
        db.String(255),
        nullable=True
    )

    # =========================================================
    # DERIVED DATE FEATURES
    # =========================================================

    month = db.Column(
        db.Integer,
        nullable=True
    )

    date_of_week = db.Column(
        db.String(20),
        nullable=True
    )

    # =========================================================
    # REPRESENTATION
    # =========================================================

    def __repr__(self):
        return (
            f"<Crime "
            f"id={self.id}, "
            f"case_number={self.case_number}, "
            f"primary_type={self.primary_type}, "
            f"year={self.year}>"
        )
