-- Updated MySQL database setup for Student Fingerprint Reader
-- Run this script in your MySQL database to create the required table

CREATE DATABASE IF NOT EXISTS college_db;
USE college_db;

-- Create students table with fingerprint support
CREATE TABLE IF NOT EXISTS students (
    student_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    department VARCHAR(50),
    year_of_study INT,
    enrollment_date DATE,
    status ENUM('active', 'inactive', 'graduated') DEFAULT 'active',
    fingerprint_template LONGTEXT,  -- Store base64 encoded fingerprint template
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO students (student_id, first_name, last_name, email, phone, department, year_of_study, enrollment_date, status) VALUES
('STU001', 'John', 'Doe', 'john.doe@college.edu', '1234567890', 'Computer Science', 3, '2022-09-01', 'active'),
('STU002', 'Jane', 'Smith', 'jane.smith@college.edu', '1234567891', 'Mathematics', 2, '2023-09-01', 'active'),
('STU003', 'Mike', 'Johnson', 'mike.johnson@college.edu', '1234567892', 'Physics', 4, '2021-09-01', 'active'),
('STU004', 'Sarah', 'Wilson', 'sarah.wilson@college.edu', '1234567893', 'Chemistry', 1, '2024-09-01', 'active'),
('STU005', 'David', 'Brown', 'david.brown@college.edu', '1234567894', 'Biology', 3, '2022-09-01', 'inactive');

-- Create indexes for better performance
CREATE INDEX idx_student_email ON students(email);
CREATE INDEX idx_student_department ON students(department);
CREATE INDEX idx_student_status ON students(status);
CREATE INDEX idx_fingerprint_template ON students(fingerprint_template(100));  -- Index for fingerprint searches
