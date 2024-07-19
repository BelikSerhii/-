import time
import random
from web3 import Web3
from loguru import logger
import requests


NFTS2ME_ABI = [
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "account",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "id",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            },
            {
                "internalType": "bytes",
                "name": "data",
                "type": "bytes"
            }
        ],
        "name": "mint",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# Адреса контракту NFTS2ME
contract_address = "0x5A77B45B6f5309b07110fe98E25A178eEe7516c1"


web3 = Web3(Web3.HTTPProvider('https://rpc.linea.build'))

# URL для змінювача проксі
proxy_changer_url = ''

# URL проксі
proxy_url = ''


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


def mint_nft(amount, private_key):
    account = web3.eth.account.from_key(private_key)
    account_address = account.address  
    contract = web3.eth.contract(address=contract_address, abi=NFTS2ME_ABI)

    nonce = web3.eth.get_transaction_count(account_address)
    gas_price = web3.to_wei(random.uniform(0.05, 0.1), 'gwei')
    token_id = 0  
    data = '0x0000000000000000000000000000000000000000000000000000000000000001'  

    tx_data = contract.functions.mint(account_address, token_id, amount, data).build_transaction({
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
        
        # Пауза
        pause_duration = random.randint(600, 1800)
        logger.info(f"Waiting for {pause_duration} seconds before next wallet...")
        time.sleep(pause_duration)

if __name__ == "__main__":
    main()
