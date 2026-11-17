from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns

from flask import current_app
from sqlalchemy import create_engine


# =========================================================
# CHART CONFIGURATION
# =========================================================

CHART_SIZE = (10, 5)
CHART_DPI = 150


# =========================================================
# SAVE CHART
# =========================================================

def save_chart(fig, chart_path):
    """
    Save a chart as a PNG image.
    """

    chart_path = Path(chart_path)

    chart_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    fig.set_size_inches(
        CHART_SIZE[0],
        CHART_SIZE[1]
    )

    fig.tight_layout(
        pad=1.2
    )

    fig.savefig(
        chart_path,
        dpi=CHART_DPI,
        facecolor="white",
        bbox_inches="tight"
    )

    plt.close(fig)

    print(
        f"Chart generated: {chart_path}"
    )


# =========================================================
# NORMALIZE BOOLEAN COLUMN
# =========================================================

def normalize_boolean(series):
    """
    Convert boolean-like values into True/False/NaN.

    Missing values remain NaN instead of being converted
    to False.
    """

    if series is None:
        return pd.Series(dtype="boolean")

    if pd.api.types.is_bool_dtype(series):
        return series.astype("boolean")

    return (
        series
        .astype("string")
        .str.strip()
        .str.upper()
        .map(
            {
                "TRUE": True,
                "FALSE": False,
                "1": True,
                "0": False,
                "YES": True,
                "NO": False,
                "Y": True,
                "N": False,
            }
        )
        .astype("boolean")
    )


# =========================================================
# READ DATABASE INTO PANDAS
# =========================================================

def get_dataframe():
    """
    Read the crime table into a Pandas DataFrame.
    """

    engine = create_engine(
        current_app.config[
            "SQLALCHEMY_DATABASE_URI"
        ]
    )

    query = """
        SELECT
            id,
            case_number,
            date,
            block,
            iucr,
            primary_type,
            description,
            location_desc,
            arrest,
            domestic,
            beat_num,
            district_name,
            ward_no,
            community_code,
            fbi_code,
            x_coordinate,
            y_coordinate,
            year,
            date_of_update,
            latitude,
            longitude,
            location
        FROM crime
    """

    try:

        with engine.connect() as connection:

            df = pd.read_sql(
                query,
                connection
            )

    finally:

        engine.dispose()

    if df.empty:
        return df

    # =====================================================
    # DATE CONVERSION
    # =====================================================

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    # =====================================================
    # ANALYSIS FEATURES
    # =====================================================

    df["month"] = (
        df["date"].dt.month
    )

    df["day_of_week"] = (
        df["date"].dt.day_name()
    )

    df["hour"] = (
        df["date"].dt.hour
    )

    # =====================================================
    # NORMALIZE BOOLEAN COLUMNS
    # =====================================================

    if "arrest" in df.columns:

        df["arrest"] = normalize_boolean(
            df["arrest"]
        )

    if "domestic" in df.columns:

        df["domestic"] = normalize_boolean(
            df["domestic"]
        )

    return df


# =========================================================
# CRIME COUNT PER YEAR
# =========================================================

def crimes_per_year(df):

    if df.empty:

        return pd.DataFrame(
            columns=[
                "year",
                "crime_count"
            ]
        )

    result = (
        df
        .dropna(subset=["year"])
        .groupby("year")
        .size()
        .reset_index(
            name="crime_count"
        )
        .sort_values("year")
    )

    result["year"] = (
        pd.to_numeric(
            result["year"],
            errors="coerce"
        )
        .astype("Int64")
    )

    return result


# =========================================================
# TOP CRIME TYPES
# =========================================================

