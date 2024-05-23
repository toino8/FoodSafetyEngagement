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
from pymongo import MongoClient
from selenium.webdriver.common.action_chains import ActionChains
#endregion


browser = webdriver.Chrome()
browser.get("https://www.flashscore.fr/")
wait = WebDriverWait(browser,10)
 
#--------------------------------------------Initialisation-----------------------------------------------------
def init_():
    #On accepte les cookies
    wait.until(EC.presence_of_element_located((By.ID,"onetrust-button-group")))
    acceptcookies=browser.find_element(By.ID,"onetrust-button-group")
    acceptcookies.click()

    time.sleep(1)
    
    # #On ferme tout ce qui est pop-up
    # wait.until(EC.presence_of_element_located((By.CLASS_NAME, "wizard__closeButton")))
    # popup1 = browser.find_element(By.CLASS_NAME, "wizard__closeButton")
    # popup1.click()
#---------------------------------------------------------------------------------------------------------------

def open_league_page(Nom_Ligue):
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'searchIcon')))
    search = browser.find_element(By.CLASS_NAME, 'searchIcon')
    search.click()
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'searchInput__input')))
    search_input = browser.find_element(By.CLASS_NAME, 'searchInput__input')
    search_input.send_keys(Nom_Ligue)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "searchResult")))
    ligue_name = browser.find_element(By.CLASS_NAME, "searchResult")
    ligue_name.click()
    return
 
def click_results_section():
    wait.until(EC.presence_of_element_located((By.ID, 'li2')))
    resultats_ligue = browser.find_element(By.ID, 'li2')
    resultats_ligue.click()
    clickable = True
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "event__participant--home")))
    while clickable:
        try:
            show_more = browser.find_element(By.PARTIAL_LINK_TEXT, "Montrer plus de matchs")
            browser.execute_script("arguments[0].scrollIntoView();", show_more)
            browser.execute_script("arguments[0].click();", show_more)
            wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div.loading-spinner')))  # Attendre que l'élément de chargement disparaisse
            time.sleep(3)
        except (NoSuchElementException, StaleElementReferenceException):
            clickable = False
    return

def get_calendrier():
    wait.until(EC.presence_of_element_located((By.ID, 'li3')))
    calendrier_ligue = browser.find_element(By.ID, 'li3')
    calendrier_ligue.click()
    soup=BeautifulSoup(browser.page_source, 'html.parser')
    home_teams = [home_team.text for home_team in soup.find_all(class_='event__participant--home')]
    away_teams = [away_team.text for away_team in soup.find_all(class_='event__participant--away')]
    times = [match_time.text for match_time in soup.find_all(class_='event__time')]
    return home_teams, away_teams, times

def click_classement_section():
    wait.until(EC.presence_of_element_located((By.ID, 'li4')))
    classement_ligue = browser.find_element(By.ID, 'li4')
    classement_ligue.click()
    

def check_match_ended():
    match_not_ended = 0
    html_content = browser.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    try:
        matches_not_played = soup.find_all(class_='event__match--scheduled')
    except NoSuchElementException:
        pass
    for _ in matches_not_played:
        match_not_ended += 1
    return match_not_ended 
            
def click_match(match):
    browser.execute_script("arguments[0].scrollIntoView();", match)
    browser.execute_script("arguments[0].click();", match)
    browser.switch_to.window(browser.window_handles[-1])
    
def return_to_matches():
    browser.close()
    browser.switch_to.window(browser.window_handles[0])

