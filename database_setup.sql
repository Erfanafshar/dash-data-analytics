-- PostgreSQL Database Setup for Cloud-Powered Data Dashboard

-- 1️ Create Database
CREATE DATABASE my_dash_db;

-- 2️ Create User and Set Password
CREATE USER myuser WITH ENCRYPTED PASSWORD 'mypassword';

-- 3️ Grant Privileges to the User
GRANT ALL PRIVILEGES ON DATABASE my_dash_db TO myuser;

-- 4️ Connect to the Database (Run this manually in psql)
-- \c my_dash_db

-- 5️ Create Table for Storing Sensor Data
CREATE TABLE public.sensor_data (
    id SERIAL PRIMARY KEY,         -- Auto-incrementing ID
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Auto-filled time
    value INTEGER                   -- Sensor value
);

-- 6️ Verify Table Creation (Optional, Run in Query Tool)
SELECT * FROM public.sensor_data;

-- 7️ Insert Sample Data (Optional)
INSERT INTO public.sensor_data (value) VALUES (10), (20), (30), (40), (50);

-- PostgreSQL setup completed! Now your Python app can connect to this database.
