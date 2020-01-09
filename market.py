import urllib.request
import xml.etree.ElementTree
import re
import pandas as pd

# ----- Helper Functions ----------------------------------

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

# ----- End Helper Functions ------------------------------


# ----- Setup ---------------------------------------------

base_url = 'http://{}/'.format(get_production_server())
equip_subtypes = ['EquipmentAccessory', 'EquipmentBody', 'EquipmentHead', 'EquipmentLeg', 'EquipmentPet', 'EquipmentWeapon']

# ----- End Setup -----------------------------------------


# ----- Market Functions ----------------------------------
def request_market_data5(currencyType, itemDesignId, rarity, itemSubType):
    url = base_url + f'MessageService/ListActiveMarketplaceMessages5?currencyType={currencyType}&itemDesignId={itemDesignId}&rarity={rarity}&itemSubType={itemSubType}'
    data = urllib.request.urlopen(url).read()
    return data

def request_market_data2(itemSubType, rarity):
    url = base_url + f'MessageService/ListActiveMarketplaceMessages2?itemSubType={itemSubType}&rarity={rarity}'
    data = urllib.request.urlopen(url).read()
    return data

def pull_min_swaps():
    # Gather 497k swaps for both small mineral and gas crates
    df1 = xmltext_to_df(request_market_data5('Mineral', '81', 'Common', 'MineralPack'))
    df1['Item'] = 'Small Mineral Crate'
    df2 = xmltext_to_df(request_market_data5('Mineral', '84', 'Common', 'GasPack'))
    df2['Item'] = 'Small Gas Crate'
    df = pd.concat([df1, df2])

    # Clean up output
    df = df.loc[lambda df : df.ActivityArgument == 'mineral:497000']
    df = df[['UserName', 'Item', 'ActivityArgument']]
    df.rename(columns={'ActivityArgument': 'Cost'}, inplace=True)
    df = df.reset_index(drop=True)

    return df

def pull_rarity(rarity):
    # Acquire data and arrange in dataframe
    df_list = []
    for subtype in equip_subtypes:
        df_list.append(xmltext_to_df(request_market_data2(subtype, rarity)))
    big_df = pd.concat(df_list)
    big_df = big_df[['Message', 'ActivityArgument']].reset_index()
    split_cols = pd.DataFrame(big_df.ActivityArgument.str.split(':', 1).tolist(), columns=['Currency', 'Price'])
    split_cols['Price'] = pd.to_numeric(split_cols['Price'])

    final_df = pd.concat([big_df['Message'], split_cols], axis=1)

    # Sort data to get cheapest items
    cheap_bux_items = final_df[final_df.Currency == 'starbux'].sort_values(by=['Price'])[:5]
    all_items = pd.concat([cheap_bux_items, final_df[final_df.Currency == 'minerals'], final_df[final_df.Currency == 'gas']])
    return all_items

# ----- Main ------
if __name__ == "__main__":
    df1 = pull_rarity('Unique')
    print(df1)