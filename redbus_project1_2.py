import csv #modules
import time
import pandas as pd
import mysql.connector
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

class Bus_links_scraper: # scraping links and route name
 
    def __init__(self, links): # Initializing
        """
        Initialize the scraper with a list of links to scrape.
        """
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        self.links = links
        self.bus_data = []

    def scrape_routes(self, link): # page with Route & links
        """
        Scrape bus route information from a given link.
        """
        self.driver.get(link)
        page = 1
        with open('scraping_log.txt', 'a') as log_file:  # Open log file in append mode
           
            while page < 6:  # Continue until no "next" button is found
                try:
                    # Wait for route elements to load
                    routes = self.wait.until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "route"))
                    )
                    log_message = f"From {link} Page {page}: Total routes found {len(routes)}\n"
                    print(log_message.strip())
                    log_file.write(log_message)  # Write log to the file

                    # Extract route name and link
                    for route in routes:
                        self.bus_data.append({
                            "route_name": route.text,
                            "route_link": route.get_attribute("href")
                        })

                    next_button = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, f"//div[text()='{page}']"))
                    )
                    ActionChains(self.driver).move_to_element(next_button).perform()
                    next_button.click()
                    time.sleep(2)
                    page += 1

                except Exception as e:
                    error_message = f"No more pages or an error occurred: {e}\n"
                    print(error_message.strip())
                    log_file.write(error_message)  # Write error message to the file
                    break
   
    def scrape_all(self): # main
        """
        Scrape data from all provided links.
        """
        for link in self.links:
            try:
                print(f"Scraping link: {link}")
                self.scrape_routes(link)
            except Exception as e:
                print(f"Error scraping link {link}: {e}")
        
        # Close the browser when done
        self.driver.quit()

    def save_results(self, filename='bus_data.xlsx'): # xlsx or csv
        """
        Save the scraped data to a CSV file or excel.
        """
        df = pd.DataFrame(self.bus_data)
        df.to_excel(filename, index=False) # to_excel or csv
        print(f"Data saved to {filename}")
        return df
    
