import streamlit as st
import mysql.connector
import pandas as pd

class BusBookingApp: 
 
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

    def distinct_filters(self): # Unique values
        """Fetch distinct values for From, To, and Bus Type dropdowns."""
       
        self.cursor.execute("SELECT DISTINCT SUBSTRING_INDEX(route_name, ' to ', 1) FROM buses")
        from_routes = sorted([row[0] for row in self.cursor.fetchall()])

        self.cursor.execute("SELECT DISTINCT SUBSTRING_INDEX(route_name, ' to ', -1) FROM buses")
        to_routes = sorted([row[0] for row in self.cursor.fetchall()])

        self.cursor.execute("SELECT DISTINCT bus_type FROM buses")
        bus_types = sorted([row[0] for row in self.cursor.fetchall()])

        return from_routes, to_routes, bus_types

    def fetch_filters(self, rating, fare, bus_type, from_route, to_route): # Sidebar distinct bus details
        """Fetch filtered bus details based on the sidebar selections."""
        query = """ -- Filtering datas By using Sql
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
                    bus_type = %s AND
                    SUBSTRING_INDEX(route_name, ' to ', 1) = %s AND
                    SUBSTRING_INDEX(route_name, ' to ', -1) = %s
            """
      
        self.cursor.execute(query, (rating[0], rating[1], fare[0], fare[1], bus_type, from_route, to_route))
        data = self.cursor.fetchall()

        self.df = pd.DataFrame(data, columns=[ #  converting Filtered SQL To DataFrame
            "ID", "Route Name", "Route Link", "Bus Name", "Bus Type", "Departure Time", 
            "Boarding Point", "Duration", "Arrival Time", "Dropping Point", "Rating", 
            "Fare", "Seats Available", "Departure → Arrival"
        ])

    def render_sidebar(self): # sidebar User Input
        """Render sidebar and get filter inputs."""
        
        from_routes, to_routes, bus_types = self.distinct_filters()
        from_routes = [""] + from_routes
        to_routes = [""] + to_routes
        bus_types = [""] + bus_types

        with st.sidebar: # Nested Filter
            with st.expander("Route Filters"): # To filter bus route
                from_route = st.selectbox("Select (From) Route", from_routes)
                to_route = st.selectbox("Select (To) Route", to_routes)
        
        with st.sidebar: # nested Filter 
            with st.expander("Bus Filters"): # To filter Bus details
                bus_type = st.selectbox("Select Bus Type", bus_types)
                rating = st.slider("Select Rating", min_value=1.0, max_value=5.0, value=(1.0, 5.0))
                fare = st.slider("Select Fare Range", min_value=0, max_value=10000, value=(0, 10000))

        return from_route, to_route, bus_type, rating, fare

    def filter_bd_point(self): # boarding & droping point filter inside page
        """Add dropdowns for Boarding Point and Dropping Point filtering."""
        col1, col2, col3 = st.columns([1, 1, 1]) # space to occupy

        with col1: # boarding_point filter @ 1st col
            boarding_point = st.selectbox("Select Boarding Point", self.df["Boarding Point"].unique())
      
        with col2: # dropping_point filter @ 2nd col
            dropping_point = st.selectbox("Select Dropping Point", self.df["Dropping Point"].unique())
        
        with col3: # departing_time filter @ 3rd col
            departing_time = st.selectbox("Select Departure Time", 
                                            options=[""] + list(self.df["Departure Time"].unique()))

            if departing_time != "": # if user not selects departing_time
                self.df = self.df[(self.df["Boarding Point"] == boarding_point) & 
                                (self.df["Dropping Point"] == dropping_point) & 
                                (self.df["Departure Time"] == departing_time)]
       
            else: # if user selects departing_time
                self.df = self.df[(self.df["Boarding Point"] == boarding_point) & 
                                (self.df["Dropping Point"] == dropping_point)]

    def booking_data(self): # display datas and booking
        """Display the filtered DataFrame and booking options."""
        self.df["Departure → Arrival"] = self.df["Boarding Point"] + " → " + self.df["Dropping Point"]
       
        filtered_df = self.df[[  # Recreating df
            "ID", "Route Name", "Departure → Arrival", "Bus Name", "Bus Type", "Departure Time",
            "Duration", "Arrival Time", "Rating", "Fare", "Seats Available"
        ]]

        if not filtered_df.empty: # avail buses @ selected routes with various time
            st.subheader("Available Buses")
            st.dataframe(filtered_df.style.format({"Fare": "₹{:,.2f}"}), hide_index=True)

            available_ids = filtered_df["ID"].tolist()
            col1, col3= st.columns([5, 2])
            
            with col3: # Selecting "ID"
                selected_id = st.selectbox("Select Bus ID to Book",available_ids, key="bus_id_select")
            
            with col1: # view this column @1 CELL
                st.subheader("Confirm Booking Details")
                selected_bus = filtered_df[filtered_df['ID'] == selected_id].iloc[0] 
                self.dp_Bus_Details(selected_bus)

                if st.button("Confirm Booking"): # after seleted confirm button call {book_bus}
                    self.book_bus(selected_id)
           
        else: # to show user that filtered data not available
            st.warning("No buses available for the selected filter.")

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
            "Bus Name": selected_bus["Bus Name"],
            "Departure → Arrival": selected_bus["Departure → Arrival"],
            "Bus Type": selected_bus["Bus Type"],
            "Departure Time": selected_bus["Departure Time"],
            "Arrival Time": selected_bus["Arrival Time"],
            "Duration": selected_bus["Duration"],
            "Fare (INR)": f"₹{selected_bus["Fare"]}", 
            "Seats Available": selected_bus["Seats Available"]
        }
       
        st.dataframe(pd.DataFrame(details.items(), columns=["Detail", "Value"]), hide_index=True)

    def run(self): # Run bus_booking applications
        """Run the Streamlit app."""
        self.hide_elements()

        col1, col2, col3 = st.columns([1, 2, 1])

        with col1: # 
            st.image("Busly.png", caption="", width=150)  
    
        with col2: #
            st.markdown('<center><h1>Busly</h1></center>',True)
            st.markdown('<center><h6><em>‘Every Route. Every Stop. One App.’</em></h6></center>',True)

        with col3: # n
            pass  

        st.markdown('---')

        from_route, to_route, bus_type, rating, fare = self.render_sidebar()
        self.fetch_filters(rating, fare, bus_type, from_route, to_route)
       
        if not self.df.empty: # Check all filters are maching datas
            st.title("Bus Booking System")
            self.filter_bd_point()
            self.booking_data()
     
        else: # if anything miss match
            logo = "No buses match the selected criteria."

            if logo == "No buses match the selected criteria.": # To Show image
                st.markdown( # Select Criteria to alin center
                    """
                        <center>
                            <h5>Select Criteria</h5>
                        </center>
                    """, True
                )
                col1, col2, col3 = st.columns([1, 1, 1])

                with col1: # Mt column
                    pass  
          
                with col2: # Error image column
                    st.image("SelecteCriteria.png", caption="No buses match the selected criteria.", width=250)
            
                with col3: # MT column
                    pass  

if __name__ == "__main__": # To run booking app
    app = BusBookingApp()
    app.run()
