import time
import random
from web3 import Web3
from loguru import logger
import requests


NFTS2ME_ABI = [
    {
        "name": None,
        "type": "constructor",
        "inputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "gas": None,
        "_isFragment": True
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "mint",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "owner",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# контракт NFTS2ME
contract_address = "0x3A21e152aC78f3055aA6b23693FB842dEFdE0213"

# Рпс
web3 = Web3(Web3.HTTPProvider('https://rpc.linea.build'))

# URL для змінювача проксі
proxy_changer_url = 'Силка на заміну'

# URL проксі
proxy_url = '-'


def read_private_keys(file_path):
    with open(file_path, 'r') as file:
        private_keys = [line.strip() for line in file if line.strip()]
    return private_keys


def change_proxy():
    global proxy_url
    try:
        response = requests.get(proxy_changer_url)
        if response.status_code == 200:
            new_proxy_url = response.text.strip()
            proxy_url = new_proxy_url
            logger.info(f"Changed proxy URL to: {proxy_url}")
        else:
            logger.error(f"Failed to fetch new proxy URL. Status code: {response.status_code}")
    except requests.RequestException as e:
        logger.error(f"Failed to fetch new proxy URL: {str(e)}")


def check_nft_balance(contract, address):
    balance = contract.functions.balanceOf(address).call()
    return balance > 0


def mint_nft(amount, private_key):
    account = web3.eth.account.from_key(private_key)
    account_address = account.address
    contract = web3.eth.contract(address=contract_address, abi=NFTS2ME_ABI)

    
    if check_nft_balance(contract, account_address):
        logger.info(f"Wallet {account_address} already has an NFT. Skipping...")
        return

    nonce = web3.eth.get_transaction_count(account_address)
    
    
    gas_price = web3.to_wei(random.uniform(0.058, 0.1), 'gwei')

    tx_data = contract.functions.mint(amount).build_transaction({
        'chainId': 59144,
        'gas': 2000000,
        'gasPrice': gas_price,
        'nonce': nonce,
    })

    signed_txn = web3.eth.account.sign_transaction(tx_data, private_key)

    
    change_proxy()

    try:
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        logger.info(f"Minted NFT from wallet: {account_address}. Transaction hash: {tx_hash.hex()}")
    except Exception as e:
        logger.error(f"Failed to mint NFT from wallet: {account_address}. Error: {str(e)}")
        return

    return tx_hash


def main():
    amount_to_mint = 1
    private_keys = read_private_keys('wallets.txt')
    random.shuffle(private_keys)

    for private_key in private_keys:
        mint_nft(amount_to_mint, private_key)
        
        # Пауза от і до в секундах
        pause_duration = random.randint(600, 2000)
        logger.info(f"Waiting for {pause_duration} seconds before next wallet...")
        time.sleep(pause_duration)

if __name__ == "__main__":
    main()