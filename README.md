# Court Data Fetcher & Mini-Dashboard

This is a full-stack web application that fetches and displays case details from the Andhra Pradesh High Court e-Courts portal. The project demonstrates programmatic web scraping, data parsing, and storage in a relational database.

## Court Chosen

The backend is configured to scrape case information from the **Andhra Pradesh High Court**.

* **URL**: `[https://hcservices.ecourts.gov.in/ecourtindiaHC/](https://hcservices.ecourts.gov.in/ecourtindiaHC/index_highcourt.php?state_cd=2&dist_cd=1&stateNm=Andhra%20Pradesh)`

---

## Setup Steps

To run this project, you need to set up both the Python backend and the React frontend.

### 1. Backend Setup (Python/Flask)
1.  Navigate to the `backend` directory.
    ```bash
    cd backend
    ```
2.  Install the required Python packages.
    ```bash
    pip install -r requirements.txt
    ```
3.  Set up the MySQL database.
    * Ensure your MySQL server is running.
    * Create a `.env` file with your credentials (see the "Sample .env" section).
    * The `app.py` script will automatically create the necessary database and table on its first run.
4.  Run the Flask application.
    ```bash
    flask run
    ```

### 2. Frontend Setup (React)
1.  Navigate to the `frontend` directory.
    ```bash
    cd frontend
    ```
2.  Install Node.js dependencies.
    ```bash
    npm install
    ```
3.  Run the React application.
    ```bash
    npm start
    ```

---

## CAPTCHA Strategy

The e-Courts portal uses a CAPTCHA to prevent automated access. This application uses a manual strategy:
1.  The Python backend launches a Chrome browser window for the user.
2.  The user must **manually solve the CAPTCHA** in the browser and click "Go".
3.  Once the results page loads, the user signals the script to continue by pressing `Enter` in the backend terminal.
4.  The script then scrapes the data from the live page and sends it to the frontend.

---

## Sample `.env` File

Create a file named `.env` in your `backend` directory with your MySQL credentials. **Do not commit this file to your repository.**

```env
# MySQL Database Credentials
DB_HOST=localhost
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=court_data_db
