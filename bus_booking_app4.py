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
    
        st.markdown( #visibility : hidden
            """ 
            <style>
                .stAppHeader.st-emotion-cache-h4xjwg.e10jh26i0 {
                    visibility : hidden;
                }
                .st-bt.st-cn.st-b6.st-co.st-cp, .st-emotion-cache-gi0tri.e121c1cl3 {
                    visibility : hidden;
                }
            </style>
        """, True)

    def distinct_filters(self): # Unique values
        """Fetch distinct values for From, To, and Bus Type dropdowns."""
       
        self.cursor.execute("SELECT DISTINCT SUBSTRING_INDEX(route_name, ' to ', 1) FROM buses")
        from_routes = [row[0] for row in self.cursor.fetchall()]

        self.cursor.execute("SELECT DISTINCT SUBSTRING_INDEX(route_name, ' to ', -1) FROM buses")
        to_routes = [row[0] for row in self.cursor.fetchall()]

        self.cursor.execute("SELECT DISTINCT bus_type FROM buses")
        bus_types = [row[0] for row in self.cursor.fetchall()]

        return from_routes, to_routes, bus_types

    def fetch_filters(self, rating, fare, bus_type, from_route, to_route): # Sidebar distinct bus details
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
                bus_type = %s AND
                SUBSTRING_INDEX(route_name, ' to ', 1) = %s AND
                SUBSTRING_INDEX(route_name, ' to ', -1) = %s
        """
      
        self.cursor.execute(query, (rating[0], rating[1], fare[0], fare[1], bus_type, from_route, to_route))
        data = self.cursor.fetchall()

        self.df = pd.DataFrame(data, columns=[ 
            "ID", "Route Name", "Route Link", "Bus Name", "Bus Type", "Departure Time", 
            "Boarding Point", "Duration", "Arrival Time", "Dropping Point", "Rating", 
            "Fare", "Seats Available", "Departure → Arrival"
        ])

    def render_sidebar(self): # sidebar User Input
        """Render sidebar and get filter inputs."""
        st.sidebar.header("Filters")
        from_routes, to_routes, bus_types = self.distinct_filters()

        from_route = st.sidebar.selectbox("Select Route (From)", from_routes)
        to_route = st.sidebar.selectbox("Select Route (To)", to_routes)
        bus_type = st.sidebar.selectbox("Select Bus Type", bus_types)
        rating = st.sidebar.slider("Select Rating", min_value=1.0, max_value=5.0, value=(1.0, 5.0))
        fare = st.sidebar.slider("Select Fare Range", min_value=0, max_value=10000, value=(0, 10000))

        return from_route, to_route, bus_type, rating, fare

    def filter_bd_point(self): # boarding & droping point filter inside page
        """Add dropdowns for Boarding Point and Dropping Point filtering."""
        col1, col2 = st.columns([1, 1])
        with col1:
            boarding_point = st.selectbox("Select Boarding Point", self.df["Boarding Point"].unique())
        with col2:
            dropping_point = st.selectbox("Select Dropping Point", self.df["Dropping Point"].unique())

        self.df = self.df[(self.df["Boarding Point"] == boarding_point) & (self.df["Dropping Point"] == dropping_point)]

    def booking_data(self): # display datas and booking
        """Display the filtered DataFrame and booking options."""
        self.df["Departure → Arrival"] = self.df["Boarding Point"] + " → " + self.df["Dropping Point"]
        filtered_df = self.df[[ 
            "ID", "Route Name", "Departure → Arrival", "Bus Name", "Bus Type", "Departure Time",
            "Duration", "Arrival Time", "Rating", "Fare", "Seats Available"
        ]]

        if not filtered_df.empty:
            st.subheader("Available Buses")
            st.dataframe(filtered_df.style.format({"Fare": "₹{:,.2f}"}), hide_index=True)

            col1, col2 = st.columns([1, 1])
            with col2:
                available_ids = filtered_df["ID"].tolist()
                selected_id = st.selectbox("Select Bus ID to Book", available_ids, key="bus_id_select")

                if st.button("Confirm Booking"):
                    self.book_bus(selected_id)

            with col1:
                st.subheader("Confirm Booking Details")
                selected_bus = filtered_df[filtered_df['ID'] == selected_id].iloc[0]
                self.dp_bus_details(selected_bus)
        else:
            st.warning("No buses available for the selected filter.")

    def book_bus(self, bus_id): # BOok Bus by choosing bus id
        """Update the seats for a selected bus."""
        try: # Seats will reduse and save permnt
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

    def dp_bus_details(self, selected_bus): # displaying selected bus
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
        st.title("Bus Booking System")

        from_route, to_route, bus_type, rating, fare = self.render_sidebar()
        self.fetch_filters(rating, fare, bus_type, from_route, to_route)
        if not self.df.empty:
            self.filter_bd_point()
            self.booking_data()
        else:
            st.warning("No buses match the selected criteria.")

if __name__ == "__main__":
    app = BusBookingApp()
    app.run()
