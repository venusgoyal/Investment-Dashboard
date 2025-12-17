-- MySQL Schema for Investment Dashboard
-- Run this script to create the database and tables

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS investment_db;

-- Use the database
USE investment_db;

-- Create investment table
CREATE TABLE IF NOT EXISTS investment (
    investment_id VARCHAR(36) PRIMARY KEY,
    investment_amount DECIMAL(15, 2) NOT NULL,
    investment_date DATE NOT NULL,
    annual_return_percentage DECIMAL(5, 2) NOT NULL,
    investment_comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_investment_date (investment_date),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add comments column if it doesn't exist (for existing tables)
ALTER TABLE investment ADD COLUMN IF NOT EXISTS investment_comments TEXT;

-- Display table structure
DESCRIBE investment;

-- Display permissions
SELECT user, host FROM mysql.user WHERE user = 'root';

-- Sample verification query
SELECT 'Investment table created successfully!' as status;

-- Remote DB table schema for reference
-- CREATE TABLE `investment` (
--   `investment_id` varchar(36) NOT NULL,
--   `investment_amount` decimal(15,2) NOT NULL,
--   `investment_date` date NOT NULL,
--   `annual_return_percentage` decimal(5,2) NOT NULL,
--   `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
--   `updated_at` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
--   `investment_comments` text,
--   PRIMARY KEY (`investment_id`),
--   KEY `idx_investment_date` (`investment_date`)
-- ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