def top_crimes(df, limit=10):

    if df.empty:

        return pd.DataFrame(
            columns=[
                "primary_type",
                "crime_count",
                "percentage"
            ]
        )

    if "primary_type" not in df.columns:

        return pd.DataFrame(
            columns=[
                "primary_type",
                "crime_count",
                "percentage"
            ]
        )

    crime_series = (
        df["primary_type"]
        .astype("string")
        .str.strip()
    )

    crime_series = crime_series[
        crime_series.notna()
        & (crime_series != "")
    ]

    if crime_series.empty:

        return pd.DataFrame(
            columns=[
                "primary_type",
                "crime_count",
                "percentage"
            ]
        )

    result = (
        crime_series
        .value_counts()
        .head(limit)
        .reset_index()
    )

    result.columns = [
        "primary_type",
        "crime_count"
    ]

    total_valid_crimes = (
        crime_series.shape[0]
    )

    result["percentage"] = (
        result["crime_count"]
        .div(total_valid_crimes)
        .mul(100)
        .round(2)
    )

    return result


# =========================================================
# OVERALL ARREST RATE
# =========================================================

def calculate_arrest_rate(df):

    if (
        df.empty
        or "arrest" not in df.columns
    ):
        return 0.0

    arrest_values = normalize_boolean(
        df["arrest"]
    )

    valid_values = arrest_values.dropna()

    if valid_values.empty:
        return 0.0

    return round(
        valid_values.astype(float).mean() * 100,
        2
    )


# =========================================================
# ARREST RATE BY YEAR
# =========================================================

def arrest_rate_by_year(df):

    if (
        df.empty
        or "arrest" not in df.columns
    ):

        return pd.DataFrame(
            columns=[
                "year",
                "arrest_rate"
            ]
        )

    temp = df.copy()

    temp["arrest"] = normalize_boolean(
        temp["arrest"]
    )

    temp = temp.dropna(
        subset=[
            "year",
            "arrest"
        ]
    )

    if temp.empty:

        return pd.DataFrame(
            columns=[
                "year",
                "arrest_rate"
            ]
        )

    result = (
        temp
        .groupby("year")["arrest"]
        .mean()
        .mul(100)
        .round(2)
        .reset_index()
    )

    result.columns = [
        "year",
        "arrest_rate"
    ]

    result = result.sort_values(
        "year"
    )

    return result


# =========================================================
# ARREST COUNT BY YEAR
# =========================================================

def arrest_count_by_year(df):

    if (
        df.empty
        or "arrest" not in df.columns
    ):

        return pd.DataFrame(
            columns=[
                "year",
                "arrest_count"
            ]
        )

    temp = df.copy()

    temp["arrest"] = normalize_boolean(
        temp["arrest"]
    )

    temp = temp[
        temp["arrest"] == True
    ]

    temp = temp.dropna(
        subset=["year"]
    )

    if temp.empty:

        return pd.DataFrame(
            columns=[
                "year",
                "arrest_count"
            ]
        )

    result = (
        temp
        .groupby("year")
        .size()
        .reset_index(
            name="arrest_count"
        )
        .sort_values("year")
    )

    return result


# =========================================================
# TOP COMMUNITY CODES
# =========================================================

def top_community_areas(df, limit=10):

    if (
        df.empty
        or "community_code" not in df.columns
    ):

        return pd.DataFrame(
            columns=[
                "community_code",
                "crime_count"
            ]
        )

    community = (
        df["community_code"]
        .astype("string")
        .str.strip()
    )

    community = community[
        community.notna()
        & (community != "")
    ]

    if community.empty:

        return pd.DataFrame(
            columns=[
                "community_code",
                "crime_count"
            ]
        )

    result = (
        community
        .value_counts()
        .head(limit)
        .reset_index()
    )

    result.columns = [
        "community_code",
        "crime_count"
    ]

    return result


# =========================================================
# TOP IUCR CODES
# =========================================================

def top_iucr_codes(df, limit=10):

    if (
        df.empty
        or "iucr" not in df.columns
    ):

        return pd.DataFrame(
            columns=[
                "iucr",
                "crime_count"
            ]
        )

    iucr = (
        df["iucr"]
        .astype("string")
        .str.strip()
    )

    iucr = iucr[
        iucr.notna()
        & (iucr != "")
    ]

    if iucr.empty:

        return pd.DataFrame(
            columns=[
                "iucr",
                "crime_count"
            ]
        )

    result = (
        iucr
        .value_counts()
        .head(limit)
        .reset_index()
    )

    result.columns = [
        "iucr",
        "crime_count"
    ]

    return result


