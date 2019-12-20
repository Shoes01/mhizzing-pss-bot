import random as rngesus
import data
import pandas as pd
import requests
import json

# =========== SETUP ===========

base_dict_url = 'https://googledictionaryapi.eu-gb.mybluemix.net/'

# =========== END SETUP =======

def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

def roll(d=1, n=6):
    roll_list = []
    for _ in range(d):
        roll_list.append(rngesus.randint(1, n))
    return roll_list

def dodge_rate(eng_lvl, eng_stat):
    return round(data.engines[eng_lvl]*(1+eng_stat/100)*100, 3)

def allwpns():
    return list(data.wpn_data.index)

def dps(wpn_string, wpn_stat=0.0, power='MAX'):
    wpn_string = wpn_string.upper()
    try:
        wpn = data.wpn_data.loc[wpn_string]
    except:
        return 'This is not a valid WPN. Use the allwpns command to see options.'
    
    if power != 'MAX':
        if power < 1 or power > wpn['POWER']:
            return 'Invalid amount of power for this weapon.'
    else:
        power = wpn['POWER']

    cycle = wpn['Reload'] * (1/(1+wpn_stat*0.01)) * wpn['POWER']/power + wpn['VOLLEY'] + wpn['COOLDOWN']

    sys_dps = round(wpn['SYS_DMG']/cycle, 3)
    crew_dps = round(wpn['CREW_DMG']/cycle, 3)
    shl_dps = round(wpn['SHLD_DMG']/cycle, 3)
    hull_dps = round(wpn['HULL_DMG']/cycle, 3)
    ap_dps = round(wpn['AP_DMG']/cycle, 3)

    return f'**DPS values for {wpn_string} with {wpn_stat}Room Stat and {power} power:**\n```{sys_dps} System DPS\n{crew_dps} Crew DPS\n{shl_dps} Shield DPS\n{hull_dps} Direct Hull DPS\n{ap_dps} AP DPS```'


def dict_api(word):
    query = f'?define={word}&lang=en'
    data = requests.get(base_dict_url+query)
    if data:
        data = data.json()[0]
        word = data['word']
        phonetic = data['phonetic']
        origin = data['origin']
        definition_str = f'**{word}**; phonetic: {phonetic}\n origin:{origin}\n```'
        for i, purpose in enumerate(data['meaning']):
            definition = data['meaning'][purpose][0]['definition']
            definition_str = definition_str + f'{i+1}. {purpose}: {definition}\n'
        definition_str = definition_str + '```'
        return definition_str
    else:
        return 'Could not find this word in the dictionary.'

if __name__ == "__main__":
    print(dodge_rate(8, 50))
    print(dps('MLZ15', 10, 2))