class BusDetails:  # To scrape bus details
    """A class to scrape bus details from Redbus using Selenium."""

    def __init__(self, route_links): #initializing
        """Initialize the scraper with the Chrome browser and route links."""
       
        self.chrome = webdriver.Chrome() 
        self.wait = WebDriverWait(self.chrome, 15)  
        self.route_links = route_links
        self.bus_details = [] 

    def scrape_route_details(self):  # Main scraping function --- scraping_log.txt
        """Scrape bus details for each route in route_links."""
        with open('scraping_log.txt', 'a') as log_file: # for cross check
            for link in self.route_links:
    
                try: # Opens link
                    self.chrome.get(link)
                    self.chrome.maximize_window()
                    time.sleep(10)  # Allow the page to load
                    
                    try:
                        # Extract route information
                        route_name, total_buses = self._extract_route_info()
                        print(log_file.write(f"Scraping route: {route_name}, Total Buses: {total_buses}\n"))  # Log to file
                        
                        # Load all bus elements
                        self._load_all_buses()
                        
                        # Extract bus details
                        self._extract_bus_details(route_name, total_buses, link,log_file) # print(f"Total bus containers found: {len(bus_elements)}") in extract_bus_details

                    except Exception as e:
                        print(f"Error scraping route: {e},")

                except Exception as e:
                    print(f"Error scraping route: {e}")
       
        self.chrome.quit()
        return self.bus_details

    def _load_all_buses(self):  # Handle scrolling and view buttons
        """Click all view buttons and scroll the page to load all buses."""
        try: # view buttons
            view_buttons = self.chrome.find_elements(By.CSS_SELECTOR, "div[class='button']")
            for button in reversed(view_buttons):
                button.click()
                time.sleep(3)
     
        except Exception as e:
            print(f"Error clicking view buttons: {e}")
            
        try: # scroll
            for _ in range(1500):
                self.chrome.execute_script('window.scrollBy(0, 100)')
 
        except Exception as e:
            print(f"Error while scrolling: {e}")

    def _extract_route_info(self):  # Extract route info
        """Extract the route name and total buses."""
        try: # Ruote name & count
            route_name = self.chrome.find_element(By.CSS_SELECTOR, "h1.D136_h1").text
            total_buses = self.chrome.find_element(By.CSS_SELECTOR, ".f-bold.busFound").text
            return route_name, total_buses
        
        except Exception as e:
            print(f"Error extracting route info: {e}")
            return "Unknown Route", "NA"

    def _extract_amenities(self, bus):  # Extract amenities
        """Extract amenities for a specific bus."""
        
        try: # amenities
            amenities_button = bus.find_element(By.CLASS_NAME, "amenities-icon")
            self.chrome.execute_script("arguments[0].click();", amenities_button)
            time.sleep(0.5)
            amenities_elements = self.wait.until(
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".amenlist li"))
            )
            return [amenity.text for amenity in amenities_elements]
        
        except Exception as e:
            print(f"Error extracting amenities: {e}")
            return []

    def _extract_bus_details(self, route_name, total_buses, link, log_file):  # Extract bus details
        """Extract bus details from the loaded page."""
        
        try: # bus containers
            bus_elements = self.chrome.find_elements(By.CLASS_NAME, "bus-item")
            print(log_file.write(f"Total bus containers found for {link}: {len(bus_elements)}\n"))
 
        except Exception as e:
            print(f"Error extracting bus-item: {e}")
            return
        
        for bus in bus_elements:
     
            try: # collecting datas
                
                operator = bus.find_element(By.CLASS_NAME, "travels").text
                bus_type = bus.find_element(By.CLASS_NAME, "bus-type").text
                departure_time = bus.find_element(By.CLASS_NAME, "dp-time").text
                boarding_point = bus.find_element(By.CLASS_NAME, "dp-loc").text
                duration = bus.find_element(By.CLASS_NAME, "dur").text
                arrival_time = bus.find_element(By.CLASS_NAME, "bp-time").text
                dropping_point = bus.find_element(By.CLASS_NAME, "bp-loc").text
                ratings = bus.find_element(By.CLASS_NAME, "rating-sec").text
                fare = bus.find_element(By.CLASS_NAME, "seat-fare").text
                seats_available = bus.find_element(By.CLASS_NAME, "seat-left").text
                
                # Extract amenities
                # amenities = self._extract_amenities(bus)
                Link = link
                # Append bus details to the list
                self.bus_details.append({
                    "Route Name": route_name,
                    "Route Link": Link,
                    "Total Buses": total_buses,
                    "Operator": operator,
                    "Bus Type": bus_type,
                    "Departure Time": departure_time,
                    "Boarding Point": boarding_point,
                    "Duration": duration,
                    "Arrival Time": arrival_time,
                    "Dropping Point": dropping_point,
                    "Ratings": ratings,
                    "Fare": fare,
                    "Seats Available": seats_available,
                    # "Amenities": amenities,
                })

            except Exception as e:
                print(f"Error extracting bus details: {e}")

    def save_results(self, filename='bus_details.csv'): # xlsx or csv
        """
        Save the scraped data to a CSV file or excel.
        """
        df = pd.DataFrame(self.bus_details)
        df.to_csv(filename, index=False) # to_excel or csv
        print(f"Data saved to {filename}")
        return df

