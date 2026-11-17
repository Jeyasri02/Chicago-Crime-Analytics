from pathlib import Path
from datetime import datetime
from charts import generate_crime_year_chart

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for
)

from models import Crime
from extensions import db

from data_loader import load_crime_data

from analysis import (
    get_dataframe,
    crimes_per_year,
    top_crimes,
    calculate_arrest_rate,
    arrest_rate_by_year,
    top_community_areas,
    top_iucr_codes,
    top_fbi_codes,
    top_locations,
    crimes_by_month,
    crimes_by_hour,
    community_area_iqr,
    generate_charts
)

from database import build_database_reporting


main = Blueprint(
    "main",
    __name__
)


# =========================================================
# Helper function - Parse Date
# =========================================================

def parse_date(date_value):
    """
    Convert HTML date/datetime input into a Python datetime object.

    Supports:
    - YYYY-MM-DD
    - YYYY-MM-DDTHH:MM
    - YYYY-MM-DD HH:MM
    - YYYY-MM-DDTHH:MM:SS
    """

    if not date_value:
        return None

    formats = [
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d"
    ]

    for date_format in formats:

        try:

            return datetime.strptime(
                date_value,
                date_format
            )

        except ValueError:

            continue

    return None


# =========================================================
# Helper function - Generate Date Features
# =========================================================

def generate_date_features(date):
    """
    Generate persistent features from the crime date.

    Returns:
        year
        month
        date_of_week
    """

    if date is None:

        return {
            "year": None,
            "month": None,
            "date_of_week": None
        }

    return {
        "year": date.year,
        "month": date.month,
        "date_of_week": date.strftime("%A")
    }


# =========================================================
# Dashboard
# =========================================================

@main.route("/")
def dashboard():

    total_crimes = Crime.query.count()

    crime_types = (
        Crime.query
        .with_entities(
            Crime.primary_type
        )
        .distinct()
        .count()
    )

    arrests = (
        Crime.query
        .filter_by(
            arrest=True
        )
        .count()
    )

    if total_crimes > 0:

        arrest_rate = round(
            arrests /
            total_crimes *
            100,
            2
        )

    else:

        arrest_rate = 0

    years = [
        row[0]
        for row in (
            Crime.query
            .with_entities(
                Crime.year
            )
            .distinct()
            .all()
        )
        if row[0] is not None
    ]

    return render_template(
        "dashboard.html",

        total_crimes=total_crimes,

        crime_types=crime_types,

        arrests=arrests,

        arrest_rate=arrest_rate,

        min_year=min(years)
        if years else None,

        max_year=max(years)
        if years else None
    )


# =========================================================
# Automatically load dataset
# =========================================================

@main.route("/load-data")
def load_data():

    try:

        metadata = load_crime_data()

        df = get_dataframe()

        generate_charts(df)

        build_database_reporting()

        flash(
            (
                f"Successfully processed "
                f"{metadata['cleaned_rows']:,} "
                "crime records."
            ),
            "success"
        )

    except Exception as error:

        flash(
            f"Data processing failed: {error}",
            "danger"
        )

    return redirect(
        url_for("main.dashboard")
    )


# =========================================================
# CRUD - Crime Records
# =========================================================


# =========================================================
# READ - Display all crime records
# =========================================================

@main.route("/crime-records")
def crime_records():

    crimes = (
        Crime.query
        .order_by(
            Crime.id.desc()
        )
        .all()
    )

    return render_template(
        "crime_records.html",
        crimes=crimes
    )


# =========================================================
# CREATE - Add a new crime record
# =========================================================

