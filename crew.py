import urllib.parse
import urllib.request
import xml.etree.ElementTree
import pandas as pd


def get_data_from_url(url):
    data = urllib.request.urlopen(url).read()
    return data.decode('utf-8')


def xmltext_to_df(raw_text):
    df = pd.DataFrame()
    root = xml.etree.ElementTree.fromstring(raw_text)
    for c in root:
        for cc in c:
            for i, ccc in enumerate(cc):
                df = df.append(pd.DataFrame(ccc.attrib, index=[i]))
    return df


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

# ----- Character Sheet -----------------------------------------------
def request_new_char_sheet():
    # Download Character Sheet from PSS Servers
    url = base_url + 'CharacterService/ListAllCharacterDesigns?languageKey=en'
    data = urllib.request.urlopen(url).read()
    return data.decode()

# ----- Main ----------------------------------------------------------
if __name__ == "__main__":
    test = request_new_char_sheet()
    df = xmltext_to_df(test)
    print(df)
    df.to_csv("data/psscrew.csv")