class Data_base_handler: # bus details to Sql
 
    def __init__(self, csv_file_path):
        self.host = "localhost"       # Fixed value for host
        self.user = "root"            # Fixed value for user
        self.password = ""            # Fixed value for password
        self.database = "bus_data"    # Fixed value for database name
        self.csv_file_path = csv_file_path  # Path to the CSV file

        try: # connecting to PHPmyAdmin
            self.conn = mysql.connector.connect( #pymys
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

    def insert_data_from_csv(self, csv_file_path):
        inserted_count = 0
        not_inserted_count = 0 

        try: # inserting datas
            with open(csv_file_path, mode='r') as file:
                csv_reader = csv.reader(file)
                header = next(csv_reader)

                insert_query = """
                INSERT INTO buses (
                    route_name, route_link, bus_name, bus_type, departing_time, boarding_point, 
                    duration, reaching_time, dropping_point, star_rating, fare, seats_available
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                for row in csv_reader: # Base cleaning
                    route_name = row[0].replace('Bus', '') if row[0] else "Unknown"
                    route_link = row[1] if row[1] else "Unknown"
                    bus_name = row[3] if row[3] else "Unknown"
                    bus_type = row[4] if row[4] else "Unknown"
                    departing_time = row[5] if row[5] else "00:00:00"
                    boarding_point = row[6] if row[6] else "Unknown"
                    duration = row[7] if row[7] else "Unknown"
                    reaching_time = row[8] if row[8] else "00:00:00"
                    dropping_point = row[9] if row[9] else "Unknown"
                    star_rating = float(row[10].replace("New", "0")) if row[10] else 0
                    fare = float(row[11].replace("Starts from\nINR", "").replace("New", "").replace("Starts from", "").replace("INR", "").split()[0]) if row[11] else 0
                    seats_available = int(row[12].replace("Seats available", "").replace("Seat available", "")) if row[12] else 0
                    
                    if not self.is_row_existing(route_link, bus_name, departing_time):
                        self.cursor.execute(insert_query, (
                            route_name, route_link, bus_name, bus_type, departing_time, boarding_point,
                            duration, reaching_time, dropping_point, star_rating, fare, seats_available
                        ))
                        inserted_count += 1  
                 
                    else: # for duplicate rows
                        # print(f"Duplicate entry found and skipped: {bus_name} ({route_link})")
                        not_inserted_count += 1  
            self.conn.commit()
            print(f"Data from {csv_file_path} has been successfully processed,\n {inserted_count}rows inserted into the database and \n {not_inserted_count}rows not inserted into the database")
    
        except Exception as e:
            print(f"Error during data insertion: {e}")

    def close_connection(self): # connection closing
        try: # closing sql
            self.cursor.close()
            self.conn.close()
            print("Database connection closed.")
       
        except Exception as e:
            print(f"Error while closing the connection: {e}")

class BusBookingApp:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='bus_data'
        )
        self.cursor = self.conn.cursor()
        self.df = None

    def hide_elements(self):
        
        st.markdown("""
            <style>
                .stAppHeader.st-emotion-cache-h4xjwg.e10jh26i0 {
                    visibility : hidden;
                }
                .st-bt.st-cn.st-b6.st-co.st-cp, .st-emotion-cache-gi0tri.e121c1cl3 {
                    visibility : hidden;
                }
            </style>
        """, True)

    def distinct_filters(self):
        """Fetch distinct values for From, To, and Bus Type dropdowns."""
        self.cursor.execute("SELECT DISTINCT SUBSTRING_INDEX(route_name, ' to ', 1) FROM buses")
        from_routes = [row[0] for row in self.cursor.fetchall()]

        self.cursor.execute("SELECT DISTINCT SUBSTRING_INDEX(route_name, ' to ', -1) FROM buses")
        to_routes = [row[0] for row in self.cursor.fetchall()]

        self.cursor.execute("SELECT DISTINCT bus_type FROM buses")
        bus_types = [row[0] for row in self.cursor.fetchall()]

        return from_routes, to_routes, bus_types

    def fetch_filters(self, rating, fare, bus_type, from_route, to_route):
        """Fetch filtered bus details based on the sidebar selections."""
        query = """
            SELECT 
                id,
                route_name,
                route_link,
                bus_name,
                bus_type,
                CAST(departing_time AS CHAR) AS departing_time,
                boarding_point,
                duration,
                CAST(reaching_time AS CHAR) AS reaching_time,
                dropping_point,
                star_rating,
                fare,
                seats_available,
                CONCAT(SUBSTRING_INDEX(route_name, ' to ', 1), ' → ', SUBSTRING_INDEX(route_name, ' to ', -1)) AS merged_route
            FROM buses
            WHERE
                star_rating >= %s AND
                star_rating <= %s AND
                fare >= %s AND
                fare <= %s AND
                bus_type = %s AND
                SUBSTRING_INDEX(route_name, ' to ', 1) = %s AND
                SUBSTRING_INDEX(route_name, ' to ', -1) = %s
        """
        self.cursor.execute(query, (rating[0], rating[1], fare[0], fare[1], bus_type, from_route, to_route))
        data = self.cursor.fetchall()

        # Create DataFrame
        self.df = pd.DataFrame(data, columns=[
            "ID", "Route Name", "Route Link", "Bus Name", "Bus Type", "Departure Time", 
            "Boarding Point", "Duration", "Arrival Time", "Dropping Point", "Rating", 
            "Fare", "Seats Available", "Departure → Arrival"
        ])

    def render_sidebar(self):
        """Render sidebar and get filter inputs."""
        st.sidebar.header("Filters")
        from_routes, to_routes, bus_types = self.distinct_filters()

        from_route = st.sidebar.selectbox("Select Route (From)", from_routes)
        to_route = st.sidebar.selectbox("Select Route (To)", to_routes)
        bus_type = st.sidebar.selectbox("Select Bus Type", bus_types)
        rating = st.sidebar.slider("Select Rating", min_value=1.0, max_value=5.0, value=(1.0, 5.0))
        fare = st.sidebar.slider("Select Fare Range", min_value=0, max_value=10000, value=(0, 10000))

        return from_route, to_route, bus_type, rating, fare

    def filter_bd_point(self):
        """Add dropdowns for Boarding Point and Dropping Point filtering."""
        col1, col2 = st.columns([1, 1])
        with col1:
            boarding_point = st.selectbox("Select Boarding Point", self.df["Boarding Point"].unique())
        with col2:
            dropping_point = st.selectbox("Select Dropping Point", self.df["Dropping Point"].unique())

        self.df = self.df[(self.df["Boarding Point"] == boarding_point) & (self.df["Dropping Point"] == dropping_point)]

    def booking_data(self):
        """Display the filtered DataFrame and booking options."""
        self.df["Departure → Arrival"] = self.df["Boarding Point"] + " → " + self.df["Dropping Point"]
        filtered_df = self.df[[  # Rearrange columns
            "ID", "Route Name", "Departure → Arrival", "Bus Name", "Bus Type", "Departure Time",
            "Duration", "Arrival Time", "Rating", "Fare", "Seats Available"
        ]]

        if not filtered_df.empty:
            st.subheader("Filtered Buses by Departure → Arrival")
            st.dataframe(filtered_df, hide_index=True)

            col1, col2 = st.columns([1, 1])
            with col2:
                available_ids = filtered_df["ID"].tolist()
                selected_id = st.selectbox("Select Bus ID to Book", available_ids, key="bus_id_select")

                if st.button("Confirm Booking"):
                    self.book_bus(selected_id)

            with col1:
                st.subheader("Confirm Details")
                selected_bus = filtered_df[filtered_df['ID'] == selected_id].iloc[0]
                self.dp_bus_details(selected_bus)
        else:
            st.warning("No buses available for the selected filter.")

    def book_bus(self, bus_id):
        """Update the seats for a selected bus."""
        try:
            self.cursor.execute("UPDATE buses SET seats_available = seats_available - 1 WHERE id = %s AND seats_available > 0", (bus_id,))
            self.conn.commit()
            self.cursor.execute("SELECT seats_available FROM buses WHERE id = %s", (bus_id,))
            remaining_seats = self.cursor.fetchone()[0]

            if remaining_seats >= 0:
                st.success(f"Bus ID {bus_id} successfully booked! Remaining Seats: {remaining_seats}")
            else:
                st.warning("This bus is already fully booked.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

    def dp_bus_details(self, selected_bus):
        """Display the selected bus details."""
        details = {
            "Bus Name": selected_bus["Bus Name"],
            "Departure → Arrival": selected_bus["Departure → Arrival"],
            "Bus Type": selected_bus["Bus Type"],
            "Departure Time": selected_bus["Departure Time"],
            "Arrival Time": selected_bus["Arrival Time"],
            "Duration": selected_bus["Duration"],
            "Fare (INR)": selected_bus["Fare"],
            "Seats Available": selected_bus["Seats Available"]
        }
        st.dataframe(pd.DataFrame(details.items(), columns=["Detail", "Value"]), hide_index=True)

    def run(self):
        """Run the Streamlit app."""
        self.hide_elements()
        st.title("Bus Details")

        from_route, to_route, bus_type, rating, fare = self.render_sidebar()
        self.fetch_filters(rating, fare, bus_type, from_route, to_route)
        if not self.df.empty:
            self.filter_bd_point()
            self.booking_data()
        else:
            st.warning("No buses match the selected criteria.")
