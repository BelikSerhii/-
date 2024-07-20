import time
import random
from web3 import Web3
from loguru import logger
import requests

# ABI 
NFTS2ME_ABI = [
    {
        "inputs": [
            {
                "internalType": "bytes4",
                "name": "bytes4",
                "type": "bytes4"
            },
            {
                "internalType": "bytes4",
                "name": "launchpadId",
                "type": "bytes4"
            },
            {
                "internalType": "uint256",
                "name": "slotId",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "quantity",
                "type": "uint256"
            },
            {
                "internalType": "uint256[]",
                "name": "additional",
                "type": "uint256[]"
            },
            {
                "internalType": "bytes",
                "name": "data",
                "type": "bytes"
            }
        ],
        "name": "launchpadBuy",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# ABI balanceOf
BALANCE_OF_ABI = [
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

# контракт
contract_address = "0xBcFa22a36E555c507092FF16c1af4cB74B8514C8"
balance_contract_address = "0x56223A633B78DCcF6926c4734B2447a4b2018CcE"


web3 = Web3(Web3.HTTPProvider('https://rpc.linea.build'))


proxy_changer_url = '-'


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


def mint_nft(private_key):
    account = web3.eth.account.from_key(private_key)
    account_address = account.address
    contract = web3.eth.contract(address=contract_address, abi=NFTS2ME_ABI)
    balance_contract = web3.eth.contract(address=balance_contract_address, abi=BALANCE_OF_ABI)

    
    if check_nft_balance(balance_contract, account_address):
        logger.info(f"Wallet {account_address} already has an NFT. Skipping...")
        return

    nonce = web3.eth.get_transaction_count(account_address)
    gas_price = web3.to_wei(random.uniform(0.05, 0.1), 'gwei')

    
    bytes4_param = '0x0c21cfbb'
    launchpad_id = '0x2968bd75'
    slot_id = 0
    quantity = 1
    additional = []
    data = b''

    tx_data = contract.functions.launchpadBuy(
        bytes4_param,
        launchpad_id,
        slot_id,
        quantity,
        additional,
        data
    ).build_transaction({
        'chainId': 59144,
        'gas': 2000000,
        'gasPrice': gas_price,
        'nonce': nonce,
    })

    signed_txn = web3.eth.account.sign_transaction(tx_data, private_key)

    try:
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        logger.info(f"Minted NFT from wallet: {account_address}. Transaction hash: {tx_hash.hex()}")

        
        change_proxy()
    except Exception as e:
        logger.error(f"Failed to mint NFT from wallet: {account_address}. Error: {str(e)}")
        return

    return tx_hash

def main():
    private_keys = read_private_keys('wallets.txt')
    random.shuffle(private_keys)

    for private_key in private_keys:
        mint_nft(private_key)
        
        # Пауза
        pause_duration = random.randint(600, 1800)
        logger.info(f"Waiting for {pause_duration} seconds before next wallet...")
        time.sleep(pause_duration)

if __name__ == "__main__":
    main()
