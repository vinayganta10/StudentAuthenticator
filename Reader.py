import cv2
import mysql.connector
import numpy as np
import json
from typing import Dict, Optional, Tuple
import sys
import hashlib
import base64
from config import HOST, USER, PASSWORD, DATABASE, PORT, CHARSET

class StudentFingerprintReader:
    def __init__(self, db_config: Dict[str, str]):
        """
        Initialize the fingerprint reader with database configuration
        
        Args:
            db_config: Dictionary containing MySQL connection parameters
        """
        self.db_config = db_config
        self.connection = None
        
    def connect_database(self) -> bool:
        """
        Establish connection to MySQL database
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            print("✅ Database connection established successfully!")
            return True
        except mysql.connector.Error as err:
            print(f"❌ Database connection failed: {err}")
            return False
    
    def close_database(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔌 Database connection closed.")
    
    def extract_fingerprint_features(self, fingerprint_image: np.ndarray) -> Optional[str]:
        """
        Extract fingerprint features and create a template
        
        Args:
            fingerprint_image: Input fingerprint image
            
        Returns:
            str: Base64 encoded fingerprint template or None if extraction fails
        """
        try:
            # Convert to grayscale if needed
            if len(fingerprint_image.shape) == 3:
                gray = cv2.cvtColor(fingerprint_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = fingerprint_image
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply threshold to get binary image
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours (fingerprint ridges)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Extract key features
            features = []
            for contour in contours:
                if cv2.contourArea(contour) > 50:  # Filter small contours
                    # Get contour properties
                    area = cv2.contourArea(contour)
                    perimeter = cv2.arcLength(contour, True)
                    if perimeter > 0:
                        circularity = 4 * np.pi * area / (perimeter * perimeter)
                        features.append({
                            'area': float(area),
                            'perimeter': float(perimeter),
                            'circularity': float(circularity)
                        })
            
            # Create a simple template from features
            template = {
                'features': features,
                'image_hash': hashlib.md5(fingerprint_image.tobytes()).hexdigest()
            }
            
            # Convert to base64 for storage
            template_json = json.dumps(template)
            template_b64 = base64.b64encode(template_json.encode()).decode()
            
            return template_b64
            
        except Exception as e:
            print(f" Fingerprint feature extraction failed: {e}")
            return None
    
    def scan_fingerprint(self) -> Optional[str]:
        """
        Scan fingerprint using camera
        
        Returns:
            str: Fingerprint template or None if no fingerprint detected
        """
        # Initialize camera
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print(" Could not open camera")
            return None
        
        print(" Place your finger on the camera lens...")
        print("Press 'c' to capture, 'q' to quit")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print(" Failed to read from camera")
                break
            
            # Display the frame
            cv2.imshow("Fingerprint Scanner - Press C to capture, Q to quit", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                print(" Capturing fingerprint...")
                
                # Extract fingerprint features
                template = self.extract_fingerprint_features(frame)
                
                if template:
                    print(" Fingerprint captured successfully!")
                    cap.release()
                    cv2.destroyAllWindows()
                    return template
                else:
                    print(" Failed to extract fingerprint features. Try again.")
        
        # Clean up
        cap.release()
        cv2.destroyAllWindows()
        return None
    
    def match_fingerprint(self, input_template: str) -> Optional[Dict]:
        """
        Match fingerprint template against database
        
        Args:
            input_template: Base64 encoded fingerprint template
            
        Returns:
            Dict: Student details if match found, None otherwise
        """
        if not self.connection or not self.connection.is_connected():
            print(" No database connection available")
            return None
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Get all fingerprint templates from database
            query = """
            SELECT 
                student_id,
                first_name,
                last_name,
                email,
                phone,
                department,
                year_of_study,
                enrollment_date,
                status,
                fingerprint_template
            FROM students 
            WHERE fingerprint_template IS NOT NULL
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
            if not results:
                print(" No fingerprint templates found in database")
                return None
            
            # Decode input template
            try:
                input_data = json.loads(base64.b64decode(input_template).decode())
                input_features = input_data.get('features', [])
            except:
                print(" Invalid fingerprint template format")
                return None
            
            best_match = None
            best_score = 0.0
            threshold = 0.7  # Similarity threshold
            
            for student in results:
                try:
                    # Decode stored template
                    stored_data = json.loads(base64.b64decode(student['fingerprint_template']).decode())
                    stored_features = stored_data.get('features', [])
                    
                    # Calculate similarity score
                    similarity = self.calculate_similarity(input_features, stored_features)
                    
                    if similarity > best_score and similarity > threshold:
                        best_score = similarity
                        best_match = student
                        
                except Exception as e:
                    print(f" Error processing template for {student['student_id']}: {e}")
                    continue
            
            if best_match:
                print(f" Fingerprint match found! Similarity: {best_score:.2f}")
                # Remove fingerprint template from result
                del best_match['fingerprint_template']
                return dict(best_match)
            else:
                print(f" No matching fingerprint found (best score: {best_score:.2f})")
                return None
                
        except mysql.connector.Error as err:
            print(f" Database query failed: {err}")
            return None
    
    def calculate_similarity(self, features1: list, features2: list) -> float:
        """
        Calculate similarity between two fingerprint feature sets
        
        Args:
            features1: First set of features
            features2: Second set of features
            
        Returns:
            float: Similarity score (0.0 to 1.0)
        """
        if not features1 or not features2:
            return 0.0
        
        # Simple similarity calculation based on feature count and properties
        # In a real implementation, you'd use more sophisticated algorithms
        
        # Normalize feature counts
        count_similarity = min(len(features1), len(features2)) / max(len(features1), len(features2))
        
        # Calculate average area similarity
        areas1 = [f['area'] for f in features1]
        areas2 = [f['area'] for f in features2]
        
        if areas1 and areas2:
            avg_area1 = sum(areas1) / len(areas1)
            avg_area2 = sum(areas2) / len(areas2)
            area_similarity = 1.0 - abs(avg_area1 - avg_area2) / max(avg_area1, avg_area2)
        else:
            area_similarity = 0.0
        
        # Weighted combination
        similarity = 0.6 * count_similarity + 0.4 * area_similarity
        
        return min(1.0, max(0.0, similarity))
    
    def enroll_fingerprint(self, student_id: str) -> bool:
        """
        Enroll a new fingerprint for a student
        
        Args:
            student_id: Student ID to enroll
            
        Returns:
            bool: True if enrollment successful, False otherwise
        """
        print(f" Enrolling fingerprint for student: {student_id}")
        
        # Scan fingerprint
        template = self.scan_fingerprint()
        if not template:
            return False
        
        # Update database
        try:
            cursor = self.connection.cursor()
            query = """
            UPDATE students 
            SET fingerprint_template = %s 
            WHERE student_id = %s
            """
            cursor.execute(query, (template, student_id))
            self.connection.commit()
            cursor.close()
            
            print(f" Fingerprint enrolled successfully for {student_id}")
            return True
            
        except mysql.connector.Error as err:
            print(f" Database update failed: {err}")
            return False
    
    def run(self):
        """
        Main application loop
        """
        print(" Student Fingerprint Reader Application")
        print("=" * 45)
        
        # Connect to database
        if not self.connect_database():
            return
        
        try:
            while True:
                print("\n Choose an option:")
                print("1. Scan fingerprint to identify student")
                print("2. Enroll new fingerprint")
                print("3. Quit")
                
                choice = input("\nEnter your choice (1-3): ").strip()
                
                if choice == "3" or choice.lower() == "quit":
                    break
                elif choice == "1":
                    # Scan and identify fingerprint
                    template = self.scan_fingerprint()
                    
                    if template:
                        student_details = self.match_fingerprint(template)
                        
                        if student_details:
                            print("\n Student Details:")
                            print("-" * 30)
                            for key, value in student_details.items():
                                print(f"{key.replace('_', ' ').title()}: {value}")
                        else:
                            print(" No matching student found")
                    else:
                        print(" No fingerprint captured")
                        
                elif choice == "2":
                    # Enroll new fingerprint
                    student_id = input("Enter student ID to enroll: ").strip()
                    if student_id:
                        self.enroll_fingerprint(student_id)
                    else:
                        print(" Invalid student ID")
                else:
                    print(" Invalid choice. Please try again.")
        
        except KeyboardInterrupt:
            print("\n\n Application interrupted by user")
        finally:
            self.close_database()
            print(" Application closed successfully!")

def main():
    """
    Main function to run the application
    """
    # Database configuration from config.py
    db_config = {
        "host": HOST,
        "user": USER,
        "password": PASSWORD,
        "database": DATABASE,
        "port": PORT,
        "charset": CHARSET
    }
    
    # Create and run the fingerprint reader
    reader = StudentFingerprintReader(db_config)
    reader.run()

if __name__ == "__main__":
    main()
