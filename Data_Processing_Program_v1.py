import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from datetime import datetime
import re
import logging
import os.path


def data_to_frame(html):
    # This part finds the dates and converts them to datetime
    soup = BeautifulSoup(html, 'lxml')
    x = soup.find(class_='stripes_list')
    x = x.find_all('div', attrs={'class': 'date show-hide-info'})

    dates = []
    for item in x:
        match_string = re.compile(r'([A-Z][a-z][a-z]).*[0-9].[AP]M')
        date = match_string.search(str(item)).group()
        dates.append(date.replace(".", "").replace(",", ""))


#    dates2 = []
#    for date in dates:
#        datetime_object = datetime.strptime(date, '%b %d %Y %I:%M %p')
#        dates2.append(datetime_object)

    dates2 = []
    for date in dates:
        try:
            datetime_object = datetime.strptime(date, '%b %d %Y %I:%M %p')
        except ValueError:
            datetime_object = datetime.strptime(date, '%a %b %d %I:%M %p')
            now = datetime.now()
            datetime_object = datetime_object.replace(year=now.year)
        dates2.append(datetime_object)



    # This part finds the article titles
    soup = BeautifulSoup(html, 'lxml')
    y = soup.find(class_='stripes_list')
    y = y.find_all('div', attrs={'class': 'content'})

    titles = []
    for item in y:
        title = item.find('a')
        titles.append(title.text)

    # This part finds the author name
    authors = []
    for item in x:
        author = item.find('a')
        if author != None:
            auth_name = author.text
            match_string = re.compile(r'[A-Z][^[A-Z]]?.*[a-z]')
            auth_name = match_string.search(str(auth_name))
            if auth_name != None: 
                authors.append(author.text)
            else:
                authors.append("")
        else:
            authors.append("")

    # Find tickers, company names, seperate them in two lists and make a list of lists
    comp = []

    for item in x:
        a = item.find('script')
        a = str(a)
        comp.append(re.findall(r"[^[]*\[([^]]*)\]", a))

    tickers = []
    comp_names = []

    for i in range(len(comp)):
        tick_art = comp[i][0]
        ticks = []
        tick_list = re.findall(r"(?<=')[^']+?(?=')", tick_art)
        for item in tick_list:
            if item == ',':
                continue
            else:
                ticks.append(item)
        tickers.append(ticks)

        comp_art = comp[i][1]
        comps = []
        comp_list = re.findall(r"(?<=')[^']+?(?=')", comp_art)
        for item in comp_list:
            if item == ',':
                continue
            else:
                comps.append(item)
        comp_names.append(comps)


    # This part finds the URLS
    urls = []
    for item in y:
        url = item.find('a')
        urls.append(url.get('href'))

    # Create dictionary and then dataframe  
    df = pd.DataFrame({'datetime': dates2, 'titles': titles, 'authors': authors, 'tickers': tickers, 
                       'companies': comp_names, 'urls': urls}, columns=['datetime','titles', 'authors', 
                                                                        'tickers', 'companies'])
    return df





logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')

now = datetime.now()
file_handler = logging.FileHandler('.\\Thesis_Data\\data_processing_{}.log'.format(now.strftime("%Y-%m-%d %H-%M-%S")))
file_handler.setFormatter(formatter)

# create a streamhandler to also display output on screen
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

logger.info("Data processing.........Program Started........\n")




    # loop over files 2 to 10

# loop over files 2 to 10
#import datetime

now = datetime.now()
logger.info("The program started at: {}".format(now.strftime("%Y-%m-%d %H:%M:%S")))

user_input = input("Start with file number: ")
user_input_2 = input("How many files to process: ") # the total amount of files to process
value_1 = int(user_input) + int(user_input_2)


# Check whether there is a master dataframe before creating one
if os.path.isfile(".//Thesis_Data//Master_Dataframe"):
    df_m = pd.read_csv(".//Thesis_Data//Master_Dataframe")
else:
    df_m = pd.DataFrame([])


for j in range(int(user_input), value_1):
    file = './/Thesis_Data//scrape{}.csv'.format(j)
    #if os.path.isfile(".//Thesis_Data//Master_Dataframe"): # if dataframe already exists the skip it but then nothing will append
    #    break 
    logger.info('Processing........... File: {}'.format(file))
    df = pd.read_csv(file, header=None, encoding='utf-8')

    df1 = pd.DataFrame([])
    a = 0
    b = 0
    for i in range(len(df[0])):
        html_data = df[0].iloc[i]
        # errors when parsing a source page
        try:
            df1 = df1.append(data_to_frame(html_data))
        except ValueError:
            # error trown because date could not be found
            a += 1
            logger.info('ValueError: {}'.format(a))
            continue
        except AttributeError:
            # error due to forbidden page
            b += 1
            logger.info('AttributeError: {}'.format(b))
            continue

    # format the dataframe - this resulted in error when appending to the master dataframe
    #df1.set_index('datetime', inplace=True)
    #df1 = df1.sort_index()

    # save to file
    df1.to_csv('./Thesis_Data/DataFrame_{}'.format(j), encoding='utf-8', index=False)
    df_m = df_m.append(df1)

df_m.to_csv('./Thesis_Data/Master_DataFrame_{}'.format(now.strftime("%Y-%m-%d %H-%M-%S")), encoding='utf-8', index=False)
    #df1 = pd.read_csv('./Thesis_Data/DataFrame_1', encoding='utf-8')

# remove duplicates, rows with no tickers or authors and save the files

#df_m = df_m.drop_duplicates()  # error found here - still needs to be resolved - drop_duplicates does not work with lists in dataframe
df_m.iloc[df_m.astype(str).drop_duplicates().index] # this still not working
df_m = df_m.replace('[]', np.nan)
df_m.dropna(how='any', inplace=True)

df_m.to_csv('./Thesis_Data/Master_DataFrame_clean_{}'.format(now.strftime("%Y-%m-%d %H-%M-%S")), encoding='utf-8', index=False)

now = datetime.now()
logger.info("The program ended at: {}".format(now.strftime("%Y-%m-%d %H:%M:%S")))
