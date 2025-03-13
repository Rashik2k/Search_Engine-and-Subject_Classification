from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def setup_selenium():
    """Configure and initialize the Selenium WebDriver."""
    
    options = Options()
    
    # Run Chrome in headless mode (newer version)
    options.add_argument("--headless=new")  
    
    # Helps prevent detection as an automated bot
    options.add_argument("--disable-blink-features=AutomationControlled")  
    
    # Required for running in certain environments (e.g., Docker, Linux)
    options.add_argument("--no-sandbox")  
    options.add_argument("--disable-dev-shm-usage")  
    
    # Start Chrome maximized
    options.add_argument("start-maximized")  
    
    # Disable Chrome info bars
    options.add_argument("disable-infobars")  
    
    # Disable extensions for a clean environment
    options.add_argument("--disable-extensions")  
    
    # Spoof user-agent to mimic a real browser
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")  

    # Initialize the WebDriver with ChromeDriverManager handling installation
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    return driver
