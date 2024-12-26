# Busly - Redbus Data Scraping and Dynamic Filtering  

## **Busly**: Every Route. Every Stop. One App.  
Busly simplifies bus travel by combining web scraping, dynamic filtering, and an intuitive interface for seamless booking.  

---

## 🌟 **Features**  
- Scrape bus routes and details from Redbus.  
- SQL database management for storing and querying data.  
- Dynamic filters for routes, bus types, ratings, fares, and more.  
- Real-time booking system with live seat availability.  

---

## 🛠️ **Tech Stack**  
- Python  
- Selenium  
- Pandas  
- SQL (PhpMyAdmin)  
- Streamlit  

---

## 🚀 **Highlights**  
1. **Data Scraping**:  
   - Extracts bus route links and operator details.  
   - Two scripts: `redbus_project.py` and `bus_data_automation.py`.  
   - Saves data as Excel/CSV with error handling.  

2. **Database Management**:  
   - MySQL for clean and deduplicated data storage.  
   - Managed via `bus_data_to_sql3.py`.  

3. **Streamlit Application**:  
   - Filters by routes, timings, ratings, fares, etc.  
   - Interactive table display for easy navigation.  
   - Real-time seat booking confirmation.  

---

## 📖 **Steps to Use**  
1. **Scrape Data**: Run `redbus_project.py` and `bus_data_automation.py`.  
2. **Insert Data**: Store in MySQL using `bus_data_to_sql3.py`.  
3. **Run App**: Launch `BusBookingApp.py` for filtering and booking.  

---

## 📂 **Key Files**  
- [`redbus_project.py`](https://github.com/madhan96p/Red_bus_final/blob/main/redbus_project.py): Scrapes route and bus details.  
- [`bus_data_automation.py`](https://github.com/madhan96p/Red_bus_final/blob/main/bus_data_automation.py): Handles scraping workflows.  
- [`bus_data_to_sql3.py`](https://github.com/madhan96p/Red_bus_final/blob/main/bus_data_to_sql3.py): MySQL operations script.  
- [`BusBookingApp.py`](https://github.com/madhan96p/Red_bus_final/blob/main/BusBookingApp.py): Streamlit app for Busly platform.  

---

**[Detailed Documentation Here](https://github.com/madhan96p/Red_bus_final/blob/main/Redbus_Scraper.pdf)**  
