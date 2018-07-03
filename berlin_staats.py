from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import requests
import time
import csv

with open("/Volumes/LaCie/Stamatov_python/Berlin_results/berlin_publication_numbers.csv", 'a', encoding = 'utf-8') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(['link', 'year', 'date','number_of_pubs', 'yearly', 'comulativecount'])

driver = webdriver.Chrome()
driver.get('http://zefys.staatsbibliothek-berlin.de/index.php?id=kalender&no_cache=1&tx_zefyskalender_pi1%5Byy%5D=1785')

yearlist = driver.find_element_by_xpath('//*[@id="tx-zefyskalender-yy"]').get_attribute('innerHTML')
soup = BeautifulSoup(yearlist, 'html.parser')
relevantyears = [x.text for x in soup.find_all('option') if (int(x.text) > 1779) and (int(x.text) < 1915)]
comulativecount = 0

for year in relevantyears:

    try:
        select = Select(driver.find_element_by_xpath('//*[@id="tx-zefyskalender-yy"]'))
        select.select_by_visible_text(year)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        daylinks = ["http://zefys.staatsbibliothek-berlin.de/{}".format(link.a.attrs['href']) for link in soup.find_all('td', {'class' :'tx-zefyskalender-daymarkiert'})]
        yearcom = 0
        for thing in daylinks:
            r = requests.get(thing)
            html = r.text
            soup = BeautifulSoup(html, 'html.parser')
            newspapers = soup.find_all('div', {'class' : 'tx-zefyskalender-thumbnail'})
            comulativecount += len(newspapers)
            yearcom += len(newspapers)
            print('I have found {} newspapers so far. I am also on year {}'.format(comulativecount, year))

            with open("/Volumes/LaCie/Stamatov_python/Berlin_results/berlin_publication_numbers.csv", 'a', encoding = 'utf-8') as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                wr.writerow([thing, year, thing.split('=')[-1], str(len(newspapers)), yearcom, comulativecount])

            time.sleep(1)
    except:
        driver.close()
        time.sleep(60*30)
        driver = webdriver.Chrome()
        driver.get('http://zefys.staatsbibliothek-berlin.de/index.php?id=kalender&no_cache=1&tx_zefyskalender_pi1%5Byy%5D=1785')
        select = Select(driver.find_element_by_xpath('//*[@id="tx-zefyskalender-yy"]'))
        select.select_by_visible_text(year)
        continue
