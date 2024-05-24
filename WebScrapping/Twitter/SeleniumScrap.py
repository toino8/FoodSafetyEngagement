#region biblio
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException 
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from selenium.common.exceptions import TimeoutException
import time
import os
from selenium.common.exceptions import StaleElementReferenceException
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys
#endregion

browser = webdriver.Chrome()
browser.maximize_window()
browser.get("https://x.com/")
wait = WebDriverWait(browser,10)

#--------------------------------------------Connection-----------------------------------------------------
def connection(email, password, phone_number):
    # Wait until the accept cookies button is present and then click it
    wait.until(EC.presence_of_element_located((By.CLASS_NAME,"r-sdzlij")))
    accept_cookies = browser.find_element(By.CLASS_NAME, 'r-sdzlij')
    accept_cookies.click()

    # Wait until the sign in button is present and then click it
    wait.until(EC.presence_of_element_located((By.CLASS_NAME,"r-1phboty")))
    sign_in_button = browser.find_element(By.CLASS_NAME,"r-1phboty")
    sign_in_button.click()

    # Wait until the "Se connecter" button is present and then click it
    wait.until(EC.presence_of_element_located((By.XPATH,'//span[contains(text(), "Se connecter")]')))
    connect = browser.find_element(By.XPATH, '//span[contains(text(), "Se connecter")]')
    connect.click()

    # Wait until the email input is present and then enter the email
    wait.until(EC.presence_of_element_located((By.NAME, 'text')))
    email_input = browser.find_element(By.NAME, 'text')
    email_input.send_keys(email)

    # Wait until the "Suivant" button is present and then click it
    wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(., "Suivant")]')))
    next_button = browser.find_element(By.XPATH, '//button[contains(., "Suivant")]')
    next_button.click()

    # Check if phone number input is required and enter it
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="text"]')))
        input_element = browser.find_element(By.XPATH, '//input[@name="text"]')
        input_element.send_keys(phone_number)
         # Wait until the "Suivant" button is present and then click it again
        wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(., "Suivant")]')))
        next_button = browser.find_element(By.XPATH, '//button[contains(., "Suivant")]')
        next_button.click()
    except:
        pass

   

    # Wait until the password input is present and then enter the password
    wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="password"]')))
    password_input = browser.find_element(By.XPATH, '//input[@name="password"]')
    password_input.send_keys(password)

    # Wait until the "Se connecter" button is present and then click it to log in
    wait.until(EC.presence_of_element_located((By.XPATH,'//span[contains(text(), "Se connecter")]')))
    connect = browser.find_element(By.XPATH, '//span[contains(text(), "Se connecter")]')
    connect.click()
    
    time.sleep(5)
#---------------------------------------------------------------------------------------------------------------

#--------------------------------------------Search-----------------------------------------------------
def research(word):
    # Wait until the search input is present
    wait.until(EC.presence_of_element_located((By.XPATH, '//input[@data-testid="SearchBox_Search_Input"]')))
    search_input = browser.find_element(By.XPATH, '//input[@data-testid="SearchBox_Search_Input"]')
    
    # Ensure the search input is displayed by scrolling horizontally if needed
    while not search_input.is_displayed():
        ActionChains(browser).send_keys(Keys.ARROW_RIGHT).perform()

    # Enter the search term and press Enter
    search_input.send_keys(word)
    search_input.send_keys(Keys.ENTER)
    time.sleep(5)
#---------------------------------------------------------------------------------------------------------------

#--------------------------------------------Get Tweets-----------------------------------------------------
def get_tweets_and_dates(time_proceeding):
    start_time = time.time()

    # Initialiser la liste pour stocker les tweets
    tweets_data = []

    while True:
        # Récupérer la position du scroll avant le défilement
        last_height = browser.execute_script("return document.body.scrollHeight")

        # Sélectionner tous les éléments <div> qui contiennent les tweets
        tweet_containers = browser.find_elements(By.XPATH, '//div[@data-testid="cellInnerDiv"]')

        for container in tweet_containers:
            try:
                # Extraire les éléments de la div tweetText
                tweet_div = container.find_element(By.XPATH, './/div[@data-testid="tweetText"]')
                tweet_date = container.find_element(By.XPATH, './/time').get_attribute('datetime')
                
                
                tweet_spans = None
                while tweet_spans is None:
                    try:
                        tweet_spans = tweet_div.find_elements(By.XPATH, './/span')
                    except StaleElementReferenceException:
                        continue
                
                tweet_text_list = [span.text.strip().replace('\n','') for span in tweet_spans]
                tweet_text = ' '.join(tweet_text_list)
                
                tweets_data.append({'tweet': tweet_text, 'date': tweet_date})
                
            except NoSuchElementException:
                continue
            except StaleElementReferenceException:
                continue
      
      
        
        # Faire défiler la page vers le bas en petites étapes
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Attendre jusqu'à ce que de nouveaux éléments soient chargés
        time.sleep(2)  # Attendre un court délai pour que la page se charge

        # Récupérer la nouvelle position du scroll après le défilement
        new_height = browser.execute_script("return document.body.scrollHeight")
        
        
        # Vérifier si on a atteint la fin de la page ou si le temps imparti est écoulé
        if new_height == last_height or time.time() - start_time >= time_proceeding:
            break

    # Convertir la liste des données en DataFrame
    dataframe = pd.DataFrame(tweets_data)

    return dataframe



#---------------------------------------Save to csv--------------------------------------------------------
def save_to_csv(dataframe):
    dataframe.to_csv('tweets_data.csv', index=False)
#---------------------------------------------------------------------------------------------------------------


#-------------------------------------------General function----------------------------------------------------

def process_with_word(word):
    load_dotenv()
    email = os.getenv('EMAIL_ADDRESS')
    password = os.getenv('PASSWORD')
    phone_number = os.getenv('PHONE_NUMBER')

    connection(email, password, phone_number)
    research(word)
    dataframe=get_tweets_and_dates(30)
    save_to_csv(dataframe)
    browser.quit()

#---------------------------------------------------------------------------------------------------------------
process_with_word("climate change")
