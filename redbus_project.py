import re #modules
import csv 
import time
import pymysql
import pandas as pd
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
           
            while page < 6:  # Continue until no "next(num)" button is found
              
                try: # Wait for route elements to load
                    routes = self.wait.until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "route"))
                    )
                    log_message = f"From {link} Page {page}: Total routes found {len(routes)}\n"
                    print(log_message.strip())
                    log_file.write(log_message)  

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

                except Exception as e: # There is no more page below 6 eg: 1,2 will show error
                    error_message = f"No more pages or an error occurred: {e}\n"
                    print(error_message.strip())
                    log_file.write(error_message)  # Write error message to the file
                    break
   
    def scrape_all(self): # Scraping route link from State link
        """
        Scrape data from all provided links.
        """
        for link in self.links:
            try:
                print(f"Scraping link: {link}")
                self.scrape_routes(link)
            except Exception as e:
                print(f"Error scraping link {link}: {e}")
        
        self.driver.quit()

    def save_results(self, filename='Bus_Data.xlsx'): # save results to xlsx or csv
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
        self.Bus_Details = [] 

    def scrape_route_details(self):  # Main scraping function --- scraping_log.txt
        """Scrape bus details for each route in route_links."""
        
        with open('scraping_log.txt', 'a') as log_file: # for cross check
          
            for link in self.route_links: # iterating link from links
    
                try: # Opens link
                    self.chrome.get(link)
                    self.chrome.maximize_window()
                    time.sleep(10)  # Allow the page to load
                    
                    try: #Extracting route info
                        # Calling route information
                        route_name, total_buses = self._extract_route_info()
                        print(log_file.write(f"Scraping route: {route_name}, Total Buses: {total_buses}\n"))  # Log to file
                        
                        # Load all bus elements
                        self._load_all_buses()
                        
                        # Extract bus details
                        self._extract_Bus_Details(route_name, total_buses, link,log_file) # print(f"Total bus containers found: {len(bus_elements)}") in extract_Bus_Details

                    except Exception as e:
                        print(f"Error scraping route: {e},")

                except Exception as e:
                    print(f"Error scraping route: {e}")
       
        self.chrome.quit()
        return self.Bus_Details

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
        try: # Route name & count
            route_name = self.chrome.find_element(By.CSS_SELECTOR, "h1.D136_h1").text
            total_buses = self.chrome.find_element(By.CSS_SELECTOR, ".f-bold.busFound").text
            return route_name, total_buses
        
        except Exception as e: # if the elemont is not found
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
        
        except Exception as e: # if there is no amenities
            print(f"Error extracting amenities: {e}")
            return []

    def _extract_Bus_Details(self, route_name, total_buses, link, log_file):  # Extract bus details
        """Extract bus details from the loaded page."""
        
        try: # finding and saving bus containers
            bus_elements = self.chrome.find_elements(By.CLASS_NAME, "bus-item")
            print(log_file.write(f"Total bus containers found for {link}: {len(bus_elements)}\n"))
 
        except Exception as e: # Error while scrapeing details
            print(f"Error extracting bus-item: {e}")
            return
        
        for bus in bus_elements: # starts loop that iterates each element
     
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
                
                ## Extract amenities
                # amenities = self._extract_amenities(bus)
                Link = link
                
                self.Bus_Details.append({ # appending dbus details to CSV
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

            except Exception as e: # if error while extracting
                print(f"Error extracting bus details: {e}")

    def save_results(self, filename='Bus_Details.csv'): # Save reslts to xlsx or csv
        """
        Save the scraped data to a CSV file or excel.
        """
        df = pd.DataFrame(self.Bus_Details)
        df.to_csv(filename, index=False) 
        print(f"Data saved to {filename}")
        return df

class Data_base:  # bus details to SQL
    def __init__(self, csv_file_path): # calling csv file and instalizing
        self.host = "localhost"       
        self.user = "root"           
        self.password = ""       
        self.database = "bus_data"   
        self.csv_file_path = csv_file_path  

        try: # connecting to PHPmyAdmin
            self.conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            self.cursor = self.conn.cursor()
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            self.cursor.execute(f"USE {self.database}")
            self.create_table()
       
        except pymysql.Error as e: # if error while connecting
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
            
    def categorize_bus_type(self, bus_type): # like label Encoding
        bus_type_lower = bus_type.lower()

        # Check for Non-AC variants
        if re.search(r'non[-]?ac|non[-]?a\.c\.|non[-]?a/c', bus_type_lower):
   
            if re.search(r'sleeper', bus_type_lower):
                return 'Sleeper'
   
            elif re.search(r'seater', bus_type_lower):
                return 'Seater'
   
            elif re.search(r'push back', bus_type_lower):
                return 'Push Back'

        # Check for AC variants
        elif re.search(r'ac|a\.c\.|a/c', bus_type_lower):
    
            if re.search(r'sleeper', bus_type_lower):
                return 'AC Sleeper'
      
            elif re.search(r'seater', bus_type_lower):
                return 'AC Seater'
    
            elif re.search(r'push back', bus_type_lower):
                return 'AC Push Back'

        # Check for basic types without AC specification
        else: # non Ac
  
            if re.search(r'sleeper', bus_type_lower):
                return 'Sleeper'
 
            elif re.search(r'seater', bus_type_lower):
                return 'Seater'
  
            elif re.search(r'push back', bus_type_lower):
                return 'Push Back'

        # Default case if none of the patterns match
        return bus_type

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

        except Exception as e: # if error during intersection
            print(f"Error during data insertion: {e}")
    
    def close_connection(self): # connection closing
    
        try: # closing sql
            self.cursor.close()
            self.conn.close()
            print("Database connection closed.")
       
        except Exception as e: # if any error while closing
            print(f"Error while closing the connection: {e}")

class BusBookingApp: # Busly App
 
    def __init__(self): # Database Connection
        try:
            self.conn = pymysql.connect(
                host='localhost',
                user='root',
                password='',
                database='bus_data'
            )
            self.cursor = self.conn.cursor()
            self.df = None
        except pymysql.Error as err:
            st.error(f"Error: {err}")

    def hide_elements(self): # <`s hidding
    
        st.markdown( # hidding Unessary "><"
            """ 
            <style>
                .stAppHeader.st-emotion-cache-h4xjwg.e10jh26i0,
                .e14lo1l1.st-emotion-cache-1b2ybts.ex0cdmw0,
                .st-bt.st-cn.st-b6.st-co.st-cp, 
                .st-emotion-cache-gi0tri.e121c1cl3 {
                    visibility : hidden;
                }
            </style>
        """, True)

    def distinct_filters(self): # Unique values {Also need to add available seats}
        """Fetch distinct values for From, To, and Bus Type dropdowns."""
       
        self.cursor.execute("SELECT DISTINCT SUBSTRING_INDEX(route_name, ' to ', 1) FROM buses")
        from_routes = sorted([row[0] for row in self.cursor.fetchall()])

        self.cursor.execute("SELECT DISTINCT SUBSTRING_INDEX(route_name, ' to ', -1) FROM buses")
        to_routes = sorted([row[0] for row in self.cursor.fetchall()])

        self.cursor.execute("SELECT DISTINCT bus_type FROM buses WHERE bus_type IN ('Push Back','Seater','AC Seater','Sleeper','AC Sleeper','AC Push Back')")
        bus_types = sorted([row[0] for row in self.cursor.fetchall()])

        self.cursor.execute("SELECT DISTINCT bus_type FROM buses WHERE bus_type NOT IN ('Push Back','Seater','AC Seater','Sleeper','AC Sleeper','AC Push Back')")
        Other_types = sorted([row[0] for row in self.cursor.fetchall()])   

        return from_routes, to_routes, bus_types, Other_types

    def fetch_filters(self, rating, fare, bus_type, Other_type, from_route, to_route): # Fetching filtered data
        """Fetch filtered bus details based on the sidebar selections."""
       
        query = """ 
            SELECT 
                id, route_name, route_link, bus_name, bus_type,
                CAST(departing_time AS CHAR) AS departing_time,
                boarding_point, duration,
                CAST(reaching_time AS CHAR) AS reaching_time,
                dropping_point, star_rating, fare, seats_available,
                CONCAT(
                    SUBSTRING_INDEX(route_name, ' to ', 1), ' → ', 
                    SUBSTRING_INDEX(route_name, ' to ', -1)
                    ) AS merged_route
            FROM buses
            WHERE
                star_rating >= %s AND
                star_rating <= %s AND
                fare >= %s AND
                fare <= %s AND
                SUBSTRING_INDEX(route_name, ' to ', 1) = %s AND
                SUBSTRING_INDEX(route_name, ' to ', -1) = %s
        """
        params = [rating[0], rating[1], fare[0], fare[1], from_route, to_route]
       
        if bus_type is not None and bus_type != 'Others': # if selected "bus_type" query and params will be added
            query += " AND bus_type = %s"
            params.append(bus_type)
        
        if Other_type is not None: # if selected "Others" query and params will be added
            query += " AND bus_type = %s"
            params.append(Other_type)

        self.cursor.execute(query, params)
        data = self.cursor.fetchall()

        self.df = pd.DataFrame(data, columns=[ # To display in df after filtering using query
            "ID", "Route Name", "Route Link", "Bus Name", "Bus Type", "Departure Time", 
            "Boarding Point", "Duration", "Arrival Time", "Dropping Point", "Rating", 
            "Fare", "Seats Available", "Departure → Arrival"
        ])
        self.df["Other Type"] = self.df.apply(lambda row: row["Bus Type"] if row["Bus Type"] != "Others" else "Other Type", axis=1)

    def render_sidebar(self): # sidebar User Input
        """Render sidebar and get filter as inputs."""
        
        from_routes, to_routes, bus_types, Other_types = self.distinct_filters()
        from_routes = [""] + from_routes
        to_routes = [""] + to_routes
        bus_types = [""] + ['Others'] + bus_types
        Other_types = [""] + Other_types

        with st.sidebar: # Nested Filter
            with st.expander("Route Filters"): # To filter bus route  
                from_route = st.selectbox("Select (From) Route", from_routes)
                to_route = st.selectbox("Select (To) Route", to_routes)
        
            with st.expander("Bus Filters"): # To filter Bus details
                bus_type = st.selectbox("Select Bus Type", bus_types) 
                
                if bus_type == '': # if not selected "bus_type" display all types
                    bus_type = None

                if bus_type == 'Others': # if selected "Others" (option) will visible
                    Other_type = st.selectbox("Select Other Bus Type", Other_types)
                    if Other_type == '': # if other type is empty display all 
                        Other_type = None
               
                else: # if not selected "Others"
                    Other_type = None
                    
                rating = st.slider("Select Rating", min_value=1.0, max_value=5.0, value=(1.0, 5.0))
                fare = st.slider("Select Fare Range", min_value=0, max_value=10000, value=(0, 10000))
        
        return from_route, to_route, bus_type, Other_type, rating, fare

    def filter_bd_point(self): # boarding & droping point filter inside page
        """Add dropdowns for Boarding Point and Dropping Point filtering."""
        
        col1, col2, col3 = st.columns([1, 1, 1]) 
        with col1: # boarding_point filter @ 1st col
            boarding_point = st.selectbox("Select Boarding Point", options=[""] + list(self.df["Boarding Point"].unique()))
       
        with col2: # dropping_point filter @ 2nd col
            dropping_point = st.selectbox("Select Dropping Point", options=[""] + list(self.df["Dropping Point"].unique()))
     
        with col3: # Departure time filter in 3rd column
            departing_time = st.selectbox("Select Departure Time",options=[""] + list(self.df["Departure Time"].unique()),)

        if boarding_point == "" and dropping_point == "" and departing_time == "":# No filters selected, show all routes
            filtered_df = self.df
        
        elif dropping_point == "" and departing_time == "":# Only boarding point selected
            filtered_df = self.df[self.df["Boarding Point"] == boarding_point]

        elif departing_time == "":# Only Boarding and Dropping Points selected
            filtered_df = self.df[(self.df["Boarding Point"] == boarding_point) & (self.df["Dropping Point"] == dropping_point)]
        
        else: # All filters selected
            filtered_df = self.df[ (self.df["Boarding Point"] == boarding_point) & (self.df["Dropping Point"] == dropping_point) & (self.df["Departure Time"] == departing_time)]

        self.df = filtered_df # Display filtered data

    def booking_data(self):# Booking data
        """Display the filtered DataFrame and booking options."""
        self.df["Departure → Arrival"] = self.df["Boarding Point"] + " → " + self.df["Dropping Point"]
        filtered_df = self.df[ # Filter the df to display relevant columns
            ["ID", "Route Name", "Departure → Arrival", "Bus Name", "Bus Type","Other Type",
                "Departure Time", "Duration", "Arrival Time", "Rating", "Fare", "Seats Available"]
            ]

        if not filtered_df.empty: # Check if any buses match the selected criteria
            st.subheader("Available Buses")
            columns_to_remove = ["Other Type", "Route Name"] 
            filtered_df = filtered_df.drop(columns=columns_to_remove)
            st.dataframe(filtered_df.style.format({"Fare": "₹{:,.2f}","Rating": "{:,.1f}"}), hide_index=True)
            st.markdown('---')

            if "show_booking_details" not in st.session_state: # To show booking details Available or not
                st.session_state.show_booking_details = False

            if st.button("Book Now"): # To Book Now
                st.session_state.show_booking_details = True

            if st.session_state.show_booking_details: # To display booking details
                available_ids = filtered_df["ID"].tolist()

                col1, col3 = st.columns([2, 5])
                with col1: # Selecting "ID"
                    selected_id = st.selectbox("Select Bus ID to Book", available_ids, key="bus_id_select")
                    selected_bus_df = filtered_df[filtered_df['ID'] == selected_id]
                
                    if not selected_bus_df.empty:# Check if seats are available                      
                        selected_bus = selected_bus_df.iloc[0]
                
                        if selected_bus["Seats Available"] > 0: # If seats are available
                            self.ldp_Bus_Details(selected_bus)
                      
                        else:
                            pass
                   
                    else:
                        pass

                with col3: # Display booking details
                    st.subheader("Confirm Booking Details")
                    selected_bus_df = filtered_df[filtered_df['ID'] == selected_id]
                
                    if not selected_bus_df.empty:# Check if seats are available                      
                        selected_bus = selected_bus_df.iloc[0]
                
                        if selected_bus["Seats Available"] > 0: # If seats are available
                            self.rdp_Bus_Details(selected_bus)

                            if st.button("Confirm Booking"):# Confirm Booking
                                self.book_bus(selected_id)
                                st.success("Your booking is confirmed!")
                      
                        else: # if selected bus is fully booked
                            st.error("Sorry, this bus is fully booked. Please select another bus.")
                   
                    else: # if not selected any bus
                        st.error("Please try again.")
                st.markdown('---')

        else: # if no buses match the selected criteria
            st.warning("No buses match your selected route and timing preferences. Please try adjusting your filters.")

    def book_bus(self, bus_id): # BOok Bus by choosing bus id
        """Update the seats for a selected bus."""
        try: # Seats will reduse and save permnt
            self.cursor.execute("UPDATE buses SET seats_available = seats_available - 1 WHERE id = %s AND seats_available > 0", (bus_id,))
            self.conn.commit()
            self.cursor.execute("SELECT seats_available FROM buses WHERE id = %s", (bus_id,))
            remaining_seats = self.cursor.fetchone()[0]

            if remaining_seats >= 0: # For user confimation
                st.success(f"Bus ID {bus_id} successfully booked! Remaining Seats: {remaining_seats}")
     
            else: # if fulled
                st.warning("This bus is already fully booked.")
     
        except Exception as e: # if buses already fulled
            st.error(f"An error occurred: {e}")

    def rdp_Bus_Details(self, selected_bus): # displaying selected bus
        """Display the selected bus details."""

        details = { # To create table to USER confirmation by selected "ID"
            "Selected ID": selected_bus["ID"],
            "Bus Name": selected_bus["Bus Name"],
            "Departure → Arrival": selected_bus["Departure → Arrival"],
            "Bus_Type" : selected_bus["Bus Type"],
            "Departure Time": selected_bus["Departure Time"],
            "Arrival Time": selected_bus["Arrival Time"],
            "Seats Available": selected_bus["Seats Available"]
        }
        st.dataframe(pd.DataFrame(details.items(), columns=["Detail", "Value"]), hide_index=True)

    def ldp_Bus_Details(self, selected_bus): # displaying selected bus

        fare_Rating = { "Rating": selected_bus["Rating"], 
                       "Fare (INR)": f"₹{selected_bus['Fare']}", 
                       "Duration": selected_bus["Duration"]
                       }
        
        st.dataframe(pd.DataFrame(fare_Rating.items(), columns=["Attribute", "Data Value"]), hide_index=True)

    def run(self): # Run bus_booking applications
        """Run the Streamlit app."""
        # s elf.hide_elements()

        col1, col2, col3 = st.columns([1, 2, 1])

        with col1: # Logo
            st.image("Busly.png", caption="", width=140)  
    
        with col2: # App name and Slogan
            st.markdown('<center><h1>Busly</h1></center>',True)
            st.markdown('<center><h6><em>‘Every Route. Every Stop. One App.’</em></h6></center>',True)

        with col3: # Mt column
            pass  

        st.markdown('---')

        from_route, to_route, bus_type, Other_type, rating, fare = self.render_sidebar()
        self.fetch_filters(rating, fare, bus_type, Other_type, from_route, to_route)
       
        if not self.df.empty: # Check all filters are maching datas
            st.title("Busly Booking System")
            self.filter_bd_point()
            self.booking_data()
     
        else: # if anything miss match
            filter = "MISS MATCH"
            if filter == "MISS MATCH": # To Show image
                st.markdown( # Select Criteria to alin center
                    """<center><h6><em>Adjust your filters to explore available buses and find the best options for your journey.</em></h6></center>""", True)
                col1, col2, col3 = st.columns([1, 1, 1])

                with col1: # Mt column
                    pass  
          
                with col2: # Error image column
                    st.image("SelectCriteria.webp", caption="No buses match the selected criteria.", width=200)
            
                with col3: # MT column
                    pass  