def process_match_data():
    teams_web = browser.find_elements(By.CLASS_NAME, "participant__overflow")
    score= browser.find_element(By.CLASS_NAME, "detailScore__wrapper")
    home_team =teams_web[0].text
    away_team =teams_web[2].text
    score = score.text.replace("-","").replace("\n","")
    home_score=int(score[0])
    away_score=int(score[1])
    
    wait.until(EC.presence_of_element_located((By.LINK_TEXT, "STATS")))
    stat = browser.find_element(By.LINK_TEXT, "STATS")
    stat.click()
    wait.until(EC.presence_of_element_located((By.CLASS_NAME,"_category_n1rcj_16")))
   
    try:
        Xpath_dangerous_stat = "//div[contains(@class, '_category_n1rcj_16') and .//strong[text()='Attaques dangereuses']]"
        Dangerous_stat = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, Xpath_dangerous_stat)))
        away_dangerous_attempts = Dangerous_stat.find_element(By.CLASS_NAME, '_awayValue_bwnrp_14')
        home_dangerous_attempts = Dangerous_stat.find_element(By.CLASS_NAME, '_homeValue_bwnrp_10')
    except TimeoutException:
        away_dangerous_attempts = None
        home_dangerous_attempts = None
    try:    
        Xpath_possession = "//div[contains(@class, '_category_n1rcj_16') and .//strong[text()='Possession de balle']]"
        possession_stat = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, Xpath_possession)))
        away_possession = int(possession_stat.find_element(By.CLASS_NAME, '_awayValue_bwnrp_14').text.strip('%'))
        home_possession = int(possession_stat.find_element(By.CLASS_NAME, '_homeValue_bwnrp_10').text.strip('%'))
    except TimeoutException:
        away_possession = None
        home_possession = None
    try:    
        Xpath_expected_goals = "//div[contains(@class, '_category_n1rcj_16') and .//strong[text()='Expected Goals (xG)']]"
        exp_goals_stat = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, Xpath_expected_goals)))
        away_exp_goals = float(exp_goals_stat.find_element(By.CLASS_NAME, '_awayValue_bwnrp_14').text)
        home_exp_goals = float(exp_goals_stat.find_element(By.CLASS_NAME, '_homeValue_bwnrp_10').text)
    except TimeoutException:
        away_exp_goals = None
        home_exp_goals = None
    try:    
        Xpath_on_target = "//div[contains(@class, '_category_n1rcj_16') and .//strong[text()='Tirs cadrés']]"
        on_target_stat = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, Xpath_on_target)))
        away_on_target = int(on_target_stat.find_element(By.CLASS_NAME, '_awayValue_bwnrp_14').text)
        home_on_target = int(on_target_stat.find_element(By.CLASS_NAME, '_homeValue_bwnrp_10').text)
    except TimeoutException:
        away_on_target = None
        home_on_target = None
    
    if away_dangerous_attempts is None:
        home_dangerous_attempts=(home_dangerous_attempts)
        away_dangerous_attempts=(away_dangerous_attempts)
    else:       
        home_dangerous_attempts=(int(home_dangerous_attempts.text))
        away_dangerous_attempts=(int(away_dangerous_attempts.text))
    return home_team, home_score, away_team, away_score,home_possession,away_possession,home_exp_goals,away_exp_goals,home_on_target,away_on_target,home_dangerous_attempts,away_dangerous_attempts 