# =========================================================
# TOP FBI CODES
# =========================================================

def top_fbi_codes(df, limit=10):

    if (
        df.empty
        or "fbi_code" not in df.columns
    ):

        return pd.DataFrame(
            columns=[
                "fbi_code",
                "crime_count"
            ]
        )

    fbi = (
        df["fbi_code"]
        .astype("string")
        .str.strip()
    )

    fbi = fbi[
        fbi.notna()
        & (fbi != "")
    ]

    if fbi.empty:

        return pd.DataFrame(
            columns=[
                "fbi_code",
                "crime_count"
            ]
        )

    result = (
        fbi
        .value_counts()
        .head(limit)
        .reset_index()
    )

    result.columns = [
        "fbi_code",
        "crime_count"
    ]

    return result


# =========================================================
# TOP CRIME LOCATIONS
# =========================================================

def top_locations(df, limit=10):

    if (
        df.empty
        or "location_desc" not in df.columns
    ):

        return pd.DataFrame(
            columns=[
                "location_desc",
                "crime_count"
            ]
        )

    locations = (
        df["location_desc"]
        .astype("string")
        .str.strip()
    )

    locations = locations[
        locations.notna()
        & (locations != "")
    ]

    if locations.empty:

        return pd.DataFrame(
            columns=[
                "location_desc",
                "crime_count"
            ]
        )

    result = (
        locations
        .value_counts()
        .head(limit)
        .reset_index()
    )

    result.columns = [
        "location_desc",
        "crime_count"
    ]

    return result


# =========================================================
# CRIME BY MONTH
# =========================================================

def crimes_by_month(df):

    if (
        df.empty
        or "month" not in df.columns
    ):

        return pd.DataFrame(
            columns=[
                "month",
                "crime_count"
            ]
        )

    result = (
        df
        .dropna(subset=["month"])
        .groupby("month")
        .size()
        .reset_index(
            name="crime_count"
        )
        .sort_values("month")
    )

    return result


# =========================================================
# CRIME BY HOUR
# =========================================================

def crimes_by_hour(df):

    if (
        df.empty
        or "hour" not in df.columns
    ):

        return pd.DataFrame(
            columns=[
                "hour",
                "crime_count"
            ]
        )

    result = (
        df
        .dropna(subset=["hour"])
        .groupby("hour")
        .size()
        .reset_index(
            name="crime_count"
        )
        .sort_values("hour")
    )

    return result


# =========================================================
# MONTH × DAY HEATMAP
# =========================================================

def month_day_heatmap_data(df):

    order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    if (
        df.empty
        or "month" not in df.columns
        or "day_of_week" not in df.columns
    ):

        return pd.DataFrame()

    valid_df = df.dropna(
        subset=[
            "month",
            "day_of_week"
        ]
    )

    if valid_df.empty:
        return pd.DataFrame()

    pivot = pd.crosstab(
        valid_df["month"],
        valid_df["day_of_week"]
    )

    pivot = pivot.reindex(
        index=range(1, 13),
        fill_value=0
    )

    pivot = pivot.reindex(
        columns=order,
        fill_value=0
    )

    return pivot


# =========================================================
# COMMUNITY CODE IQR ANALYSIS
# =========================================================

