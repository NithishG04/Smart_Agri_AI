-- Smart Agri AI — MySQL Database Schema
-- Database: smart_agri

CREATE DATABASE IF NOT EXISTS smart_agri
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE smart_agri;

-- 1. Farmers table
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Soil test & crop recommendation history
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
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    INDEX idx_soil_test_farmer_date (farmer_id, date),
    INDEX idx_soil_test_recommendation (recommendation)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Plant disease detection history
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
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    INDEX idx_disease_farmer_date (farmer_id, date),
    INDEX idx_disease_crop_type (crop_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Market crop prices
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Weather data (historical & synced snapshots)
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
