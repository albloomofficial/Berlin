import requests
import csv
import multiprocessing

from multiprocessing import cpu_count, Pool
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup

#Define a function to find all years on the Berlin database that have articles for them and store those years as a list
def get_list_years(start_date, end_date):
    #Start up Google Chrome and navigate to the calendar section of the database
    driver = webdriver.Chrome()
    driver.get('http://zefys.staatsbibliothek-berlin.de/index.php?id=kalender&no_cache=1&tx_zefyskalender_pi1%5Byy%5D=1785')

    #Retrieve the years and place them in a list
    yearlist = driver.find_element_by_xpath('//*[@id="tx-zefyskalender-yy"]').get_attribute('innerHTML')
    soup = BeautifulSoup(yearlist, 'html.parser')
    relevantyears = [x.text.strip() for x in soup.find_all('option') if (int(x.text) > start_date) and (int(x.text) < end_date)]
    comulativecount = 0

    #close Google Chrome
    driver.close()

    #Pass list of year to the environment so that we can work with it
    return relevantyears

#Define a function that retrieves the first page of a newspaper
#and then scrolls through it for more links

def link_scraper(year):
    sleep(1)
    name = f'driver {str(multiprocessing.current_process().name.split("-")[1])}'
    name = name.replace(' ','')

    page = requests.get('http://zefys.staatsbibliothek-berlin.de/index.php?id=kalender&no_cache=1&tx_zefyskalender_pi1%5Byy%5D={}'.format(year))
    html = page.text
    soup = BeautifulSoup(html, 'html.parser')
    daylinks = ["http://zefys.staatsbibliothek-berlin.de/{}".format(link.a.attrs['href']) for link in soup.find_all('td', {'class' :'tx-zefyskalender-daymarkiert'})]
    yearcom = 0
    comulativecount = 0

    for day in daylinks:
        r = requests.get(day)
        html = r.text
        soup = BeautifulSoup(html,'html.parser')

        newspapers = soup.find_all('div',{'class' : 'tx-zefyskalender-thumbnail'})

        comulativecount += len(newspapers)
        yearcom += len(newspapers)
        print('{}: Newspaper count: {}. Current year: {}'.format(name,comulativecount,year))

        with open("berlin_publication_numbers{}.csv".format(name),'a',
        encoding = 'utf-8') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerow([day,
            year,
            day.split('=')[-1],
            str(len(newspapers)),
            yearcom,
            comulativecount])
            myfile.close()

        sleep(1)

if __name__ == "__main__":
    #THIS IS WHERE YOU SET THE DATES
    start_date = 1779
    end_date = 1915

    #Pass the year range to the get_list_years() function
    year_list = get_list_years(start_date, end_date)

    #Create the csv files that we will store out index on
    for i in range(cpu_count()):
        with open("berlin_publication_numbersdriver{}.csv".format(str(i+1)),
        'w') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            myfile.close()

    #For every core the computer the script generate a woker
    #gives it a share of the work
    #waits for all of the to finish their shares
    #moves on to the next year

    with Pool(cpu_count()) as p:
        p.map(link_scraper, year_list, chunksize = 10)
    p.close()
    p.join()