@main.route(
    "/crime-records/add",
    methods=["GET", "POST"]
)
def add_crime():
    print("******** ADD CRIME ROUTE CALLED ********")
    print("METHOD:", request.method)

    if request.method == "POST":
        print("******** POST RECEIVED ********")
        print("FORM DATA:", request.form)

        try:

            # -------------------------------------------------
            # Parse Date
            # -------------------------------------------------

            date_value = request.form.get(
                "date",
                ""
            ).strip()

            date = parse_date(
                date_value
            )

            if date_value and date is None:

                flash(
                    "Invalid date format.",
                    "danger"
                )

                return render_template(
                    "add_crime.html"
                )

            # -------------------------------------------------
            # Generate Date Features
            # -------------------------------------------------

            date_features = generate_date_features(
                date
            )

            year = date_features["year"]

            month = date_features["month"]

            date_of_week = date_features[
                "date_of_week"
            ]

            # -------------------------------------------------
            # Coordinates
            # -------------------------------------------------

            x_coordinate_value = request.form.get(
                "x_coordinate",
                ""
            ).strip()

            y_coordinate_value = request.form.get(
                "y_coordinate",
                ""
            ).strip()

            latitude_value = request.form.get(
                "latitude",
                ""
            ).strip()

            longitude_value = request.form.get(
                "longitude",
                ""
            ).strip()

            # -------------------------------------------------
            # Create Crime Object
            # -------------------------------------------------

            crime = Crime(

                case_number=request.form.get(
                    "case_number",
                    ""
                ).strip() or None,

                date=date,

                block=request.form.get(
                    "block",
                    ""
                ).strip() or None,

                iucr=request.form.get(
                    "iucr",
                    ""
                ).strip() or None,

                primary_type=request.form.get(
                    "primary_type",
                    ""
                ).strip() or None,

                description=request.form.get(
                    "description",
                    ""
                ).strip() or None,

                location_desc=request.form.get(
                    "location_desc",
                    ""
                ).strip() or None,

                arrest=(
                    request.form.get("arrest")
                    == "true"
                ),

                domestic=(
                    request.form.get("domestic")
                    == "true"
                ),

                beat_num=request.form.get(
                    "beat_num",
                    ""
                ).strip() or None,

                district_name=request.form.get(
                    "district_name",
                    ""
                ).strip() or None,

                ward_no=request.form.get(
                    "ward_no",
                    ""
                ).strip() or None,

                community_code=request.form.get(
                    "community_code",
                    ""
                ).strip() or None,

                fbi_code=request.form.get(
                    "fbi_code",
                    ""
                ).strip() or None,

                x_coordinate=(
                    float(x_coordinate_value)
                    if x_coordinate_value
                    else None
                ),

                y_coordinate=(
                    float(y_coordinate_value)
                    if y_coordinate_value
                    else None
                ),

                # ---------------------------------------------
                # Persisted Date Features
                # ---------------------------------------------

                year=year,

                month=month,

                date_of_week=date_of_week,

                date_of_update=request.form.get(
                    "date_of_update",
                    ""
                ).strip() or None,

                latitude=(
                    float(latitude_value)
                    if latitude_value
                    else None
                ),

                longitude=(
                    float(longitude_value)
                    if longitude_value
                    else None
                ),

                location=request.form.get(
                    "location",
                    ""
                ).strip() or None
            )

            # -------------------------------------------------
            # Save Crime
            # -------------------------------------------------

            db.session.add(
                crime
            )

            db.session.commit()

            flash(
                "Crime record created successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "main.crime_records"
                )
            )

        except ValueError:

            db.session.rollback()

            flash(
                "Please enter valid numeric values for coordinates.",
                "danger"
            )

        except Exception as error:

            db.session.rollback()

            flash(
                f"Failed to create crime record: {error}",
                "danger"
            )

    return render_template(
        "add_crime.html"
    )


# =========================================================
# UPDATE - Edit an existing crime record
# =========================================================

