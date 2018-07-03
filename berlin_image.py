import csv
import os
import urllib.request
import os, errno
import requests
import csv
import eventlet
import random
import multiprocessing
import time
from bs4 import BeautifulSoup
from datetime import datetime
import math



eventlet.monkey_patch()

def berlin_scraper(url_range, increment, i):
    name = multiprocessing.current_process().name
    print("{}{}{}".format(url_range, increment, i))

    print('I am {} and I will wait {} seconds'.format(name, i))
    time.sleep(i)
    with open('berlin_publication_numbers.csv', 'r') as f:
        reader = csv.reader(f)
        your_list = list(reader)

    your_list = your_list[1::]
    mainlist = [link for link in your_list[url_range:url_range+increment:]]

    print("I am {} and I am working from page {} to page {}".format(name, url_range, url_range+increment))
    for link in mainlist:
        try:
            result = requests.get(link[0])
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

                with open("/Volumes/LaCie/Stamatov_python/Berlin_results/index.csv", 'a', encoding = 'utf-8') as myfile:
                    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                    wr.writerow([title, date, location])

                image = test.img['src']
                directory = "/Volumes/LaCie/Stamatov_python/Berlin_results/{}/{}/{}".format(location,title,date)

                try:
                    print('{}: working on {} in {} from  {}'.format(name, title, location, date))
                    os.makedirs(directory)

                except OSError as e:
                    if e.errno == errno.EEXIST:
                        print('{}: same article'.format(name))


                try:
                    with eventlet.Timeout(20):
                        urllib.request.urlretrieve(image, "/Volumes/LaCie/Stamatov_python/Berlin_results/{}/{}/{}/{}{}.jpg".format(location,title,date,title,page))
                except:
                    newspapernumber -= 1
                    os.remove('/Volumes/LaCie/Stamatov_python/Berlin_results/{}/{}/{}/{}{}.jpg".format(location,title,date,title,page)')
                    continue

                nextpage = soup.find('a', {'class': 'next'})

                while nextpage != None:
                    try:
                        page += 1
                        r = requests.get('http://zefys.staatsbibliothek-berlin.de/{}'.format(nextpage['href']))
                        html = r.text
                        soup = BeautifulSoup(html, 'html.parser')
                        test = soup.find('a', {'class' : 'imglink'})
                        image = test.img['src']
                        with eventlet.Timeout(20):
                            urllib.request.urlretrieve(image, "/Volumes/LaCie/Stamatov_python/Berlin_results/{}/{}/{}/{}{}.jpg".format(location,title,date,title,page))
                        nextpage = soup.find('a', {'class': 'next'})

                    except:
                        page -= 1
                        os.remove('/Volumes/LaCie/Stamatov_python/Berlin_results/{}/{}/{}/{}{}.jpg".format(location,title,date,title,page)')
                        continue


        except:
            for i in range(4):
                print('There was an error and I am just waiting it out')
                time.sleep(5)
            continue

if __name__ == "__main__":

    with open("/Volumes/LaCie/Stamatov_python/Berlin_results/index.csv", 'a', encoding = 'utf-8') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerow(['Publication', 'Date', 'Location'])

    slave_names = ["driver{}".format(i+1) for i in range(int(multiprocessing.cpu_count()*3/4))]

    with open('berlin_publication_numbers.csv', 'r') as f:
        reader = csv.reader(f)
        your_list = list(reader)

    pages = sum(1 for row in your_list)
    increment = math.ceil(pages / (multiprocessing.cpu_count()*3/4))
    print(increment)
    pool = multiprocessing.Pool()
    for i in range(int(multiprocessing.cpu_count()*3/4)):
        print('starting this whole thing up')
        url_range = increment * i
        new_process = multiprocessing.Process(name=slave_names[i], target=berlin_scraper, args = (url_range, increment, i))
        new_process.start()
    pool.close()
    pool.join()