def confrontations(home_team):
    home_team_vs = []
    score_vs=[]
    wait.until(EC.presence_of_element_located((By.LINK_TEXT, "tàt".upper())))
    Tat = browser.find_element(By.LINK_TEXT, "tàt".upper())
    browser.execute_script("arguments[0].click();", Tat)
    wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains   (@class, 'section__title') and text()='Confrontations']")))
    sections = browser.find_elements(By.CLASS_NAME, "h2h__section")
        
    for section in sections:
        section_title = section.find_element(By.CLASS_NAME,"section__title").text
        if section_title == "CONFRONTATIONS":
            confrontations_section = section
            break
        
    clickable = True
    while clickable:
        try:
            show_more = browser.find_element(By.CLASS_NAME, "showMore")
            show_more_text = section.find_element(By.CLASS_NAME,"showMore").text
            if show_more_text=="Montrer plus de matchs":
                browser.execute_script("arguments[0].scrollIntoView();", show_more)
                browser.execute_script("arguments[0].click();", show_more)
                wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div.loading-spinner')))  # Attendre que l'élément de chargement disparaisse
        except (NoSuchElementException, StaleElementReferenceException):
            clickable = False
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME,"h2h__row ")))
        confrontations_elements = confrontations_section.find_elements(By.CLASS_NAME, "h2h__row")
    except NoSuchElementException:
        pass
            
    confrontation=0
    for element in confrontations_elements:
        match_date = element.find_element(By.CLASS_NAME, "h2h__date")
        match_date_compar = datetime.strptime(match_date.text, "%d.%m.%y")
        date_compar = datetime.strptime("01.01.22", "%d.%m.%y")
        
        if match_date_compar > date_compar:
            home_team_name_web = element.find_element(By.CLASS_NAME,"h2h__homeParticipant").text
            score_vs_web = element.find_element(By.CLASS_NAME, "h2h__result").text
        
            home_team_vs.append(home_team_name_web)
            score_vs.append(score_vs_web)
            
            confrontation+=1

    separated_scores = []
    
    for score in score_vs:
        score_parts = score.split('\n')
        score_parts = [int(part) for part in score_parts]
        separated_scores.append(score_parts)

    
    home_ratio=0
    away_ratio=0
    nul_ratio=0
    
    for i in range(len(home_team_vs)):
        if separated_scores[i][0] > separated_scores[i][1]:
            if home_team_vs[i]==home_team:
                home_ratio+=1
            else:
                away_ratio+=1
                
        if separated_scores[i][0] < separated_scores[i][1]:     
            if home_team_vs[i]==home_team:
                away_ratio+=1
            else:
                home_ratio+=1 
        if separated_scores[i][0] == separated_scores[i][1]: 
            nul_ratio+=1
            continue
    vs_factor_home=home_ratio / (home_ratio + away_ratio + nul_ratio)
    vs_factor_away=home_ratio / (home_ratio + away_ratio + nul_ratio)
    return confrontation,[vs_factor_home,vs_factor_away]    

def process_data_mongoDB(match_data,confrontation,equipe):
    if match_data[0]==equipe or match_data[2]==equipe:
        match = {
        "opponent" : match_data[2] if match_data[0]==equipe else match_data[0],
        "home_score" : match_data[1],
        "away_score" : match_data[3],
        "home_possession" : match_data[4],
        "away_possession" : match_data[5],
        "home_on_target" : match_data[8],
        "away_on_target" : match_data[9],
        "home_exp_goals" : match_data[6],
        "away_exp_goals" : match_data[7],
        "home_dangerous_attempts" : match_data[10],
        "away_dangerous_attempts" : match_data[11],
        "confrontation" : confrontation[0],  
        "vs_factor" : confrontation[1][0] if match_data[0]==equipe else confrontation[1][1],
        "location" : "away" if match_data[2]==equipe else "home",
        "result" : "win" if match_data[1]>match_data[3] and match_data[0]==equipe or match_data[1]<match_data[3] and match_data[2]==equipe else "draw" if match_data[1]==match_data[3] else "lose",
        }
        return match
    return 0

def get_league_teams():
    wait.until(EC.presence_of_element_located((By.CLASS_NAME,"tableCellParticipant__name")))
    html_content = browser.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    teams = soup.find_all(class_='tableCellParticipant__name')
    team_names = [team.text for team in teams]
    teams_info = [[]]
    teams_ranking_infos = browser.find_elements(By.CLASS_NAME, "table__cell--value ")
    print("il y a ",len(teams_ranking_infos),"infos de classement")
    for num_info,info  in enumerate(teams_ranking_infos):
        print("info",num_info,info.text,len(teams_info[-1]))
        if (num_info in {0, 1, 2, 3, 6} or (num_info%7) in {0, 1, 2, 3, 6 }) and len(teams_info[-1])%5==0 and len(teams_info[-1])!=0:
            print("Taille Liste normalement egal à 5 ou multipe",len(teams_info[-1]))
            teams_info.append([])
            teams_info[-1].append(int(info.text))
            
        elif (num_info in {0, 1, 2, 3, 6} or (num_info%7) in {0, 1, 2, 3, 6 }):
            print("Taille Liste normalement pas egal à 5 ou multipe",len(teams_info[-1]))
            teams_info[-1].append(int(info.text))
    print("iciiiiiiiiiiiiiiiiiiiiii",teams_info)
    return team_names,teams_info


