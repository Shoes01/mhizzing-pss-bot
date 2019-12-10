import urllib.request
import xml.etree.ElementTree
import re
import pandas as pd

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

def xmltext_to_df(raw_text):
    df = pd.DataFrame()
    root = xml.etree.ElementTree.fromstring(raw_text)
    for c in root:
        for cc in c:
            for i, ccc in enumerate(cc):
                df = df.append(pd.DataFrame(ccc.attrib, index=[i]))
    return df

def get_production_server():
    url = 'http://api.pixelstarships.com/SettingService/GetLatestVersion2?languageKey=en'
    raw_text = get_data_from_url(url)
    d = xmltree_to_dict2(raw_text, key=None)
    return d['ProductionServer']

base_url = 'http://{}/'.format(get_production_server())

# ----- Get Market Data -----------------------------------
def request_market_data():
    url = base_url + 'MessageService/ListActiveMarketplaceMessages5?currencyType=Mineral&itemDesignId=81&rarity=Common&itemSubType=MineralPack'
    data = urllib.request.urlopen(url).read()
    return data

def pull_min_swaps():
    df = xmltext_to_df(request_market_data())
    filtered = df[df['ActivityArgument'] == 'mineral:497000']
    sliced = filtered[['UserName', 'ActivityArgument']]
    return sliced.to_string()

# ----- Main ------
if __name__ == "__main__":
    df = pull_min_swaps()
    sliced = df[['UserName', 'ActivityArgument']]
    print(sliced.to_string())

