import pandas as pd #importing modules
import subprocess
from redbus_project1_2 import Bus_links_scraper, BusDetails, Data_base_handler, BusBookingApp

def links_scraper(): # Scrape bus route links
    """
    Scrape bus route links from the specified pages.
    """
    links_to_scrape = [
        'https://www.redbus.in/online-booking/apsrtc/?utm_source=rtchometile',
        'https://www.redbus.in/online-booking/tsrtc/?utm_source=rtchometile', 
        'https://www.redbus.in/online-booking/ksrtc-kerala/?utm_source=rtchometile', 
        'https://www.redbus.in/online-booking/rsrtc/?utm_source=rtchometile', 
        'https://www.redbus.in/online-booking/west-bengal-transport-corporation?utm_source=rtchometile', 
        'https://www.redbus.in/travels/nbstc', 
        'https://www.redbus.in/online-booking/south-bengal-state-transport-corporation-sbstc', 
        'https://www.redbus.in/online-booking/gsrtce', 
        'https://www.redbus.in/online-booking/uttar-pradesh-state-road-transport-corporation-upsrtc', 
        'https://www.redbus.in/online-booking/astc',
    ]

    scraper = Bus_links_scraper(links_to_scrape)
    scraper.scrape_all()
    scraper.save_results()

    df = pd.read_excel('Bus_Data.xlsx')
    cleanedBD = df.drop_duplicates()
    cleanedBD.to_excel('Bus_Data_Cleaned.xlsx', index=False)
    print("Data cleaned and saved to Bus_Data_Cleaned.xlsx")

def route_data_scraper(): # Scrape route detail
    """
    Scrape detailed route data from the collected route links.
    """

    xlsx_path = 'Bus_Data_Cleaned.xlsx'
    scraped_links = pd.read_excel(xlsx_path)
    route_links = scraped_links['route_link'].tolist()
#     route_links = ['https://www.redbus.in/bus-tickets/dergaon-to-dibrugarh',
#                    'https://www.redbus.in/bus-tickets/gohpur-to-guwahati'
#                   ]
   
    scraper = BusDetails(route_links)
    scraper.scrape_route_details()
    scraper.save_results()

def insert_to_Sql(): # insert datas into sql

    csv_file_path = 'Bus_Details.csv'
    db_handler = Data_base_handler(csv_file_path)
    db_handler.insert_data_from_csv(csv_file_path)
    db_handler.close_connection()
 
def run_streamlit(): # To Run Streamlit
    """
    Run the Streamlit app.
    """
    try:
        print("Running BusBookingApp...")
        app = BusBookingApp() 
        app.run()  

        print("Running Streamlit app...")
        subprocess.run(["streamlit", "run", "redbus_project.py"], check= True)

    except Exception as e:
        print(f"Error occurred while running Streamlit: {e}")

def main(): # To run any one of this 4 def 
    """
    Provide the user with options to scrape links, route data, insert data into SQL, or run Streamlit.
    """
    options = {
        "1": links_scraper,
        "2": route_data_scraper
        # "3": insert_to_Sql,
        # "4": run_streamlit 
    }

    print('1 - Scrape links\n2 - Scrape data') #\n3 - Insert data into SQL\n4 - Run Streamlit app')
    choice = input("Enter your choice: ")
    
    if choice in options: # To call function with selected option
        options[choice]()
  
    else: # user chooise to chose code to run

        ''' And in hear this (2 and 3) class is not working in .py file, So
        am chaged some code after i splited code file... if needed view [bus_data_to_sql3.py and
          bus_booking_app4.py] files''' 
        
        print("Invalid choice. Please enter a valid option (1, 2).") #, 3, or 4).")

if __name__ == "__main__":
    main()
