import urllib.request
import datetime
import os
import xml.etree.ElementTree
import pandas as pd
import re
import numpy as np

def get_data_from_url(url):
    data = urllib.request.urlopen(url).read()
    return data.decode('utf-8')

def xmltree_to_dict2(raw_text, key=None):
    root = xml.etree.ElementTree.fromstring(raw_text)
    for c in root:
        d = {}
        for cc in c:
            if key is None:
                d = cc.attrib
            else:
                d[cc.attrib[key]] = cc.attrib
    return d

def get_production_server():
    url = 'http://api.pixelstarships.com/SettingService/GetLatestVersion2?languageKey=en'
    raw_text = get_data_from_url(url)
    d = xmltree_to_dict2(raw_text, key=None)
    return d['ProductionServer']

base_url = 'http://{}/'.format(get_production_server())

# ----- Item Designs --------------------------------------------------
def get_item_designs():
    url = base_url + 'ItemService/ListItemDesigns2?languageKey=en'
    data = urllib.request.urlopen(url).read()
    return data.decode()


def xmltext_to_df(raw_text):
    df = pd.DataFrame()
    root = xml.etree.ElementTree.fromstring(raw_text)
    for c in root:
        for cc in c:
            for i, ccc in enumerate(cc):
                df = df.append(pd.DataFrame(ccc.attrib, index=[i]))
    return df


# ----- Main ----------------------------------------------------------
if __name__ == "__main__":
    test = get_item_designs()
    df = xmltext_to_df(test)
    print(df)
    df.to_csv("data/pssitems.csv")