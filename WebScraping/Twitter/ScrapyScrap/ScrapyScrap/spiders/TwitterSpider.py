import scrapy
from scrapy import Spider
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from dotenv import load_dotenv
from scrapy.http import HtmlResponse
import os
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from w3lib.html import remove_tags

#Care to be in the folder ScrapyScrap ( the first ) and execute the file with the command:
# scrapy crawl twitter_spider -o tweets.json

load_dotenv()
email = os.getenv('EMAIL_ADDRESS')
password = os.getenv('PASSWORD')
phone_number = os.getenv('PHONE_NUMBER')

word = 'Python'
time_procceeding = 30


class TwitterSpider(Spider):
    name = 'twitter_spider'
    # allowed_domains = ["x.com"]
    start_urls = ['https://x.com/?lang=fr']

    def __init__(self, *args, **kwargs):
        super(TwitterSpider, self).__init__(*args, **kwargs)
        self.driver = webdriver.Chrome()  
        self.driver.maximize_window()
        
    def scroll_down(self):
        # Fonction pour simuler un défilement de la page
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # Faire défiler vers le bas
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Attendez que la page se charge

            # Calculer la nouvelle hauteur de la page et comparer avec la dernière hauteur
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def parse(self, response):
        start_time = time.time()
        self.driver.get(response.url)
        wait = WebDriverWait(self.driver, 10)

        # Accept cookies
        try:
            accept_cookies = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'r-sdzlij')))
            accept_cookies.click()
        except Exception as e:
            self.logger.info("No cookies to accept")


        # Wait until the "Se connecter" button is present and then click it
        wait.until(EC.presence_of_element_located((By.XPATH,'//span[contains(text(), "Se connecter")]')))
        connect = self.driver.find_element(By.XPATH, '//span[contains(text(), "Se connecter")]')
        connect.click()

        # Wait until the email/username input is present and then enter the email
        wait.until(EC.presence_of_element_located((By.NAME, 'text')))
        email_input = self.driver.find_element(By.NAME, 'text')
        email_input.send_keys(email)

        # Wait until the "Suivant" button is present and then click it
        wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(., "Suivant")]')))
        next_button = self.driver.find_element(By.XPATH, '//button[contains(., "Suivant")]')
        next_button.click()
    
      

        # Check if phone number input is required and enter it
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="text"]')))
            input_element = self.driver.find_element(By.XPATH, '//input[@name="text"]')
            input_element.send_keys(phone_number)
            # Wait until the "Suivant" button is present and then click it again
            wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(., "Suivant")]')))
            next_button = self.driver.find_element(By.XPATH, '//button[contains(., "Suivant")]')
            next_button.click()
            
        except Exception as e:
            self.logger.info("Phone number step not required")

       # Wait until the password input is present and then enter the password
        wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="password"]')))
        password_input = self.driver.find_element(By.XPATH, '//input[@name="password"]')
        password_input.send_keys(password)

        # Wait until the "Se connecter" button is present and then click it to log in
        wait.until(EC.presence_of_element_located((By.XPATH,'//span[contains(text(), "Se connecter")]')))
        connect = self.driver.find_element(By.XPATH, '//span[contains(text(), "Se connecter")]')
        connect.click()

        time.sleep(5)
        
        # Wait until the search input is present
        wait.until(EC.presence_of_element_located((By.XPATH, '//input[@data-testid="SearchBox_Search_Input"]')))
        search_input = self.driver.find_element(By.XPATH, '//input[@data-testid="SearchBox_Search_Input"]')
        
        # Ensure the search input is displayed by scrolling horizontally if needed
        while not search_input.is_displayed():
            ActionChains(self.driver).send_keys(Keys.ARROW_RIGHT).perform()

        # Enter the search term and press Enter
        search_input.send_keys(word)
        search_input.send_keys(Keys.ENTER)
        
        self.scroll_down()
        time.sleep(5)
        
        
        html = self.driver.page_source
        response_obj = HtmlResponse(url=self.driver.current_url, body=html, encoding='utf-8')
        tweets_data = []    
        tweet_containers = response_obj.xpath('//div[@data-testid="cellInnerDiv"]')

        while True:
            for container in tweet_containers:
                try:
                    tweet_divs = container.xpath('.//div[@data-testid="tweetText"]')
                    tweet_dates = container.xpath('.//time/@datetime').get()
                    
                    for tweet_div, tweet_date in zip(tweet_divs, tweet_dates):
                        tweet_spans = tweet_div.xpath('.//span')
                        tweet_text_list = [remove_tags(span.get()) for span in tweet_spans]
                        tweet_text = ' '.join(tweet_text_list).strip()
                        tweets_data.append({'tweet': tweet_text, 'date': tweet_date})

                        yield {
                            'tweet': tweet_text,
                            'date': tweet_date
                        }

                except Exception as e:
                    self.logger.error(f"Erreur lors de l'extraction du texte du tweet: {e}")
                
                if time.time() - start_time > 5:
                    break
            
            self.driver.quit()
