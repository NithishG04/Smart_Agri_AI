"""
Smart Agri AI — MySQL Database Layer
Handles connection pooling, automatic schema creation, safe non-destructive seeding,
and parameterized query helpers.
"""

import csv
import os
from contextlib import contextmanager
from datetime import date, timedelta
import mysql.connector
from mysql.connector import Error as MySQLError, pooling
from config import Config


class DatabaseUnavailableError(RuntimeError):
    """Raised when MySQL cannot be reached or initialized."""


_pool = None


def _base_db_params(include_database: bool = True) -> dict:
    params = {
        "host": Config.MYSQL_HOST,
        "port": Config.MYSQL_PORT,
        "user": Config.MYSQL_USER,
        "password": Config.MYSQL_PASSWORD,
        "charset": "utf8mb4",
        "use_unicode": True,
        "autocommit": False,
    }
    if include_database:
        params["database"] = Config.MYSQL_DATABASE
    return params


def get_pool():
    """Lazily initialize and return the MySQL connection pool."""
    global _pool
    if _pool is None:
        try:
            _pool = pooling.MySQLConnectionPool(
                pool_name="smart_agri_pool",
                pool_size=8,
                pool_reset_session=True,
                **_base_db_params(include_database=True),
            )
        except MySQLError as exc:
            raise DatabaseUnavailableError(
                f"Unable to connect to MySQL database '{Config.MYSQL_DATABASE}': {exc}"
            ) from exc
    return _pool


@contextmanager
def get_db_connection():
    """Yield a pooled MySQL connection with automatic commit/rollback."""
    try:
        conn = get_pool().get_connection()
    except MySQLError as exc:
        raise DatabaseUnavailableError(
            f"Database connection error: {exc}"
        ) from exc

    try:
        yield conn
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        try:
            conn.close()
        except Exception:
            pass


def query_all(sql: str, params: tuple = ()) -> list:
    """Execute a SELECT query and return all rows as dictionaries."""
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, params)
            return cursor.fetchall()
        finally:
            cursor.close()


def query_one(sql: str, params: tuple = ()):
    """Execute a SELECT query and return a single row dict or None."""
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, params)
            return cursor.fetchone()
        finally:
            cursor.close()


