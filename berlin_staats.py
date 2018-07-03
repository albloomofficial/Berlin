from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import requests
from time import sleep
import csv
from multiprocessing import cpu_count, Pool
import multiprocessing

def get_list_years(start_date, end_date):
    driver = webdriver.Chrome()
    driver.get('http://zefys.staatsbibliothek-berlin.de/index.php?id=kalender&no_cache=1&tx_zefyskalender_pi1%5Byy%5D=1785')

    yearlist = driver.find_element_by_xpath('//*[@id="tx-zefyskalender-yy"]').get_attribute('innerHTML')
    soup = BeautifulSoup(yearlist, 'html.parser')
    relevantyears = [x.text for x in soup.find_all('option') if (int(x.text) > start_date) and (int(x.text) < end_date)]
    comulativecount = 0
    return relevantyears

def the_other_part(year):
    name = f'driver {str(multiprocessing.current_process().name.split("-")[1])}'
    name = name.replace(' ','')
    driver = webdriver.Chrome()
    driver.get('http://zefys.staatsbibliothek-berlin.de/index.php?id=kalender&no_cache=1&tx_zefyskalender_pi1%5Byy%5D=1785')
    year = str(year)
    # try:
    select = Select(driver.find_element_by_xpath('//*[@id="tx-zefyskalender-yy"]'))
    select.select_by_visible_text(year)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    daylinks = ["http://zefys.staatsbibliothek-berlin.de/{}".format(link.a.attrs['href']) for link in soup.find_all('td', {'class' :'tx-zefyskalender-daymarkiert'})]
    yearcom = 0
    comulativecount = 0
    for thing in daylinks:
        r = requests.get(thing)
        html = r.text
        soup = BeautifulSoup(html,'html.parser')

        newspapers = soup.find_all('div',{'class' : 'tx-zefyskalender-thumbnail'})

        comulativecount += len(newspapers)
        yearcom += len(newspapers)
        print('{}:Newspaper count: {}. Current year: {}'.format(name,comulativecount,year))

        with open("berlin_publication_numbers{}.csv".format(name),'a',
        encoding = 'utf-8') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerow([thing,
            year,
            thing.split('=')[-1],
            str(len(newspapers)),
            yearcom,
            comulativecount])

        sleep(1)
        print('thing')
    driver.close()
    print('despacito')
    sleep(1)
    # except:
    #     driver.close()


if __name__ == "__main__":
    start_date = 1779
    end_date = 1915
    year_list = get_list_years(start_date, end_date)

    for i in range(cpu_count()):
        with open("berlin_publication_numbersdriver{}.csv".format(str(i+1)), 'w') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            myfile.close()

    print(year_list)

    with Pool(cpu_count()) as p:
        p.map(the_other_part, year_list)
    p.close()
    p.join()



    # with open("/Volumes/LaCie/Stamatov_python/Berlin_results/berlin_publication_numbers.csv", 'w', encoding = 'utf-8') as myfile:
    #     wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    #     wr.writerow(['link', 'year', 'date','number_of_pubs', 'yearly', 'comulativecount'])
    #     myfile.close()
