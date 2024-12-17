import re
import csv
import mysql.connector

class Data_base:  # bus details to SQL
    def __init__(self, csv_file_path):
        self.host = "localhost"       
        self.user = "root"           
        self.password = ""       
        self.database = "bus_data"   
        self.csv_file_path = csv_file_path  

        try: # connecting to PHPmyAdmin
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            self.cursor = self.conn.cursor()
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            self.cursor.execute(f"USE {self.database}")
            self.create_table()
       
        except mysql.connector.Error as e:
            print(f"Error: {e}")

    def create_table(self): # creating table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS buses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            route_name TEXT,
            route_link TEXT,
            bus_name TEXT,
            bus_type TEXT,
            departing_time TIME,
            boarding_point TEXT,
            duration TEXT,
            reaching_time TIME,
            dropping_point TEXT,
            star_rating FLOAT,
            fare FLOAT,
            seats_available INT,
            UNIQUE(route_link, bus_name, departing_time)
        )
        """
        self.cursor.execute(create_table_query)

    def is_row_existing(self, route_link, bus_name, departing_time):
        query = """
        SELECT COUNT(*) FROM buses
        WHERE route_link = %s AND bus_name = %s AND departing_time = %s
        """
        self.cursor.execute(query, (route_link, bus_name, departing_time))
        return self.cursor.fetchone()[0] > 0
            
    def categorize_bus_type(self, bus_type):
        bus_type_lower = bus_type.lower()

        # Check for Non-AC variants
        if re.search(r'non[-]?ac|non[-]?a\.c\.|non[-]?a/c', bus_type_lower):
            if re.search(r'sleeper', bus_type_lower):
                return 'Non-AC Sleeper'
            elif re.search(r'seater', bus_type_lower):
                return 'Non-AC Seater'
            elif re.search(r'push back', bus_type_lower):
                return 'Non-AC Push Back'

        # Check for AC variants
        elif re.search(r'ac|a\.c\.|a/c', bus_type_lower):
            if re.search(r'sleeper', bus_type_lower):
                return 'AC Sleeper'
            elif re.search(r'seater', bus_type_lower):
                return 'AC Seater'
            elif re.search(r'push back', bus_type_lower):
                return 'AC Push Back'

        # Check for basic types without AC specification
        else:
            if re.search(r'sleeper', bus_type_lower):
                return 'Sleeper'
            elif re.search(r'seater', bus_type_lower):
                return 'Seater'
            elif re.search(r'push back', bus_type_lower):
                return 'Push Back'

        # Default case if none of the patterns match
        return 'Others'

    def insert_data_from_csv(self, csv_file_path):
        inserted_count = 0
        not_inserted_count = 0 

        try:  # inserting data
            with open(csv_file_path, mode='r') as file:
                csv_reader = csv.reader(file)
                header = next(csv_reader)

                insert_query = """
                INSERT INTO buses (
                    route_name, route_link, bus_name, bus_type, departing_time, boarding_point, 
                    duration, reaching_time, dropping_point, star_rating, fare, seats_available
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                for row in csv_reader:  # Base cleaning
                    route_name = row[0].replace('Bus', '').strip() if row[0] else "Unknown"
                    route_link = row[1].strip() if row[1] else "Unknown"
                    bus_name = row[3].strip() if row[3] else "Unknown"
                    raw_bus_type = row[4].strip() if row[4] else "Unknown"
                    bus_type = self.categorize_bus_type(raw_bus_type) 
                    departing_time = row[5].strip() if row[5] else "00:00:00"
                    boarding_point = row[6].strip() if row[6] else "Unknown"
                    duration = row[7].strip() if row[7] else "Unknown"
                    reaching_time = row[8].strip() if row[8] else "00:00:00"
                    dropping_point = row[9].strip() if row[9] else "Unknown"
                    star_rating = float(row[10].replace("New", "0")) if row[10] else 0
                    fare_str = row[11].replace("Starts from\nINR", "").replace("New", "").replace("Starts from", "").replace("INR", "").strip()
                    fare = float(fare_str.split()[0]) if fare_str else 0
                    seats_available_str = row[12].replace("Seats available", "").replace("Seat available", "").strip()
                    seats_available = int(seats_available_str) if seats_available_str.isdigit() else 0

                    # Check for duplicates before inserting
                    if not self.is_row_existing(route_link, bus_name, departing_time):
                        self.cursor.execute(insert_query, (
                            route_name, route_link, bus_name, bus_type, departing_time, boarding_point,
                            duration, reaching_time, dropping_point, star_rating, fare, seats_available
                        ))
                        inserted_count += 1  
                    else:  # for duplicate rows
                        not_inserted_count += 1  
            
            self.conn.commit()
            print(f"Data from {csv_file_path} has been successfully processed,\n"
                f"{inserted_count} rows inserted into the database and\n"
                f"{not_inserted_count} rows not inserted into the database")

        except Exception as e:
            print(f"Error during data insertion: {e}")
    
    def close_connection(self): # connection closing
        try: # closing sql
            self.cursor.close()
            self.conn.close()
            print("Database connection closed.")
       
        except Exception as e:
            print(f"Error while closing the connection: {e}")

csv_file_path = 'bus_details.csv'
db_handler = Data_base(csv_file_path)
db_handler.insert_data_from_csv(csv_file_path)
db_handler.close_connection()