def community_area_iqr(df):

    if (
        df.empty
        or "community_code" not in df.columns
    ):

        return pd.DataFrame(
            columns=[
                "community_code",
                "crime_count",
                "Q1",
                "Q3",
                "IQR",
                "lower_bound",
                "upper_bound"
            ]
        )

    community = (
        df["community_code"]
        .astype("string")
        .str.strip()
    )

    community = community[
        community.notna()
        & (community != "")
    ]

    if community.empty:

        return pd.DataFrame(
            columns=[
                "community_code",
                "crime_count",
                "Q1",
                "Q3",
                "IQR",
                "lower_bound",
                "upper_bound"
            ]
        )

    counts = community.value_counts()

    values = counts.values

    q1 = np.percentile(
        values,
        25
    )

    q3 = np.percentile(
        values,
        75
    )

    iqr = q3 - q1

    lower_bound = (
        q1 - 1.5 * iqr
    )

    upper_bound = (
        q3 + 1.5 * iqr
    )

    outliers = counts[
        (counts < lower_bound)
        |
        (counts > upper_bound)
    ]

    if outliers.empty:

        return pd.DataFrame(
            columns=[
                "community_code",
                "crime_count",
                "Q1",
                "Q3",
                "IQR",
                "lower_bound",
                "upper_bound"
            ]
        )

    result = (
        outliers
        .reset_index()
    )

    result.columns = [
        "community_code",
        "crime_count"
    ]

    result["Q1"] = q1
    result["Q3"] = q3
    result["IQR"] = iqr
    result["lower_bound"] = lower_bound
    result["upper_bound"] = upper_bound

    return result


# =========================================================
# CORRELATION MATRIX
# =========================================================

def correlation_matrix(df):

    numeric_columns = [
        "year",
        "month",
        "hour",
        "arrest",
        "domestic",
        "x_coordinate",
        "y_coordinate",
        "latitude",
        "longitude"
    ]

    numeric_columns = [
        column
        for column in numeric_columns
        if column in df.columns
    ]

    if not numeric_columns:

        return pd.DataFrame()

    numeric_df = df[
        numeric_columns
    ].copy()

    for column in [
        "arrest",
        "domestic"
    ]:

        if column in numeric_df.columns:

            numeric_df[column] = (
                normalize_boolean(
                    numeric_df[column]
                )
                .astype(float)
            )

    numeric_df = (
        numeric_df
        .apply(
            pd.to_numeric,
            errors="coerce"
        )
    )

    return numeric_df.corr()


# =========================================================
# GENERATE ALL CHARTS AND REPORTS
# =========================================================

