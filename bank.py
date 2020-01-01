import os

from dotenv import load_dotenv
from pymongo import MongoClient


# =========== SETUP ===========

load_dotenv()
DB_PASSWORD = os.getenv('MONGODB_PW')
client = MongoClient(f'mongodb+srv://Mhizzing:{DB_PASSWORD}@expressdiscord-pucto.mongodb.net/test?retryWrites=true&w=majority')

# =========== END SETUP =======

def bank_update_account(account_name, balance=0):
    db = client.bank
    db.accounts.update_one(
    {"name": account_name},
    {"$set": {"balance": balance},
    "$currentDate": {"lastModified": True}},
    upsert = True
    )
    return f'{account_name}\'s balance is now {balance}.'

def bank_inc_balance(account_name, amount):
    db = client.bank

    # Check if account exists
    record = db.accounts.find_one({'name': account_name})
    if record:
        db.accounts.update_one(
        {"name": account_name},
        {"$inc": {"balance": amount},
        "$currentDate": {"lastModified": True}}
        )
        return True
    else:
        return False

def bank_check_balance(account_name):
    db = client.bank
    record = db.accounts.find_one({'name': account_name})
    if record:
        return record['balance']
    else:
        return False

def bank_all_accounts():
    db = client.bank
    accounts = []
    for item in list(db.accounts.find({})):
        accounts.append((item['name'], item['balance']))
    return accounts

def bank_delete_account(account_name):
    db = client.bank
    record = db.accounts.find_one({'name': account_name})
    if record:
        db.accounts.delete_one({'name': account_name})
        return True
    else:
        return False

if __name__ == "__main__":
    print(bank_check_balance('Mhizzing'))