def check_DB_state(league):
    league=league.replace(".","")
    print(league)
    database_name = "PronosticData"
    db = connect_to_mongoDB(database_name)
    collection_name = "History"
    num_matches = 0
    collection = db[collection_name]
    for document in collection.find():
        num_matches += len(document.get(league, []))
    print("Number of matches in the database: ",league, int(num_matches/2))
    return int(num_matches/2)

def connect_to_mongoDB(database_name):
    client = MongoClient("mongodb+srv://theohinaut:tlAEFRvWBHeFW6cx@pronosticia.ie9dpby.mongodb.net/")
    db = client[database_name]
    return db

def check_DB(collection_name):
    db = connect_to_mongoDB('PronosticData')
    collection = db[collection_name]
    collection_id = collection.count_documents({})
    return collection_id

def save_to_mongoDB(League,country,match_data,confrontation,league_teams,home_teams,away_teams,times,db): 
    League = League.replace(".","")  
    collection_league = db[League.replace(" ", "").replace(".","") + 'DB']
    calendar_id = check_DB('Calendar')+1
    history_id = check_DB('History')+1
    collection_calendar = db['Calendar']
    collection_history = db['History']
    
    
    result_league=collection_league.update_one({"_id":"rank"+League}, {"$set": {"Ranking": []}})
        
    if result_league.modified_count == 0:
        collection_league.insert_one({"_id":"rank"+League,"Ranking":[]})
        
    for num_team in range(len(league_teams[0])):
        collection_league.update_one({"_id": "rank" + League}, {"$push": {"Ranking": {"team_name": league_teams[0][num_team], "played": league_teams[1][num_team][0], "wins": league_teams[1][num_team][1], "draws": league_teams[1][num_team][2], "loses": league_teams[1][num_team][3], "points": league_teams[1][num_team][4]}}})

    for team in league_teams[0]:  
        match=process_data_mongoDB(match_data,confrontation,team) 
        if match: 
            result = collection_history.update_one({"team_name": team},{"$push":{League:match}})
            if result.modified_count == 1:
                collection_calendar.update_one({"team_name": team}, {"$set": {League: []}})
                for home_team, away_team, match_time in zip(home_teams, away_teams, times):
                    if team == home_team or team == away_team:
                        collection_calendar.update_one({"team_name": team }, {"$push": {League: {"country": country,"home_team": home_team, "away_team": away_team,"date": match_time, "odds":[2,2,2],"oddChosen":1,"state":"Pending"}}})
            else:
                collection_history.insert_one({"_id": "history_" + str(history_id), "team_name": team, League:[match]})     
                collection_league.insert_one({"team_name": team,"logo": team + ".svg","history_id": "history_" + str(history_id),"calendar_id": "calendar_" + str(calendar_id),"championship": League})
                for home_team, away_team, match_time in zip(home_teams, away_teams, times):
                    if team == home_team or team == away_team:
                        try:
                            collection_calendar.insert_one({"_id": "calendar_"+str(calendar_id), "team_name": team, League: [{"country": country,"home_team": home_team, "away_team": away_team,"date": match_time, "odds":[2,2,2],"oddChosen":1,"state":"Pending"}]})
                            
                        except:
                            collection_calendar.update_one({"team_name": team}, {"$push": {League: {"country": country,"home_team": home_team, "away_team": away_team,"date": match_time, "odds":[2,2,2],"oddChosen":1,"state":"Pending"}}})   
                calendar_id += 1
                history_id += 1
    return
                   
def traitement_ligue(Nom_Ligue,country):
    database = "PronosticData"
    db = connect_to_mongoDB(database)
    open_league_page(Nom_Ligue)
    click_classement_section()
    league_teams=get_league_teams()
    home_teams, away_teams, times = get_calendrier()
    click_results_section()
    
    match_not_ended = check_match_ended()
    matchs_loaded = check_DB_state(Nom_Ligue)
    matchs = list(reversed(browser.find_elements(By.CLASS_NAME,'event__match')))
    matchs=matchs[matchs_loaded:len(matchs)-match_not_ended]
    
    for match in matchs:
        click_match(match)
        match_data=process_match_data()
        confrontation=confrontations(match_data[0])
        save_to_mongoDB(Nom_Ligue,country,match_data,confrontation,league_teams,home_teams,away_teams,times,db)
        return_to_matches()
        