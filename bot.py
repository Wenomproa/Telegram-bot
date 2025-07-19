import telebot
from mnemonic import Mnemonic
from ecdsa import SigningKey, SECP256k1
import hashlib
import requests
import base58
import os

TOKEN = '7919640577:AAE-6M9yer-d8vGnsEXzrNxLNfkWBkrwZdw'
bot = telebot.TeleBot(TOKEN)

def sha256(data):
return hashlib.sha256(data).digest()

def ripemd160(data):
h = hashlib.new('ripemd160')
h.update(data)
return h.digest()

def generate_btc_address(seed):
sk = SigningKey.from_string(seed[:32], curve=SECP256k1)
vk = sk.get_verifying_key()
pubkey = b'\x04' + vk.to_string()
h160 = ripemd160(sha256(pubkey))
addr = b'\x00' + h160
checksum = sha256(sha256(addr))[:4]
return base58.b58encode(addr + checksum).decode()

def get_btc_balance(address):
url = f"https://blockchain.info/q/addressbalance/{address}"
try:
res = requests.get(url, timeout=10)
return int(res.text) / 1e8
except:
return 0

def get_trx_balance(address):
url = f"https://apilist.tronscanapi.com/api/account?address={address}"
try:
res = requests.get(url, timeout=10).json()
balance = res.get('balance', 0)
return float(balance) / 1e6
except:
return 0

def get_eth_balance(address):
try:
url = f"https://api.blockcypher.com/v1/eth/main/addrs/{address}/balance"
res = requests.get(url, timeout=10).json()
return res.get("balance", 0) / 1e18
except:
return 0

def get_ton_balance(address):
try:
url = f"https://toncenter.com/api/v2/getAddressBalance?address={address}"
res = requests.get(url, timeout=10).json()
return int(res['result']) / 1e9
except:
return 0

@bot.message_handler(content_types=['document'])
def handle_file(message):
file_info = bot.get_file(message.document.file_id)
downloaded = bot.download_file(file_info.file_path)
filename = message.document.file_name

with open(filename, 'wb') as f:  
    f.write(downloaded)  

with open(filename, 'r') as f:  
    seeds = f.read().splitlines()  

found = []  
for seed in seeds:  
    try:  
        mnemo = Mnemonic("english")  
        if not mnemo.check(seed):  
            continue  
        seed_bytes = hashlib.pbkdf2_hmac("sha512", seed.encode(), b'mnemonic', 2048)  

        btc_address = generate_btc_address(seed_bytes)  
        btc_balance = get_btc_balance(btc_address)  

        eth_balance = get_eth_balance(btc_address)  
        trx_balance = get_trx_balance(btc_address)  
        ton_balance = get_ton_balance(btc_address)  

        total = btc_balance + eth_balance + trx_balance + ton_balance  

        if total > 0:  
            result = f"✅ Found:\nSeed: {seed}\nBTC: {btc_address} = {btc_balance} BTC\nTRX: {trx_balance} TRX\nETH: {eth_balance} ETH\nTON: {ton_balance} TON"  
            found.append(result)  
            bot.send_message(message.chat.id, result)  
    except Exception as e:  
        continue  

if not found:  
    bot.send_message(message.chat.id, "❌ Дар ягон wallet баланс нест.")

bot.polling()

