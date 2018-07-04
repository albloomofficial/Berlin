import csv
import os
import urllib.request
import os, errno
import requests
import csv
import eventlet
import random
import multiprocessing
from multiprocessing import Pool, cpu_count
import time
from bs4 import BeautifulSoup
from datetime import datetime
import math


def berlin_scraper(row):
    name = f'driver{str(multiprocessing.current_process().name.split("-")[1])}'
    print('{}: I am actually working hehe'.format(name))

    result = requests.get(row)
    homepage = result.content
    soup = BeautifulSoup(homepage, "html.parser")
    newspapers = soup.find_all('div', {'class' : 'tx-zefyskalender-thumbnail'})
    newspaperpages = [thing.a['href'] for thing in newspapers]
    newspapernumber = 0
    for thing in newspaperpages:
        newspapernumber += 1
        time.sleep(2)
        page = 1
        r = requests.get('http://zefys.staatsbibliothek-berlin.de/{}'.format(thing))
        html = r.text
        soup = BeautifulSoup(html, 'html.parser')
        test = soup.find('a', {'class' : 'imglink'})

        newspaper_title = soup.find('div', {'id' : 'title'})
        meta_data = newspaper_title.text.split('\n')
        title = meta_data[1].strip().replace(' ', '_')
        location = meta_data[2].strip().replace(' ', '_')
        date = meta_data[3].strip().replace(' ', '_')

        print('I got this far!')

        with open("index_{}.csv".format(name), 'a', encoding = 'utf-8') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerow([title, date, location])

        image = test.img['src']
        directory = "Berlin_results/{}/{}/{}".format(location,title,date)

        try:
            print('{}: working on {} in {} from  {}'.format(name, title, location, date))
            os.makedirs(directory)

        except OSError as e:
            if e.errno == errno.EEXIST:
                print('{}: same article'.format(name))



            # with eventlet.Timeout(20):
        urllib.request.urlretrieve(image, "Berlin_results/{}/{}/{}/{}{}.jpg".format(location,title,date,title,page))


        nextpage = soup.find('a', {'class': 'next'})

        while nextpage != None:
            try:
                page += 1
                r = requests.get('http://zefys.staatsbibliothek-berlin.de/{}'.format(nextpage['href']))
                html = r.text
                soup = BeautifulSoup(html, 'html.parser')
                test = soup.find('a', {'class' : 'imglink'})
                image = test.img['src']
                # with eventlet.Timeout(20):
                urllib.request.urlretrieve(image, "Berlin_results/{}/{}/{}/{}{}.jpg".format(location,title,date,title,page))
                nextpage = soup.find('a', {'class': 'next'})
            except:
                pass





if __name__ == "__main__":
    for i in range(cpu_count()):
        with open("index_driver{}.csv".format(i+1), 'w', encoding = 'utf-8') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)

    with open('berlin_publication_merged.csv', 'r') as f:
        reader = csv.reader(f)
        list_of_pubs = list(reader)

    # pages = sum(1 for row in list_of_pubs)
    # increment = math.ceil(pages / (multiprocessing.cpu_count()*3/4))
    # print(increment)
    list_of_rows = [row[0] for row in list_of_pubs]
    print('created the list of rows')
    with Pool(cpu_count()) as p:
        p.map(berlin_scraper, list_of_rows , chunksize = 10)
    p.close()
    p.join()

    # pool = multiprocessing.Pool()
    # for i in range(int(multiprocessing.cpu_count()*3/4)):
    #     print('starting this whole thing up')
    #     url_range = increment * i
    #     new_process = multiprocessing.Process(name=driver_names[i], target=berlin_scraper, args = (url_range, increment, i))
    #     new_process.start()
    # pool.close()
    # pool.join()
