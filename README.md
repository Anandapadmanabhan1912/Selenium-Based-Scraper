# Selenium-Based Scraper

A robust Selenium-based web scraper designed to extract questions, options, correct answers, and explanations from IndiaBix. This scraper supports automated pagination and batch processing from a list of URLs.

## Prerequisites

* **Python 3.x** installed on your system.
* **Google Chrome** browser installed.

## Setup Instructions

Follow these steps to set up your project in a virtual environment.

### 1. Clone or Navigate to the Project

Open your terminal (PowerShell or Command Prompt) and navigate to your project directory:

```powershell
cd D:\IndiaBixScraper\scraper
```

### 2. Create a Virtual Environment

Creating a virtual environment ensures that the dependencies for this project do not interfere with your global Python installation.

**On Windows:**

```powershell
# Create the virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\activate
```

*After activation, your terminal prompt should show `(venv)` at the beginning.*

### 3. Install Dependencies

Install the required libraries listed in your `requirements.txt` file:

```powershell
pip install -r requirements.txt
```

### 4. Prepare Your Input File

Ensure you have a file named `urls.txt` in the same directory as your script. Add the IndiaBix category URLs you wish to scrape, one per line:

```text
https://www.indiabix.com/aptitude/simple-interest/questions-and-answers/
https://www.indiabix.com/aptitude/problems-on-trains/
```

### 5. Running the Program

Once the environment is set up and your `urls.txt` is ready, execute the script:

```powershell
python scrapper.py
```

## Troubleshooting

* **Permission/Path Errors:** Ensure your terminal is running in the correct directory.
* **Driver Issues:** The script uses `webdriver-manager`, which automatically handles the ChromeDriver version for you. If you face issues, ensure you are connected to the internet on the first run so it can download the appropriate driver.
* **Timeout Errors:** If the script fails, it is usually because the website is temporarily blocking the requests. Ensure you have not removed the `time.sleep(2)` calls, as these prevent your IP from being rate-limited.
* **Missing `bs4` or `selenium`:** If you get a `ModuleNotFoundError` even after running the install command, verify that your virtual environment is still active (check for the `(venv)` prefix in your terminal prompt).

---

*Created for: IndiaBix Scraping Project*