@main.route(
    "/crime-records/edit/<int:crime_id>",
    methods=["GET", "POST"]
)
def edit_crime(crime_id):

    crime = Crime.query.get_or_404(
        crime_id
    )

    if request.method == "POST":

        try:

            # -------------------------------------------------
            # Parse Date
            # -------------------------------------------------

            date_value = request.form.get(
                "date",
                ""
            ).strip()

            date = parse_date(
                date_value
            )

            if date_value and date is None:

                flash(
                    "Invalid date format.",
                    "danger"
                )

                return render_template(
                    "edit_crime.html",
                    crime=crime
                )

            # -------------------------------------------------
            # Generate Date Features
            # -------------------------------------------------

            date_features = generate_date_features(
                date
            )

            year = date_features["year"]

            month = date_features["month"]

            date_of_week = date_features[
                "date_of_week"
            ]

            # -------------------------------------------------
            # Coordinates
            # -------------------------------------------------

            x_coordinate_value = request.form.get(
                "x_coordinate",
                ""
            ).strip()

            y_coordinate_value = request.form.get(
                "y_coordinate",
                ""
            ).strip()

            latitude_value = request.form.get(
                "latitude",
                ""
            ).strip()

            longitude_value = request.form.get(
                "longitude",
                ""
            ).strip()

            # -------------------------------------------------
            # Update Crime Fields
            # -------------------------------------------------

            crime.case_number = request.form.get(
                "case_number",
                ""
            ).strip() or None

            crime.date = date

            crime.block = request.form.get(
                "block",
                ""
            ).strip() or None

            crime.iucr = request.form.get(
                "iucr",
                ""
            ).strip() or None

            crime.primary_type = request.form.get(
                "primary_type",
                ""
            ).strip() or None

            crime.description = request.form.get(
                "description",
                ""
            ).strip() or None

            crime.location_desc = request.form.get(
                "location_desc",
                ""
            ).strip() or None

            crime.arrest = (
                request.form.get("arrest")
                == "true"
            )

            crime.domestic = (
                request.form.get("domestic")
                == "true"
            )

            crime.beat_num = request.form.get(
                "beat_num",
                ""
            ).strip() or None

            crime.district_name = request.form.get(
                "district_name",
                ""
            ).strip() or None

            crime.ward_no = request.form.get(
                "ward_no",
                ""
            ).strip() or None

            crime.community_code = request.form.get(
                "community_code",
                ""
            ).strip() or None

            crime.fbi_code = request.form.get(
                "fbi_code",
                ""
            ).strip() or None

            crime.x_coordinate = (
                float(x_coordinate_value)
                if x_coordinate_value
                else None
            )

            crime.y_coordinate = (
                float(y_coordinate_value)
                if y_coordinate_value
                else None
            )

            # -------------------------------------------------
            # Update Persisted Date Features
            # -------------------------------------------------

            crime.year = year

            crime.month = month

            crime.date_of_week = date_of_week

            # -------------------------------------------------
            # Other Fields
            # -------------------------------------------------

            crime.date_of_update = request.form.get(
                "date_of_update",
                ""
            ).strip() or None

            crime.latitude = (
                float(latitude_value)
                if latitude_value
                else None
            )

            crime.longitude = (
                float(longitude_value)
                if longitude_value
                else None
            )

            crime.location = request.form.get(
                "location",
                ""
            ).strip() or None

            # -------------------------------------------------
            # Save Changes
            # -------------------------------------------------

            db.session.commit()

            flash(
                "Crime record updated successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "main.crime_records"
                )
            )

        except ValueError:

            db.session.rollback()

            flash(
                "Please enter valid numeric values for coordinates.",
                "danger"
            )

        except Exception as error:

            db.session.rollback()

            flash(
                f"Failed to update crime record: {error}",
                "danger"
            )

    return render_template(
        "edit_crime.html",
        crime=crime
    )


# =========================================================
# DELETE - Delete a crime record
# =========================================================

@main.route(
    "/crime-records/delete/<int:crime_id>",
    methods=["POST"]
)
def delete_crime(crime_id):

    crime = Crime.query.get_or_404(
        crime_id
    )

    try:

        db.session.delete(
            crime
        )

        db.session.commit()

        flash(
            "Crime record deleted successfully.",
            "success"
        )

    except Exception as error:

        db.session.rollback()

        flash(
            f"Failed to delete crime record: {error}",
            "danger"
        )

    return redirect(
        url_for(
            "main.crime_records"
        )
    )


# =========================================================
# Analysis page
# =========================================================

