Court Data Fetcher & Mini-Dashboard
This project is a web application that fetches and displays case data from an Indian District eCourts portal.

Technologies Used
Frontend: React with Tailwind CSS

Backend: Python with Flask

Database: MySQL

Scraping: requests and BeautifulSoup to target a District eCourts portal on districts.ecourts.gov.in.

Court Targeted
This application is configured to scrape data from a generic District eCourts portal, which typically follow a similar structure. Specifically, it targets the "Case Status by Case Number" form. The scraping logic is built to handle the form submission and parse the resulting HTML for case details and order links.

CAPTCHA Strategy
The eCourts portals use CAPTCHA to prevent automated access. For this project, the backend is designed to receive a CAPTCHA solution, which for this demonstration is hardcoded as a placeholder.

In a real-world scenario, you would need to implement a strategy such as:

Manual Input: Prompting the user on the frontend to solve the CAPTCHA and submit the solution along with the case details.

Third-Party Solver: Integrating with a service (e.g., Anti-Captcha, 2Captcha) that uses OCR or human labor to solve CAPTCHAs programmatically.

Setup and Running the Project
1. Backend Setup
Navigate to the backend directory:

cd backend

Install Python dependencies:

pip install -r requirements.txt

Set up the MySQL Database:

Ensure you have a MySQL server running.

Create a .env file in the backend directory with your database credentials.

Example .env file:

DB_HOST=localhost
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=court_data_db

Run the Flask application:

flask run

2. Frontend Setup
Navigate to the frontend directory:

cd frontend

Install Node.js dependencies:

npm install

Run the React application:

npm start

3. Usage
Open your browser to http://localhost:3000.

Enter case details and a valid CAPTCHA solution (or for this example, simply use 1234 for the case number and let the backend assume success).

The application will display the fetched case details and log the query to your database.