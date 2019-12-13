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
def request_market_data(currencyType, itemDesignId, rarity, itemSubType):
    url = base_url + f'MessageService/ListActiveMarketplaceMessages5?currencyType={currencyType}&itemDesignId={itemDesignId}&rarity={rarity}&itemSubType={itemSubType}'
    data = urllib.request.urlopen(url).read()
    return data

def pull_min_swaps():
    # Gather 497k swaps for both small mineral and gas crates
    df1 = xmltext_to_df(request_market_data('Mineral', '81', 'Common', 'MineralPack'))
    df1['Item'] = 'Small Mineral Crate'
    df2 = xmltext_to_df(request_market_data('Mineral', '84', 'Common', 'GasPack'))
    df2['Item'] = 'Small Gas Crate'
    df = pd.concat([df1, df2])

    # Clean up output
    df = df.loc[lambda df : df.ActivityArgument == 'mineral:497000']
    df = df[['UserName', 'Item', 'ActivityArgument']]
    df.rename(columns={'ActivityArgument': 'Cost'}, inplace=True)
    df = df.reset_index(drop=True)

    return df

# ----- Main ------
if __name__ == "__main__":
    df = pull_min_swaps()
    print(df)
