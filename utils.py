import sqlite3
import os
from sqlite3.dbapi2 import connect 
from urllib.parse import parse_qs, parse_qsl, unquote, urlparse
import csv

HISTORY_PATH = os.path.join(os.getenv('USERPROFILE'),r'AppData\Local\Google\Chrome\User Data\Default\History')
#print(HISTORY_PATH)

SPLIT_CH = ' '

def table_info(table_name):
    return "PRAGMA table_info({})".format(table_name)

def show_query_results(cur,rows,table_name):
    csvrows = [[r[1] for r in cur.execute(table_info(table_name))]]
    for row in rows:
        csvrows.append([str(_) for _ in row])
    #print(csvrows)
    return csvrows

def url_query_decode(query):
    return parse_qsl(unquote(query))

def get_search_records(cursor):
    urls_query_results = cursor.execute("select * from urls order by last_visit_time").fetchall()
    csv_rows = show_query_results(cursor,urls_query_results,"urls")
    #print(csv_str)
    with open("record.csv",'w') as f:
        csv_writer=csv.writer(f)
        csv_writer.writerows(csv_rows)

def get_search_keywords(cursor):
    urls_query_results = cursor.execute("select url from urls").fetchall()
    keywords = dict()
    for url_row in urls_query_results:
        # url_row is a tuble with length=1
        # parse and decode url query
        url_parse = urlparse(url_row[0])
        if url_parse.netloc != 'www.baidu.com':
            continue
        query_parse = url_query_decode(url_parse.query)
        for each in query_parse:
            #print(each)
            if each[0] =='wd':
                for word in each[1].split(SPLIT_CH):
                    if word in keywords:
                        keywords[word] += 1
                    else:
                        keywords[word] = 1
    items = list(keywords.items())    
    items = sorted(items,key=lambda x:x[1],reverse=True)
    with open("./keywords.csv","w") as f:
        writer = csv.writer(f)
        writer.writerow(('Keyword','frequency'))
        writer.writerows(items)

def main():
    assert(os.path.isfile(HISTORY_PATH))
    connection = sqlite3.connect(HISTORY_PATH)
    cursor = connection.cursor()
    get_search_keywords(cursor)
    get_search_records(cursor)

if __name__=='__main__':
    main()