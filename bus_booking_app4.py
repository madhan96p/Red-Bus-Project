import streamlit as st # importing modules
import mysql.connector
import pandas as pd

class BusBookingApp: # Busly App
 
    def __init__(self): # Database Connection
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='bus_data'
        )
        self.cursor = self.conn.cursor()
        self.df = None

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
       
        if bus_type is not None: # if selected "bus_type" query and params will be added
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
                    if Other_type == '': # if not selected "Others" 
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

                with col3: # Display booking details
                    st.subheader("Confirm Booking Details")
                    selected_bus_df = filtered_df[filtered_df['ID'] == selected_id]
                
                    if not selected_bus_df.empty:# Check if seats are available                      
                        selected_bus = selected_bus_df.iloc[0]
                
                        if selected_bus["Seats Available"] > 0: # If seats are available
                            self.dp_Bus_Details(selected_bus)

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

    def dp_Bus_Details(self, selected_bus): # displaying selected bus
        """Display the selected bus details."""

        details = { # To create table to USER confirmation by selected "ID"
            "Selected ID": selected_bus["ID"],
            "Bus Name": selected_bus["Bus Name"],
            "Departure → Arrival": selected_bus["Departure → Arrival"],
            "Bus_Type" : selected_bus["Bus Type"],
            "Departure Time": selected_bus["Departure Time"],
            "Arrival Time": selected_bus["Arrival Time"],
            "Duration": selected_bus["Duration"],
            "Fare (INR)": f"₹{selected_bus['Fare']}", 
            "Seats Available": selected_bus["Seats Available"]
        }
       
        st.dataframe(pd.DataFrame(details.items(), columns=["Detail", "Value"]), hide_index=True)

    def run(self): # Run bus_booking applications
        """Run the Streamlit app."""
        self.hide_elements()

        col1, col2, col3 = st.columns([1, 2, 1])

        with col1: # Logo
            st.image("Busly.png", caption="", width=150)  
    
        with col2: # App name and Slogan
            st.markdown('<center><h1>Busly</h1></center>',True)
            st.markdown('<center><h6><em>‘Every Route. Every Stop. One App.’</em></h6></center>',True)

        with col3: # Mt column
            pass  

        st.markdown('---')

        from_route, to_route, bus_type, Other_type, rating, fare = self.render_sidebar()
        self.fetch_filters(rating, fare, bus_type, Other_type, from_route, to_route)
       
        if not self.df.empty: # Check all filters are maching datas
            st.title("Bus Booking System")
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

if __name__ == "__main__": # To run Busly Booking app
    app = BusBookingApp()
    app.run()