@main.route("/analysis")
def analysis():

    df = get_dataframe()

    print(
        "\n========== IUCR DEBUG =========="
    )

    print(
        "IUCR column exists:",
        "iucr" in df.columns
    )

    if "iucr" in df.columns:

        print(
            "IUCR non-null count:",
            df["iucr"].notna().sum()
        )

        print(
            "IUCR unique count:",
            df["iucr"].nunique()
        )

        print(
            "Top IUCR values:"
        )

        print(
            df["iucr"]
            .value_counts()
            .head(10)
        )

    print(
        "================================"
    )

    if df.empty:

        return render_template(
            "analysis.html",
            empty=True
        )

    yearly = crimes_per_year(
        df
    )

    categories = top_crimes(
        df,
        10
    )

    communities = top_community_areas(
        df,
        10
    )

    iucr = top_iucr_codes(
        df,
        10
    )

    fbi = top_fbi_codes(
        df,
        10
    )

    locations = top_locations(
        df,
        10
    )

    arrest_yearly = arrest_rate_by_year(
        df
    )

    monthly = crimes_by_month(
        df
    )

    hourly = crimes_by_hour(
        df
    )

    outliers = community_area_iqr(
        df
    )

    # -----------------------------------------------------
    # Most common crime
    # -----------------------------------------------------

    most_common_crime = (
        categories.iloc[0]["primary_type"]
        if not categories.empty
        else "N/A"
    )

    # -----------------------------------------------------
    # Highest month
    # -----------------------------------------------------

    highest_month = (
        int(
            monthly.loc[
                monthly["crime_count"].idxmax(),
                "month"
            ]
        )
        if not monthly.empty
        else None
    )

    # -----------------------------------------------------
    # Busiest hour
    # -----------------------------------------------------

    busiest_hour = (
        int(
            hourly.loc[
                hourly["crime_count"].idxmax(),
                "hour"
            ]
        )
        if not hourly.empty
        else None
    )

    return render_template(
        "analysis.html",

        empty=False,

        total=len(df),

        arrest_rate=calculate_arrest_rate(
            df
        ),

        most_common_crime=most_common_crime,

        highest_month=highest_month,

        busiest_hour=busiest_hour,

        yearly=yearly.to_dict(
            "records"
        ),

        categories=categories.to_dict(
            "records"
        ),

        communities=communities.to_dict(
            "records"
        ),

        iucr=iucr.to_dict(
            "records"
        ),

        fbi=fbi.to_dict(
            "records"
        ),

        locations=locations.to_dict(
            "records"
        ),

        arrest_yearly=arrest_yearly.to_dict(
            "records"
        ),

        monthly=monthly.to_dict(
            "records"
        ),

        hourly=hourly.to_dict(
            "records"
        ),

        outliers=outliers.to_dict(
            "records"
        )
    )


# =========================================================
# Data Quality
# =========================================================

@main.route("/data-quality")
def data_quality():

    report_file = (
        Path(
            current_app.config[
                "REPORT_FOLDER"
            ]
        )
        /
        "missing_values_report.csv"
    )

    if not report_file.exists():

        return render_template(
            "data_quality.html",
            rows=[]
        )

    import pandas as pd

    df = pd.read_csv(
        report_file
    )

    return render_template(
        "data_quality.html",
        rows=df.to_dict(
            "records"
        )
    )


# =========================================================
# Reports
# =========================================================
@main.route("/reports")
def reports():

    # Generate graph from database VIEW
    generate_crime_year_chart()

    folder = Path(
        current_app.config["REPORT_FOLDER"]
    )

    files = sorted(
        [
            file.name
            for file in folder.glob("*")
            if file.is_file()
        ]
    )

    # Report Charts
    chart_folder = Path(
        current_app.config["CHART_FOLDER"]
    )

    crime_count_chart = (
        "crime_by_year.png"
        if (
            chart_folder /
            "crime_by_year.png"
        ).exists()
        else None
    )

    arrest_count_chart = (
        "arrest_count_by_year.png"
        if (
            chart_folder /
            "arrest_count_by_year.png"
        ).exists()
        else None
    )

    return render_template(
        "reports.html",
        files=files,
        crime_count_chart=crime_count_chart,
        arrest_count_chart=arrest_count_chart
    )

# =========================================================
# Download report
# =========================================================

@main.route(
    "/download-report/<filename>"
)
def download_report(filename):

    return send_from_directory(

        current_app.config[
            "REPORT_FOLDER"
        ],

        filename,

        as_attachment=True
    )


# =========================================================
# Serve charts
# =========================================================

@main.route(
    "/chart/<filename>"
)
def serve_chart(filename):

    return send_from_directory(

        current_app.config[
            "CHART_FOLDER"
        ],

        filename
    )
