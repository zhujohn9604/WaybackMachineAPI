from wayback import WaybackClient
import datetime
import pandas as pd
from dateutil import parser
from wayback import Mode
from bs4 import BeautifulSoup
from tqdm import tqdm

def get_Webs(row):

    
    if row.outcome == 1:
        from_date = parser.parse(row['Founded_Date'])
        to_date = parser.parse(row['endPeriod_Date'])
    else:
        from_date = parser.parse(row['Founded Date'])
        to_date = datetime.datetime(2022, 4, 1)

    client = WaybackClient()
    results = client.search(row.Website, matchType='prefix', from_date = from_date,
                            to_date = to_date)
    
    

    print(from_date)
    print(to_date)
    results = list(results)
    
    
    
    results = [i for i in results if not i.view_url.endswith(('.jpg', '.png', '.gif', '.txt', '.css', '.js', '.json', '.GIF', 
                                                          '.aspx', '.ico', '.webm', '.woff', '.mp3', '.mp4', '.svg',
                                                          '.woff2', '.pdf'))]
    results = [i for i in results if i.mime_type.startswith(('text', 'unk'))]
    results = [i for i in results if len(i.view_url) <= 200]
    
    temp_records = pd.DataFrame({
            'url': [record.url for record in results],
            'year': [record.timestamp.year for record in results],
            'month': [record.timestamp.month for record in results],
            'record': results
    })

    temp_records_sel = temp_records.groupby(['url', 'year']).last()

    records = temp_records_sel['record']

    #[i.view_url for i in results]

    #uni_inds = []
    contents = []
    for record in tqdm(records):
        try:
            response = client.get_memento(record, mode=Mode.original)
            content = response.content.decode()
            #uni_ind = sum([content.lower().count(word) for word in uni])
            clean_text = ' '.join(BeautifulSoup(content, "html.parser").stripped_strings)
            contents.append(clean_text)
            #uni_inds.append(uni_ind)
        except:
            contents.append(None)
    
    temp_records_sel['contents'] = contents
    temp_records_sel['view_url'] = [i.view_url for i in temp_records_sel.record]

    return temp_records_sel