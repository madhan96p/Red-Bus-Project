# Busly - Redbus Data Scraping and Dynamic Filtering

**Busly**: Every Route. Every Stop. One App.  
Busly is an innovative bus travel platform designed to simplify the process of finding, filtering, and booking bus services. It combines the power of web scraping, dynamic filtering, and a user-friendly interface to provide a seamless experience for users.

---

## 🌟 **Features**
- Scrape bus routes and details from the Redbus website.
- Store and manage data using SQL databases.
- Dynamically display bus information with filters for routes, bus types, ratings, fares, and more.
- Real-time booking system with live updates to seat availability.

---

## 🛠️ **Tech Stack**
- **Python**
- **Selenium**
- **Pandas**
- **SQL (PhpMyAdmin)**
- **Streamlit**

---

## 🚀 **Key Highlights**
### **Data Scraping**
- Extracts bus route links and detailed information about bus operators, schedules, and pricing.
- Two main scripts: `Red_bus_scraper.py` and `Key_for_scrape.py` for efficient and error-logged scraping.
- Outputs saved in structured formats (Excel and CSV).

### **Database Management**
- Uses MySQL for storing scraped data.
- Avoids duplication with robust checks.
- Ensures clean data insertion using `bus_data_to_sql3.py`.

### **Streamlit Application**
- **Filters**: Search by routes, timings, bus types, ratings, and more.
- **Interactive Display**: Styled tables for easier data readability.
- **Booking Flow**: Real-time seat booking with confirmations.
- **User Interface**: Intuitive sidebar and main content display for smooth navigation.

---

## 📖 **How It Works**
1. **Scrape Data**:
   - Run the scraping scripts to collect and save data.
2. **Insert into SQL**:
   - Use `bus_data_to_sql3.py` to store data in a MySQL database.
3. **Launch the App**:
   - Open the `bus_booking_app4.py` Streamlit app to filter, view, and book buses.

---

## 📂 **Files and Directories**
- `Red_bus_scraper.py`: Script for scraping bus routes and details.
- `Key_for_scrape.py`: Manages the flow for scraping route links and bus data.
- `bus_data_to_sql3.py`: Handles MySQL database operations.
- `bus_booking_app4.py`: Streamlit application for the Busly platform.

---

## 📄 **Documentation**
Detailed documentation, including feature descriptions, script functionality, and database setup, is available in the [Redbus Scraper PDF](https://github.com/madhan96p/Red_bus_final/blob/main/Redbus_Scraper.pdf).

---

## 💡 **Getting Started**
1. Clone the repository:
   ```bash
   git clone https://github.com/madhan96p/Red_bus_final.git
   cd Red_bus_final
