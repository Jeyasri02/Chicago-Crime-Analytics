from sqlalchemy import text

from extensions import db


# =========================================================
# CREATE SUMMARY TABLES
# =========================================================

def create_summary_tables():
    """
    Create summary tables used for dashboard/reporting.

    These tables are separate from the main 'crime' table
    defined in models.py.
    """

    # -----------------------------------------------------
    # Yearly crime summary
    # -----------------------------------------------------

    db.session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS crime_yearly_summary (
                year INTEGER PRIMARY KEY,
                crime_count INTEGER NOT NULL
            )
            """
        )
    )

    # -----------------------------------------------------
    # Crime category summary
    # -----------------------------------------------------

    db.session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS crime_category_summary (
                primary_type TEXT PRIMARY KEY,
                crime_count INTEGER NOT NULL,
                percentage REAL
            )
            """
        )
    )

    # -----------------------------------------------------
    # Arrest yearly summary
    # -----------------------------------------------------

    db.session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS arrest_yearly_summary (
                year INTEGER PRIMARY KEY,
                arrest_count INTEGER NOT NULL,
                total_crimes INTEGER NOT NULL,
                arrest_rate REAL
            )
            """
        )
    )

    db.session.commit()


# =========================================================
# POPULATE SUMMARY TABLES
# =========================================================

def populate_summary_tables():
    """
    Populate all summary tables using data from the
    main 'crime' table.
    """

    create_summary_tables()

    # -----------------------------------------------------
    # Clear existing summary data
    # -----------------------------------------------------

    db.session.execute(
        text("DELETE FROM crime_yearly_summary")
    )

    db.session.execute(
        text("DELETE FROM crime_category_summary")
    )

    db.session.execute(
        text("DELETE FROM arrest_yearly_summary")
    )

    # =====================================================
    # 1. CRIME COUNT PER YEAR
    # =====================================================

    db.session.execute(
        text(
            """
            INSERT INTO crime_yearly_summary (
                year,
                crime_count
            )
            SELECT
                year,
                COUNT(*) AS crime_count
            FROM crime
            WHERE year IS NOT NULL
            GROUP BY year
            """
        )
    )

    # =====================================================
    # 2. CRIME CATEGORY SUMMARY
    # =====================================================

    db.session.execute(
        text(
            """
            INSERT INTO crime_category_summary (
                primary_type,
                crime_count,
                percentage
            )
            SELECT
                primary_type,
                COUNT(*) AS crime_count,
                ROUND(
                    COUNT(*) * 100.0 /
                    NULLIF(
                        (
                            SELECT COUNT(*)
                            FROM crime
                            WHERE primary_type IS NOT NULL
                        ),
                        0
                    ),
                    2
                ) AS percentage
            FROM crime
            WHERE primary_type IS NOT NULL
            GROUP BY primary_type
            """
        
        )
    )

    # =====================================================
    # 3. ARREST SUMMARY PER YEAR
    # =====================================================

    db.session.execute(
        text(
            """
            INSERT INTO arrest_yearly_summary (
                year,
                arrest_count,
                total_crimes,
                arrest_rate
            )
            SELECT
                year,

                SUM(
                    CASE
                        WHEN arrest = 1 THEN 1
                        ELSE 0
                    END
                ) AS arrest_count,

                COUNT(*) AS total_crimes,

                ROUND(
                    SUM(
                        CASE
                            WHEN arrest = 1 THEN 1
                            ELSE 0
                        END
                    ) * 100.0 /
                    NULLIF(COUNT(*), 0),
                    2
                ) AS arrest_rate

            FROM crime

            WHERE year IS NOT NULL

            GROUP BY year
            """
        )
    )

    db.session.commit()


# =========================================================
# CREATE DATABASE VIEWS
# =========================================================

def create_views():
    """
    Create SQLite views for frequently used analysis queries.
    """

    # -----------------------------------------------------
    # Remove existing views
    # -----------------------------------------------------

    db.session.execute(
        text(
            "DROP VIEW IF EXISTS vw_crime_yearly"
        )
    )

    db.session.execute(
        text(
            "DROP VIEW IF EXISTS vw_crime_by_category"
        )
    )

    # =====================================================
    # VIEW 1: YEARLY CRIME
    # =====================================================

    db.session.execute(
        text(
            """
            CREATE VIEW vw_crime_yearly AS
            SELECT
                year,
                COUNT(*) AS crime_count
            FROM crime
            WHERE year IS NOT NULL
            GROUP BY year
            """
        )
    )

    # =====================================================
    # VIEW 2: CRIME BY CATEGORY
    # =====================================================

    db.session.execute(
        text(
            """
            CREATE VIEW vw_crime_by_category AS
            SELECT
                primary_type,
                COUNT(*) AS crime_count,

                ROUND(
                    COUNT(*) * 100.0 /
                    NULLIF(
                        (
                            SELECT COUNT(*)
                            FROM crime
                            WHERE primary_type IS NOT NULL
                        ),
                        0
                    ),
                    2
                ) AS percentage

            FROM crime

            WHERE primary_type IS NOT NULL

            GROUP BY primary_type
            """
        )
    )

    db.session.commit()


# =========================================================
# BUILD DATABASE REPORTING
# =========================================================

def build_database_reporting():
    """
    Build all summary tables and database views.
    """

    populate_summary_tables()

    create_views()
