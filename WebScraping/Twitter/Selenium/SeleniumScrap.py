import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
from translate import Translator
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.common.exceptions import TimeoutException 
from datetime import datetime
import random
import requests
import check_proxy
import json


import json

def remove_proxy_from_list(proxies, failed_proxy):
    proxies.remove(failed_proxy)
    with open('valid_proxies.txt', 'w') as f:
        for proxy in proxies:
            f.write("%s\n" % proxy)    
    return proxies



class TwitterScraper:
    def __init__(self,email,password,phone_number,time_proccedding,rotating_ip,ip_search):
        self.email = email
        self.password = password
        self.phone_number = phone_number
        self.time_proceeding =  time_proccedding
        self.browser = None
        self.proxies = None
        self.options = webdriver.ChromeOptions()
        self.rotating_ip = rotating_ip
        self.ip_search = ip_search
        if self.ip_search:
            check_proxy.main()
      
        # Open the file and read each line
        with open('valid_proxies.txt', 'r') as f:
            self.proxies = [line.strip() for line in f]



    def start_browser_with_proxy(self, timeout=15):
        # Convertir chaque chaîne en un dictionnaire
        proxy_info = random.choice(self.proxies)
       

        self.options.add_argument(f'--proxy-server={proxy_info}')
        print(f"Using proxy server at {proxy_info}")
        try:
            self.browser = webdriver.Chrome(options=self.options)
            self.browser.maximize_window()
            self.browser.get("https://x.com/")
            self.wait = WebDriverWait(self.browser, 10)
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "r-1phboty")))
        except TimeoutException:
            print("Le chargement de la page a pris trop de temps. Redémarrage du navigateur.")
            self.browser.quit()
            time.sleep(1)
            self.start_browser_with_proxy(timeout=timeout)
        except Exception as e:
            print(f"Erreur lors du chargement de la page : {e}")
            self.browser.quit()
            time.sleep(1)
            self.start_browser_with_proxy(timeout=timeout)
        
    def connection(self):
        while True:
            try:
                email = self.email
                password = self.password
                phone_number = self.phone_number
                if self.rotating_ip:
                    self.start_browser_with_proxy()
                else:
                    self.browser = webdriver.Chrome()
                    self.browser.maximize_window()
                    self.browser.get("https://x.com/")
                    self.wait = WebDriverWait(self.browser, 10)
                    
                self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "r-1phboty")))
                sign_in_button = self.browser.find_element(By.CLASS_NAME, "r-1phboty")
                sign_in_button.click()

                self.wait.until(EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "Se connecter")]')))
                connect = self.browser.find_element(By.XPATH, '//span[contains(text(), "Se connecter")]')
                connect.click()

                self.wait.until(EC.presence_of_element_located((By.NAME, 'text')))
                email_input = self.browser.find_element(By.NAME, 'text')
                email_input.send_keys(email)

                self.wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(., "Suivant")]')))
                next_button = self.browser.find_element(By.XPATH, '//button[contains(., "Suivant")]')
                next_button.click()

                try:
                    self.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="text"]')))
                    input_element = self.browser.find_element(By.XPATH, '//input[@name="text"]')
                    input_element.send_keys(phone_number)

                    self.wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(., "Suivant")]')))
                    next_button = self.browser.find_element(By.XPATH, '//button[contains(., "Suivant")]')
                    next_button.click()
                except:
                    pass

                self.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="password"]')))
                password_input = self.browser.find_element(By.XPATH, '//input[@name="password"]')
                password_input.send_keys(password)

                self.wait.until(EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "Se connecter")]')))
                connect = self.browser.find_element(By.XPATH, '//span[contains(text(), "Se connecter")]')
                connect.click()

                time.sleep(5)
                break
            except Exception as e:
                print(f"Erreur lors du processus de connexion : {e}")
                self.browser.quit()
                time.sleep(1)

       

        
    
    def request(self, word):
        try:
            self.connection()  # Effectue la connexion et toutes les interactions nécessaires
            self.research(word, 'en', 2024)  # Effectue la recherche avec le mot clé
            
            # Attendre que la page de résultats de recherche soit complètement chargée
          
            
            # Récupérer le contenu HTML de la page
            page_html = self.browser.page_source
            print(page_html)  # Affiche le HTML pour le débogage
            
            return page_html  # Retourne le contenu HTML
        except Exception as e:
            print(f"Erreur lors de la requête : {e}")
            return None



    def research(self, word, language, years):
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@data-testid="SearchBox_Search_Input"]')))
        search_input = self.browser.find_element(By.XPATH, '//input[@data-testid="SearchBox_Search_Input"]')

        while not search_input.is_displayed():
            ActionChains(self.browser).send_keys(Keys.ARROW_RIGHT).perform()

        search_input.send_keys(Keys.CONTROL + "a")
        
        if years == 2024:
            today_date = datetime.today().strftime('%Y-%m-%d')
            search_query = f"{word} lang:{language} until:{today_date} since:2024-01-01"
        else:
            start_date = f"{years}-01-01"
            end_date = f"{years}-12-31"
            search_query = f"{word} lang:{language} until:{end_date} since:{start_date}"
        
        search_input.send_keys(search_query)
        search_input.send_keys(Keys.RETURN)
        
    def convert_abbreviations(self,text):
            if 'k' in text.lower():
                return int(float(text.lower().replace('k', '')) * 1000)
            elif 'm' in text.lower():
                return int(float(text.lower().replace('m', '')) * 1000000)
            elif text == '':
                return None
            else:
                return int(text)
            
            
            
    def get_data(self, time_proceeding, language):
        start_time = time.time()
        tweets_data = []

        while True:
            last_height = self.browser.execute_script("return document.body.scrollHeight")
            tweet_containers = self.browser.find_elements(By.XPATH, '//div[@data-testid="cellInnerDiv"]')

            for container in tweet_containers:
                try:
                    tweet_div = container.find_element(By.XPATH, './/div[@data-testid="tweetText"]')
                    tweet_date = container.find_element(By.XPATH, './/time').get_attribute('datetime')
                    tweet_infos = container.find_elements(By.CSS_SELECTOR, '.css-175oi2r.r-xoduu5.r-1udh08x')
                    tweet_comments = self.convert_abbreviations(tweet_infos[0].text)
                    tweet_share = self.convert_abbreviations(tweet_infos[1].text)
                    tweet_likes = self.convert_abbreviations(tweet_infos[2].text)
                    tweet_views = self.convert_abbreviations(tweet_infos[3].text) if len(tweet_infos) == 4 else None
                    tweet_language = language

                    tweet_spans = None
                    while tweet_spans is None:
                        try:
                            tweet_spans = tweet_div.find_elements(By.XPATH, './/span')
                        except StaleElementReferenceException:
                            continue

                    tweet_text_list = [span.text.strip().replace('\n', '') for span in tweet_spans]
                    tweet_text = ' '.join(tweet_text_list)

                    tweets_data.append({'tweet': tweet_text, 'date': tweet_date, 'comments': tweet_comments, 'shares': tweet_share, 'likes': tweet_likes, 'views': tweet_views, 'language': tweet_language})

                except NoSuchElementException:
                    continue
                except StaleElementReferenceException:
                    continue

            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.browser.execute_script("return document.body.scrollHeight")

            if new_height == last_height or time.time() - start_time >= time_proceeding:
                break

        return pd.DataFrame(tweets_data)
    def save_to_csv(self, dataframe, file_path):
        
        # Vérifier si le fichier existe déjà
        if os.path.exists(file_path):
            # Ouvrir le fichier en mode append et sans réécrire les en-têtes
            dataframe.to_csv(file_path, mode='a', index=False, header=False, encoding='utf-8')
        else:
            # Créer un nouveau fichier avec les en-têtes
            dataframe.to_csv(file_path, mode='w', index=False, encoding='utf-8')
            
            
    def getComments(self, word, language,year):
            self.connection()
            self.research(word + " min_replies:300 min_faves:2000 min_retweets:2500", language,year)
            tweet_data = []

            self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="cellInnerDiv"]')))
            tweet_containers = self.browser.find_elements(By.XPATH, '//div[@data-testid="cellInnerDiv"]')

            for container in tweet_containers:
                try:
                    tweet_div = container.find_element(By.XPATH, './/div[@data-testid="tweetText"]')
                    tweet_date = container.find_element(By.XPATH, './/time').get_attribute('datetime')
                    tweet_infos = container.find_elements(By.CSS_SELECTOR, '.css-175oi2r.r-xoduu5.r-1udh08x')
                    tweet_comments = self.convert_abbreviations(tweet_infos[0].text)
                    tweet_share = self.convert_abbreviations(tweet_infos[1].text)
                    tweet_likes = self.convert_abbreviations(tweet_infos[2].text)
                    tweet_views = self.convert_abbreviations(tweet_infos[3].text) if len(tweet_infos) >= 4 else None

                    tweet_spans = None
                    while tweet_spans is None:
                        try:
                            tweet_spans = tweet_div.find_elements(By.XPATH, './/span')
                        except StaleElementReferenceException:
                            continue

                    tweet_text_list = [span.text.strip().replace('\n', '') for span in tweet_spans]
                    tweet_text = ' '.join(tweet_text_list)
                    
                    tweet_data.append({
                        'tweet': tweet_text,
                        'date': tweet_date,
                        'comments': tweet_comments,
                        'shares': tweet_share,
                        'likes': tweet_likes,
                        'views': tweet_views,
                        'language': language
                    })

                    print('Clicking on tweet container with text:', tweet_div.text)
                    self.wait.until(EC.element_to_be_clickable(tweet_div)).click()
                    time.sleep(2)

                    while True:
                        last_height_comments = self.browser.execute_script("return document.body.scrollHeight")
                        self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="cellInnerDiv"]')))
                        responses_containers = self.browser.find_elements(By.XPATH, '//div[@data-testid="cellInnerDiv"]')

                        for index, response in enumerate(responses_containers):
                            try:
                                response_div = response.find_element(By.XPATH, './/div[@data-testid="tweetText"]')
                                tweet_date = response.find_element(By.XPATH, './/time').get_attribute('datetime')

                                if index == 0:
                                    tweet_infos = response.find_elements(By.CSS_SELECTOR, '.css-175oi2r.r-xoduu5.r-1udh08x')
                                    print([tweet_info.text for tweet_info in tweet_infos])
                                    tweet_comments = self.convert_abbreviations(tweet_infos[1].text)
                                    tweet_share = self.convert_abbreviations(tweet_infos[2].text)
                                    tweet_likes = self.convert_abbreviations(tweet_infos[3].text)
                                    tweet_views = self.convert_abbreviations(tweet_infos[0].text.replace(",", ".")) if len(tweet_infos) >= 4 else None
                                    print(tweet_views)
                                else:
                                    print([tweet_info.text for tweet_info in tweet_infos])
                                    tweet_infos = response.find_elements(By.CSS_SELECTOR, '.css-175oi2r.r-xoduu5.r-1udh08x')
                                    tweet_comments = self.convert_abbreviations(tweet_infos[0].text)
                                    tweet_share = self.convert_abbreviations(tweet_infos[1].text)
                                    tweet_likes = self.convert_abbreviations(tweet_infos[2].text)
                                    tweet_views = self.convert_abbreviations(tweet_infos[3].text) if len(tweet_infos) >= 4 else None

                                
                                tweet_spans = None
                                while tweet_spans is None:
                                    try:
                                        tweet_spans = response_div.find_elements(By.XPATH, './/span')
                                    except StaleElementReferenceException:
                                        continue

                                tweet_text_list = [span.text.strip().replace('\n', '') for span in tweet_spans]
                                tweet_text = ' '.join(tweet_text_list)
                                
                                tweet_data.append({
                                    'tweet': tweet_text,
                                    'date': tweet_date,
                                    'comments': tweet_comments,
                                    'shares': tweet_share,
                                    'likes': tweet_likes,
                                    'views': tweet_views,
                                    'language': language
                                })

                                print('Response text:', response_div.text)
                            except NoSuchElementException:
                                print('Response element not found')
                                continue
                            except StaleElementReferenceException:
                                print('Stale response element reference')
                                continue

                        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)
                        new_height_comments = self.browser.execute_script("return document.body.scrollHeight")
                        if new_height_comments == last_height_comments:
                            try:
                                voir_plus_reponses_button = WebDriverWait(self.browser, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, "//button[@role='button' and .//span[text()='Voir plus de réponses']]"))
                                )
                                voir_plus_reponses_button.click()
                            except TimeoutException:
                                print("The button to load more responses was not found or not clickable.")
                                break

                            time.sleep(2)
                            new_height_comments = self.browser.execute_script("return document.body.scrollHeight")
                            if new_height_comments == last_height_comments:
                                break
                            last_height_comments = new_height_comments
                        else:
                            last_height_comments = new_height_comments

                except NoSuchElementException:
                    break
                except StaleElementReferenceException:
                    break

            self.save_to_csv(pd.DataFrame(tweet_data), 'comments_data.csv')
            self.browser.quit()

        
        
        
    def process_with_word(self, word, languages,years):

        
        self.connection()

        dataframes = []

        self.research(word, 'en',years)
        dataframes.append(self.get_data(self.time_proceeding/len(languages)+1, 'en'))

        for language in languages:
            print(f"Processing tweets in {language}...")
            translator = Translator(to_lang=language)
            word_translation = translator.translate(word)

            self.research(word, language,years)
            original_data = self.get_data(self.time_proceeding/len(languages)+1, language)

            self.research(word_translation, language,years)
            translated_data = self.get_data(self.time_proceeding/len(languages)+1, language)

            combined_data = pd.concat([original_data, translated_data], ignore_index=True)
            dataframes.append(combined_data)

        final_dataframe = pd.concat(dataframes, ignore_index=True)
        self.save_to_csv(final_dataframe,'tweets_data.csv')
        self.browser.quit()
        return final_dataframe
