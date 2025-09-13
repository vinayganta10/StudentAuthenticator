# Student Fingerprint Reader Application

A Python application that scans student fingerprints and fetches their details from a MySQL database.

## Features

-  Real-time fingerprint scanning using camera
-  MySQL database integration with fingerprint template storage
-  Student details retrieval and identification
-  User-friendly interface with enrollment support
-  Advanced fingerprint matching algorithms
-  Secure fingerprint template storage

## Prerequisites

- Python 3.7 or higher
- MySQL database server
- Webcam or camera device
- Windows/Linux/macOS

## Installation

1. Install Python dependencies:
`ash
pip install -r requirements.txt
`

2. Set up MySQL database:
   - Run the database_setup.sql script in your MySQL database
   - Update database configuration in config.py

3. Configure database settings:
   - Open config.py
   - Update the configuration with your MySQL credentials:
   `python
   HOST = "localhost"
   USER = "your_username"
   PASSWORD = "your_password"
   DATABASE = "college_db"
   PORT = 3306
   CHARSET = "utf8mb4"
   `

## Usage

1. Run the application:
`ash
python Reader.py
`

2. Choose from the menu options:
   - **Option 1**: Scan fingerprint to identify student
   - **Option 2**: Enroll new fingerprint for existing student
   - **Option 3**: Quit application

3. For fingerprint scanning:
   - Place your finger on the camera lens
   - Press 'c' to capture the fingerprint
   - Press 'q' to quit scanning

## Database Schema

The application uses a students table with fingerprint support:

`sql
CREATE TABLE students (
    student_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    department VARCHAR(50),
    year_of_study INT,
    enrollment_date DATE,
    status ENUM('active', 'inactive', 'graduated') DEFAULT 'active',
    fingerprint_template LONGTEXT,  -- Base64 encoded fingerprint template
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
`

## Fingerprint Processing

The application uses computer vision techniques to:

1. **Capture**: Uses camera to capture fingerprint image
2. **Process**: Applies Gaussian blur and thresholding for noise reduction
3. **Extract**: Identifies contours and extracts geometric features
4. **Template**: Creates a unique template with area, perimeter, and circularity data
5. **Store**: Encodes template as base64 for database storage
6. **Match**: Compares input templates against stored templates using similarity algorithms

## Sample Data

The database_setup.sql file includes sample student data:
- STU001: John Doe (Computer Science)
- STU002: Jane Smith (Mathematics)
- STU003: Mike Johnson (Physics)
- STU004: Sarah Wilson (Chemistry)
- STU005: David Brown (Biology)

## Troubleshooting

1. **Camera not working**: Ensure your camera is not being used by another application
2. **Database connection failed**: Check your MySQL credentials and ensure the database server is running
3. **Fingerprint not detected**: Ensure good lighting and clean camera lens
4. **Low matching accuracy**: Try enrolling multiple fingerprint samples for better accuracy

## Security Notes

- Fingerprint templates are stored as base64-encoded JSON
- No raw fingerprint images are stored in the database
- Templates contain only geometric features, not actual fingerprint images
- Similarity threshold can be adjusted for security vs. convenience

## Dependencies

- opencv-python: Computer vision library for image processing
- mysql-connector-python: MySQL database connectivity
- numpy: Numerical computing for fingerprint analysis
- Pillow: Image processing support

## License

This project is open source and available under the MIT License.
