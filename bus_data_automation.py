import pandas as pd  # Importing modules
import os
from redbus_project import Bus_links_scraper, BusDetails, Data_base, BusBookingApp
import logging
import subprocess

def links_scraper():
    """
    Scrape bus route links from the specified pages and save cleaned data.
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

    try:
        df = pd.read_excel('Bus_Data.xlsx')
        cleaned_data = df.drop_duplicates()
        cleaned_data.to_excel('Bus_Data_Cleaned.xlsx', index=False)
        print("Data cleaned and saved to Bus_Data_Cleaned.xlsx")
    except Exception as e:
        print(f"Error while cleaning or saving data: {e}")

def route_data_scraper():
    """
    Scrape detailed route data from the collected route links.
    """
    try:
        xlsx_path = 'Bus_Data_Cleaned.xlsx'
        scraped_links = pd.read_excel(xlsx_path)
        route_links = scraped_links['route_link'].tolist()

        scraper = BusDetails(route_links)
        scraper.scrape_route_details()
        scraper.save_results()
    except FileNotFoundError:
        print(f"Error: File {xlsx_path} not found. Please run the links scraper first.")
    except Exception as e:
        print(f"Error while scraping route data: {e}")

def insert_to_sql():
    """
    Insert bus data from a CSV file into the SQL database.
    """
    csv_file_path = 'Bus_Details.csv'
    
    if not os.path.exists(csv_file_path):
        print(f"Error: File not found at {csv_file_path}. Please scrape route data first.")
        return

    try:
        db_handler = Data_base(csv_file_path)
        db_handler.insert_data_from_csv(csv_file_path)
        db_handler.close_connection()
        print("Data successfully inserted into the SQL database.")
    except Exception as e:
        print(f"Error while inserting data into SQL: {e}")

def run_streamlit():
    """
    Run the Streamlit app using the proper Streamlit command.
    """
    try:
        print("Launching Streamlit app...")
        subprocess.run(["streamlit", "run", "redbus_project.py"], check=True)
    except Exception as e:
        print(f"Error occurred while running Streamlit app: {e}")


 
logging.getLogger("streamlit").setLevel(logging.ERROR)


def main():
    """
    Provide the user with options to scrape links, route data, insert data into SQL, or run Streamlit.
    """
    options = {
        "1": links_scraper,
        "2": route_data_scraper,
        "3": insert_to_sql,
        "4": run_streamlit 
    }

    print('1 - Scrape links\n2 - Scrape route data\n3 - Insert data into SQL\n4 - Run Streamlit app')
    choice = input("Enter your choice: ")
    
    if choice in options:
        try:
            options[choice]()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    else:
        print("Invalid choice. Please enter a valid option (1, 2, 3, or 4).")

if __name__ == "__main__":
    main()
