# app.py - Python Flask Backend (Final, Robust Version)

from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os
import json
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_NAME = os.getenv('DB_NAME', 'court_data_db')

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        if conn.is_connected():
            print(f"Connected to MySQL database: {DB_NAME}")
            return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_db():
    try:
        conn_no_db = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor_no_db = conn_no_db.cursor()
        cursor_no_db.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        conn_no_db.close()

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS queries (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    query_data JSON NOT NULL,
                    raw_response TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            conn.close()
    except Error as e:
        print(f"Error during database initialization: {e}")

init_db()

def log_query(query_data, raw_response):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query_data_str = json.dumps(query_data)
            query = """
                INSERT INTO queries (query_data, raw_response)
                VALUES (%s, %s)
            """
            cursor.execute(query, (query_data_str, raw_response))
            conn.commit()
        except Error as e:
            print(f"Error logging query to database: {e}")
        finally:
            conn.close()

def scrape_ap_high_court(case_type, case_number, filing_year):
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get("https://hcservices.ecourts.gov.in/ecourtindiaHC/cases/case_no.php?state_cd=2&dist_cd=1&court_code=1&stateNm=Andhra%20Pradesh")
        
        wait = WebDriverWait(driver, 10)
        
        case_type_select = Select(wait.until(EC.presence_of_element_located((By.ID, "case_type"))))
        
        case_type_map = {
            'Criminal Appeal': '19',
            'Civil Suit': '24',
            'Writ Petition': '63'
        }
        case_type_value = case_type_map.get(case_type, '19')
        case_type_select.select_by_value(case_type_value)
        
        case_number_input = driver.find_element(By.ID, "search_case_no")
        case_number_input.send_keys(case_number)
        
        filing_year_input = driver.find_element(By.ID, "rgyear")
        filing_year_input.send_keys(filing_year)

        print("\n--- ATTENTION: CAPTCHA REQUIRED ---")
        print("A browser window has opened. Please solve the CAPTCHA on the webpage.")
        print("After solving the CAPTCHA and clicking 'Go', press Enter in this terminal to continue...")
        
        input("Press Enter to continue scraping...")
        
        try:
            wait = WebDriverWait(driver, 20)
            wait.until(EC.presence_of_element_located((By.ID, "showList")))
        except TimeoutException:
             driver.quit()
             return {'success': False, 'message': 'Scraping failed: Results table not found or page took too long to load.'}

        # FIX: NEW SELECTORS based on the provided HTML
        
        # Extract Parties and Advocate
        parties = "N/A"
        try:
            petitioner_advocate_span = driver.find_element(By.XPATH, "//span[@class='Petitioner_Advocate_table']")
            respondent_advocate_span = driver.find_element(By.XPATH, "//span[@class='Respondent_Advocate_table']")
            petitioner_name = petitioner_advocate_span.text.split("\n")[0].strip()
            respondent_name = respondent_advocate_span.text.split("\n")[0].strip()
            parties = f"{petitioner_name} vs. {respondent_name}"
        except (NoSuchElementException, IndexError):
            pass

        # Extract Filing Date from the 'Case Details' div
        filing_date = "N/A"
        try:
            filing_date_element = driver.find_element(By.XPATH, "//span[contains(., 'Filing Date') and contains(@style, 'text-align:left')]")
            filing_date = filing_date_element.text.split(':')[-1].strip()
        except NoSuchElementException:
            pass

        # Extract Next Hearing Date from the 'Case Status' div
        next_hearing_date = "N/A"
        try:
            next_hearing_element = driver.find_element(By.XPATH, "//strong[contains(text(), 'Next Hearing Date')]")
            next_hearing_date = next_hearing_element.find_element(By.XPATH, "./following-sibling::strong").text.strip()
        except NoSuchElementException:
            pass
        
        # Extract Order PDF links
        order_links = []
        try:
            orders_table = driver.find_element(By.XPATH, "//table[@class='order_table']")
            order_elements = orders_table.find_elements(By.TAG_NAME, "a")
            for link in order_elements:
                order_date_cell = link.find_element(By.XPATH, "./ancestor::tr/td[4]")
                order_links.append({
                    'date': order_date_cell.text.strip(),
                    'link': link.get_attribute('href')
                })
        except NoSuchElementException:
            pass
        
        raw_html = driver.page_source
        driver.quit()
        
        return {
            'success': True,
            'parties': parties,
            'filingDate': filing_date,
            'nextHearingDate': next_hearing_date,
            'orders': order_links,
            'raw_response': raw_html
        }

    except Exception as e:
        print(f"An unhandled error occurred during scraping: {e}")
        if driver:
            driver.quit()
        return {'success': False, 'message': f'Scraping failed: {e}'}

@app.route('/api/fetch_case_data', methods=['POST'])
def fetch_case_data():
    try:
        data = request.get_json()
        case_type = data.get('caseType')
        case_number = data.get('caseNumber')
        filing_year = data.get('filingYear')

        if not all([case_type, case_number, filing_year]):
            return jsonify({'success': False, 'message': 'Missing form data.'}), 400

        scrape_result = scrape_ap_high_court(case_type, case_number, filing_year)
        
        log_query(data, scrape_result.get('raw_response', ''))
        
        if scrape_result['success']:
            return jsonify({
                'success': True,
                'parties': scrape_result['parties'],
                'filingDate': scrape_result['filingDate'],
                'nextHearingDate': scrape_result['nextHearingDate'],
                'orders': scrape_result['orders']
            })
        else:
            return jsonify({'success': False, 'message': scrape_result['message']}), 404
            
    except Exception as e:
        print(f"An unhandled error occurred in fetch_case_data: {e}")
        return jsonify({'success': False, 'message': 'Internal server error.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
