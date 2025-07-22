# Karpel Downloader 
Automated Python script that downloads Karpel custom reports (only provides raw exports, does not perform any data cleaning)

# Set Up
1. Clone the repository to your local Git repo 

2. Create virtual environment
```bash
python -m venv <venv name>
source venv/bin/activate # MacOS / Linux
.\venv\Scripts\activate # Windows
```

3. Install required dependencies
```bash
pip install -r requirements.txt
playwright install # Additional command that downloads web browser drivers
```
    - Playwright is the main Python library that allows us to automate report downloads 
    - Python-dotenv is a local environment variable manager via .env file (see next steps)

4. From the `setup` folder, copy setup.env and save it in the main directory as an '.env' file. Then, edit the variables:
    - KARPEL_USERNAME
    - KARPEL_PASSWORD

5. Create a `KARPEL DOWNLOADS` folder in the main directory

6. You can now run download_karpel.py in your local venv and begin downloading custom reports from Karpel!
    - **download_karpel.py** *currently only downloads the following: (1) Received Cases, (2) Not Filed Cases, (3) Filed Cases, and (4) Disposed Cases*

## More about Web Automation 
Web automation is a powerful tool that allows for navigation of websites or web applications without the need for human input. Python libraries such as Selenium, Playwright, and Beautiful Soup offer powerful tools to conduct web automation. The shoot review workflow has been recently updated to use Playwright instead of Selenium. [Playwright](https://playwright.dev/python/docs/library) is a more modern Python web automation library that is popular for modern web apps, headless testing, and CI/CD pipelines. 

#### Advantages of Playwright over Selenium:
1. Simple setup - Selenium requires the separate installation of a WebDriver (depending on the web browser), whereas Playwright handles that for you.
```bash
pip install playwright  
playwright install
```
2. Faster execution - Playwright uses a persistent WebSocket connection instead of Selenium’s HTTP-based WebDriver, reducing latency and speeding up tests.
3. Implicit Waits - Playwright automatically waits for elements to be ready (visible, stable, etc.) before interacting—no need for explicit waits.
4. More concise API - Playwright utilizes a more intuitive and expressive syntax, especially for modern JavaScript/TypeScript workflows.