def execute_write(sql: str, params: tuple = ()) -> int:
    """Execute an INSERT/UPDATE/DELETE statement inside a transaction and return lastrowid."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()


def _create_database_and_tables():
    """Create the smart_agri database and required tables if they do not exist."""
    conn = mysql.connector.connect(**_base_db_params(include_database=False))
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{Config.MYSQL_DATABASE}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        cursor.execute(f"USE `{Config.MYSQL_DATABASE}`")

        table_statements = [
            """
            CREATE TABLE IF NOT EXISTS farmers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(120) NOT NULL,
                email VARCHAR(160) NOT NULL,
                phone VARCHAR(24) NOT NULL,
                farm_location VARCHAR(100) NOT NULL,
                farm_size DECIMAL(10, 2) NOT NULL DEFAULT 1.00,
                soil_type VARCHAR(80) NOT NULL DEFAULT 'Alluvial Soil',
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uq_farmers_email (email),
                UNIQUE KEY uq_farmers_phone (phone),
                INDEX idx_farmers_location (farm_location)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            """
            CREATE TABLE IF NOT EXISTS soil_test (
                id INT AUTO_INCREMENT PRIMARY KEY,
                farmer_id INT NOT NULL,
                nitrogen DECIMAL(8, 2) NOT NULL,
                phosphorus DECIMAL(8, 2) NOT NULL,
                potassium DECIMAL(8, 2) NOT NULL,
                ph DECIMAL(4, 2) NOT NULL DEFAULT 6.50,
                district VARCHAR(100) NOT NULL DEFAULT '',
                temperature DECIMAL(6, 2) NULL,
                humidity DECIMAL(6, 2) NULL,
                rainfall DECIMAL(8, 2) NULL,
                confidence DECIMAL(5, 2) NULL,
                recommendation VARCHAR(120) NOT NULL,
                date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_soil_test_farmer
                    FOREIGN KEY (farmer_id) REFERENCES farmers(id)
                    ON DELETE CASCADE ON UPDATE CASCADE,
                INDEX idx_soil_test_farmer_date (farmer_id, date),
                INDEX idx_soil_test_recommendation (recommendation)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            """
            CREATE TABLE IF NOT EXISTS disease_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                farmer_id INT NOT NULL,
                crop_type VARCHAR(120) NOT NULL,
                disease_name VARCHAR(160) NOT NULL,
                confidence DECIMAL(5, 2) NOT NULL,
                severity VARCHAR(24) NOT NULL DEFAULT 'medium',
                image_path VARCHAR(255) NOT NULL,
                treatment TEXT NULL,
                date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_disease_history_farmer
                    FOREIGN KEY (farmer_id) REFERENCES farmers(id)
                    ON DELETE CASCADE ON UPDATE CASCADE,
                INDEX idx_disease_farmer_date (farmer_id, date),
                INDEX idx_disease_crop_type (crop_type)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            """
            CREATE TABLE IF NOT EXISTS crop_prices (
                id INT AUTO_INCREMENT PRIMARY KEY,
                crop_name VARCHAR(100) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                previous_price DECIMAL(10, 2) NULL,
                district VARCHAR(100) NOT NULL,
                date_recorded DATE NOT NULL,
                UNIQUE KEY uq_crop_district_date (crop_name, district, date_recorded),
                INDEX idx_crop_prices_district (district),
                INDEX idx_crop_prices_crop (crop_name),
                INDEX idx_crop_prices_date (date_recorded)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            """
            CREATE TABLE IF NOT EXISTS weather_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                district VARCHAR(100) NOT NULL,
                temperature DECIMAL(6, 2) NOT NULL,
                humidity DECIMAL(6, 2) NOT NULL,
                rainfall DECIMAL(8, 2) NOT NULL DEFAULT 0.00,
                wind_speed DECIMAL(6, 2) NOT NULL DEFAULT 0.00,
                condition_name VARCHAR(80) NOT NULL DEFAULT 'Clear',
                source VARCHAR(40) NOT NULL DEFAULT 'historical',
                date DATE NOT NULL,
                UNIQUE KEY uq_weather_district_date_source (district, date, source),
                INDEX idx_weather_district_date (district, date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
        ]

        for stmt in table_statements:
            cursor.execute(stmt)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def _seed_crop_prices_if_empty():
    """
    Seed crop_prices with the latest prices per (crop, district) from market_data.csv
    ONLY if crop_prices currently has zero rows. Never deletes existing rows.
    """
    row = query_one("SELECT COUNT(*) AS cnt FROM crop_prices")
    if row and row["cnt"] > 0:
        return

    csv_path = Config.MARKET_CSV_PATH
    if not os.path.exists(csv_path):
        return

    # Track latest 2 dates per (crop, district) to compute real price movement
    latest_map = {}
    with open(csv_path, "r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for item in reader:
            crop = (item.get("crop") or "").strip()
            district = (item.get("district") or "").strip()
            dt = (item.get("date") or "").strip()
            price_str = item.get("price")
            if not crop or not district or not dt or not price_str:
                continue
            try:
                price_val = round(float(price_str), 2)
            except ValueError:
                continue

            key = (crop, district)
            history = latest_map.setdefault(key, [])
            history.append((dt, price_val))
            if len(history) > 4:
                history.sort(key=lambda x: x[0], reverse=True)
                latest_map[key] = history[:2]

    records_to_insert = []
    for (crop, district), entries in latest_map.items():
        entries.sort(key=lambda x: x[0], reverse=True)
        latest_date, latest_price = entries[0]
        prev_price = entries[1][1] if len(entries) > 1 else latest_price
        records_to_insert.append((crop, latest_price, prev_price, district, latest_date))

    if not records_to_insert:
        return

    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.executemany(
                """
                INSERT IGNORE INTO crop_prices
                    (crop_name, price, previous_price, district, date_recorded)
                VALUES (%s, %s, %s, %s, %s)
                """,
                records_to_insert,
            )
            conn.commit()
        finally:
            cursor.close()


def _seed_historical_weather_if_empty():
    """
    Seed baseline historical Tamil Nadu weather records ONLY if weather_data is empty.
    Clearly tagged with source='historical' to distinguish from live Open-Meteo data.
    """
    row = query_one("SELECT COUNT(*) AS cnt FROM weather_data")
    if row and row["cnt"] > 0:
        return

    yesterday = (date.today() - timedelta(days=1)).isoformat()
    historical_rows = [
        ("Thanjavur", 33.4, 76.0, 2.4, 16.5, "Partly Cloudy", "historical", yesterday),
        ("Coimbatore", 30.2, 64.0, 0.0, 18.2, "Clear Sky", "historical", yesterday),
        ("Madurai", 34.8, 58.0, 0.5, 14.0, "Mostly Sunny", "historical", yesterday),
        ("Salem", 32.1, 66.0, 1.2, 13.4, "Partly Cloudy", "historical", yesterday),
        ("Trichy", 34.5, 70.0, 0.8, 17.1, "Partly Cloudy", "historical", yesterday),
        ("Vellore", 32.8, 61.0, 0.0, 15.6, "Clear Sky", "historical", yesterday),
        ("Tirunelveli", 31.6, 74.0, 4.2, 19.0, "Light Rain", "historical", yesterday),
        ("Erode", 30.9, 68.0, 1.8, 12.5, "Overcast", "historical", yesterday),
        ("Dindigul", 29.8, 67.0, 2.0, 14.8, "Partly Cloudy", "historical", yesterday),
        ("Chennai", 33.0, 79.0, 3.1, 21.4, "Partly Cloudy", "historical", yesterday),
        ("Cuddalore", 32.6, 80.0, 4.5, 20.1, "Light Rain", "historical", yesterday),
        ("Kancheepuram", 33.2, 75.0, 1.0, 16.0, "Mostly Sunny", "historical", yesterday),
        ("Karur", 33.9, 60.0, 0.0, 15.2, "Clear Sky", "historical", yesterday),
        ("Krishnagiri", 28.7, 69.0, 1.5, 13.8, "Partly Cloudy", "historical", yesterday),
        ("Virudhunagar", 34.1, 59.0, 0.2, 16.2, "Mostly Sunny", "historical", yesterday),
    ]

    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.executemany(
                """
                INSERT IGNORE INTO weather_data
                    (district, temperature, humidity, rainfall, wind_speed, condition_name, source, date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                historical_rows,
            )
            conn.commit()
        finally:
            cursor.close()


def init_db() -> bool:
    """
    Initialize MySQL database, schema, and baseline datasets if empty.
    Returns True on success, False if MySQL is unavailable (logged cleanly).
    """
    try:
        _create_database_and_tables()
        _seed_crop_prices_if_empty()
        _seed_historical_weather_if_empty()
        return True
    except Exception as exc:
        print(f"⚠️  Database initialization failed: {exc}")
        return False