def generate_charts(df):
    """
    Generate charts and CSV reports from the crime DataFrame.
    """

    chart_folder = Path(
        current_app.config[
            "CHART_FOLDER"
        ]
    )

    report_folder = Path(
        current_app.config[
            "REPORT_FOLDER"
        ]
    )

    # -----------------------------------------------------
    # Make sure directories exist
    # -----------------------------------------------------

    chart_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    report_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    print(
        f"\nChart folder: {chart_folder.resolve()}"
    )

    print(
        f"Report folder: {report_folder.resolve()}"
    )

    if df.empty:

        print(
            "No crime data available. "
            "Charts were not generated."
        )

        return

    # -----------------------------------------------------
    # Matplotlib / Seaborn configuration
    # -----------------------------------------------------

    sns.set_theme(
        style="whitegrid"
    )

    # =====================================================
    # 1. CRIME TREND BY YEAR
    # =====================================================

    yearly = crimes_per_year(df)

    yearly.to_csv(
        report_folder / "crime_count_per_year.csv",
        index=False
    )

    if not yearly.empty:

        fig, ax = plt.subplots(
            figsize=CHART_SIZE
        )

        ax.plot(
            yearly["year"],
            yearly["crime_count"],
            marker="o",
            linewidth=2
        )

        ax.set_title(
            "Crime Count by Year",
            fontsize=15,
            fontweight="bold"
        )

        ax.set_xlabel(
            "Year"
        )

        ax.set_ylabel(
            "Number of Crimes"
        )

        ax.set_xticks(
            yearly["year"]
        )

        save_chart(
            fig,
            chart_folder / "crime_by_year.png"
        )

    # =====================================================
    # 2. TOP CRIME CATEGORIES
    # =====================================================

    crime_types = top_crimes(
        df,
        10
    )

    crime_types.to_csv(
        report_folder / "top_10_crime_types.csv",
        index=False
    )

    if not crime_types.empty:

        plot_data = (
            crime_types
            .sort_values(
                "crime_count"
            )
        )

        fig, ax = plt.subplots(
            figsize=CHART_SIZE
        )

        ax.barh(
            plot_data["primary_type"],
            plot_data["crime_count"]
        )

        ax.set_title(
            "Top 10 Crime Categories",
            fontsize=15,
            fontweight="bold"
        )

        ax.set_xlabel(
            "Number of Crimes"
        )

        ax.set_ylabel(
            "Crime Category"
        )

        save_chart(
            fig,
            chart_folder / "top_crime_categories.png"
        )

    # =====================================================
    # 3. ARREST RATE BY YEAR
    # =====================================================

    arrest_yearly = arrest_rate_by_year(
        df
    )

    arrest_yearly.to_csv(
        report_folder / "arrest_rate_by_year.csv",
        index=False
    )

    if not arrest_yearly.empty:

        fig, ax = plt.subplots(
            figsize=CHART_SIZE
        )

        ax.plot(
            arrest_yearly["year"],
            arrest_yearly["arrest_rate"],
            marker="o",
            linewidth=2
        )

        ax.set_title(
            "Arrest Rate by Year",
            fontsize=15,
            fontweight="bold"
        )

        ax.set_xlabel(
            "Year"
        )

        ax.set_ylabel(
            "Arrest Rate (%)"
        )

        ax.set_xticks(
            arrest_yearly["year"]
        )

        save_chart(
            fig,
            chart_folder / "arrest_rate_by_year.png"
        )

    # =====================================================
    # 4. MONTH × DAY HEATMAP
    # =====================================================

    heatmap_data = (
        month_day_heatmap_data(df)
    )

    if not heatmap_data.empty:

        fig, ax = plt.subplots(
            figsize=CHART_SIZE
        )

        sns.heatmap(
            heatmap_data,
            annot=True,
            fmt="g",
            cmap="YlOrRd",
            ax=ax,
            cbar=True
        )

        ax.set_title(
            "Crime Frequency by Month and Day",
            fontsize=15,
            fontweight="bold"
        )

        ax.set_xlabel(
            "Day of Week"
        )

        ax.set_ylabel(
            "Month"
        )

        save_chart(
            fig,
            chart_folder / "month_day_heatmap.png"
        )

    # =====================================================
    # 5. TOP COMMUNITY CODES
    # =====================================================

    communities = top_community_areas(
        df,
        10
    )

    communities.to_csv(
        report_folder / "top_10_community_areas.csv",
        index=False
    )

    if not communities.empty:

        plot_data = (
            communities
            .sort_values(
                "crime_count"
            )
        )

        fig, ax = plt.subplots(
            figsize=CHART_SIZE
        )

        ax.barh(
            plot_data["community_code"].astype(str),
            plot_data["crime_count"]
        )

        ax.set_title(
            "Top 10 Community Areas",
            fontsize=15,
            fontweight="bold"
        )

        ax.set_xlabel(
            "Number of Crimes"
        )

        ax.set_ylabel(
            "Community Code"
        )

        save_chart(
            fig,
            chart_folder / "top_community_areas.png"
        )

    # =====================================================
    # 6. CRIME BY HOUR
    # =====================================================

    hourly = crimes_by_hour(
        df
    )

    hourly.to_csv(
        report_folder / "crime_by_hour.csv",
        index=False
    )

    if not hourly.empty:

        fig, ax = plt.subplots(
            figsize=CHART_SIZE
        )

        ax.plot(
            hourly["hour"],
            hourly["crime_count"],
            marker="o",
            linewidth=2
        )

        ax.set_title(
            "Crime Distribution by Hour",
            fontsize=15,
            fontweight="bold"
        )

        ax.set_xlabel(
            "Hour of Day"
        )

        ax.set_ylabel(
            "Number of Crimes"
        )

        ax.set_xticks(
            range(24)
        )

        save_chart(
            fig,
            chart_folder / "crime_by_hour.png"
        )

    # =====================================================
    # 7. COMMUNITY CODE BOX PLOT
    # =====================================================

    if "community_code" in df.columns:

        community = (
            df["community_code"]
            .astype("string")
            .str.strip()
        )

        community = community[
            community.notna()
            & (community != "")
        ]

        community_counts = (
            community.value_counts()
        )

        if not community_counts.empty:

            fig, ax = plt.subplots(
                figsize=CHART_SIZE
            )

            ax.boxplot(
                community_counts.values
            )

            ax.set_title(
                "Community Area Crime Counts - Box Plot",
                fontsize=15,
                fontweight="bold"
            )

            ax.set_ylabel(
                "Crime Count"
            )

            save_chart(
                fig,
                chart_folder / "community_area_boxplot.png"
            )

    # =====================================================
    # 8. CORRELATION HEATMAP
    # =====================================================

    correlation = correlation_matrix(
        df
    )

    correlation.to_csv(
        report_folder / "correlation_matrix.csv"
    )

    if not correlation.empty:

        fig, ax = plt.subplots(
            figsize=CHART_SIZE
        )

        sns.heatmap(
            correlation,
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            center=0,
            ax=ax,
            cbar=True
        )

        ax.set_title(
            "Crime Data Correlation Matrix",
            fontsize=15,
            fontweight="bold"
        )

        save_chart(
            fig,
            chart_folder / "correlation_heatmap.png"
        )

    # =====================================================
    # 9. TOP IUCR CODES
    # =====================================================

    top_iucr = top_iucr_codes(
        df,
        10
    )

    top_iucr.to_csv(
        report_folder / "top_iucr_codes.csv",
        index=False
    )

    # =====================================================
    # 10. TOP FBI CODES
    # =====================================================

    top_fbi = top_fbi_codes(
        df,
        10
    )

    top_fbi.to_csv(
        report_folder / "top_fbi_codes.csv",
        index=False
    )

    # =====================================================
    # 11. TOP CRIME LOCATIONS
    # =====================================================

    locations = top_locations(
        df,
        10
    )

    locations.to_csv(
        report_folder / "top_crime_locations.csv",
        index=False
    )

    # =====================================================
    # 12. COMMUNITY IQR OUTLIERS
    # =====================================================

    outliers = community_area_iqr(
        df
    )

    outliers.to_csv(
        report_folder / "community_area_outliers.csv",
        index=False
    )

    # =====================================================
    # 13. ARREST COUNT BY YEAR
    # =====================================================

    arrest_counts = arrest_count_by_year(
        df
    )

    arrest_counts.to_csv(
        report_folder / "arrest_count_by_year.csv",
        index=False
    )

    if not arrest_counts.empty:

        fig, ax = plt.subplots(
            figsize=CHART_SIZE
        )

        sns.barplot(
            data=arrest_counts,
            x="year",
            y="arrest_count",
            ax=ax
        )

        ax.set_title(
            "Arrest Count by Year",
            fontsize=15,
            fontweight="bold"
        )

        ax.set_xlabel(
            "Year"
        )

        ax.set_ylabel(
            "Number of Arrests"
        )

        ax.tick_params(
            axis="x",
            rotation=0
        )

        save_chart(
            fig,
            chart_folder / "arrest_count_by_year.png"
        )

    # =====================================================
    # VERIFY GENERATED CHARTS
    # =====================================================

    expected_charts = [
        "crime_by_year.png",
        "top_crime_categories.png",
        "arrest_rate_by_year.png",
        "month_day_heatmap.png",
        "top_community_areas.png",
        "crime_by_hour.png",
        "community_area_boxplot.png",
        "correlation_heatmap.png"
    ]

    print(
        "\n========================================"
    )

    print(
        "CHART GENERATION SUMMARY"
    )

    print(
        "========================================"
    )

    for chart_name in expected_charts:

        chart_path = (
            chart_folder / chart_name
        )

        if chart_path.exists():

            print(
                f"[OK] {chart_name}"
            )

        else:

            print(
                f"[MISSING] {chart_name}"
            )

    print(
        "\nCharts saved to:"
    )

    print(
        chart_folder.resolve()
    )

    print(
        "\nReports saved to:"
    )

    print(
        report_folder.resolve()
    )

    print(
        "\nAnalysis completed successfully."
    )

    print(
        "========================================\n"
    )
