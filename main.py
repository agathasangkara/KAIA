import requests
from eth_account import Account
from web3 import Web3

class KAIA:
    
    def __init__(self, *args, **kwargs) -> None:
        self.api = requests.Session()
        self.RPC_URL = "https://archive-en.node.kaia.io"
        self.w3 = Web3(Web3.HTTPProvider(self.RPC_URL))
        self.TO_ADDRESS = self.w3.toChecksumAddress("0x09b3252867f6fd67a7353527367d6ceeac0e5700") # RECEIVER 
        
    def get_chain_id(self):
        payload = {"jsonrpc": "2.0", "method": "eth_chainId", "params": [], "id": 1}
        response = self.api.post(self.RPC_URL, json=payload)
        result = response.json().get("result")
        return int(result, 16) if result else None
    
    def get_nonce(self, address):
        payload = {"jsonrpc": "2.0", "method": "eth_getTransactionCount", "params": [address, "latest"], "id": 1}
        response = self.api.post(self.RPC_URL, json=payload)
        result = response.json().get("result")
        return int(result, 16) if result else None
    
    def get_gas_price(self):
        payload = {"jsonrpc": "2.0", "method": "eth_gasPrice", "params": [], "id": 1}
        response = self.api.post(self.RPC_URL, json=payload)
        result = response.json().get("result")
        return int(result, 16) if result else None
    
    def get_balance(self, address):
        payload = {"jsonrpc": "2.0", "method": "eth_getBalance", "params": [address, "latest"], "id": 1}
        response = self.api.post(self.RPC_URL, json=payload)
        result = response.json().get("result")
        return Web3.fromWei(int(result, 16), "ether") if result else 0
    
    def send_transaction(self, value_kaia):
        value_wei = Web3.toWei(value_kaia, "ether")
        nonce = self.get_nonce(SENDER_ADDRESS)
        chain_id = self.get_chain_id()
        base_fee = self.get_gas_price()

        if nonce is None or chain_id is None or base_fee is None:
            print("Failed to retrieve nonce, chain ID, or gas price!")
            return

        priority_fee = Web3.toWei(2, "gwei")
        max_fee = base_fee + priority_fee
        gas_limit = 21000
        tx = {
            "nonce": nonce,
            "to": self.TO_ADDRESS,
            "value": value_wei,
            "gas": gas_limit,
            "maxFeePerGas": max_fee,
            "maxPriorityFeePerGas": priority_fee,
            "chainId": chain_id,
            "type": "0x2"
        }
        signed_tx = Account.sign_transaction(tx, PRIVATE_KEY)
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_sendRawTransaction",
            "params": [signed_tx.rawTransaction.hex()],
            "id": 1
        }
        response = self.api.post(self.RPC_URL, json=payload)
        print(f"TX Hash: {response.json().get('result', 'Failed to send transaction !')}")
    
    def get_transaction_receipt(self, SENDER_ADDRESS: str) -> str:
        sender_balance = self.get_balance(SENDER_ADDRESS)
        print(f"{line_number}. {SENDER_ADDRESS} {sender_balance} KAIA")
        base_fee = self.get_gas_price()
        priority_fee = Web3.toWei(2, "gwei")
        max_fee = base_fee + priority_fee
        gas_limit = 21000
        total_gas_cost = Web3.fromWei(max_fee * gas_limit, "ether")
        available_balance = sender_balance - total_gas_cost
        if available_balance <= 0:
            print("Available balance not enough for fee !")
        else:
            self.send_transaction(available_balance)


with open("wallets.txt", "r") as file:
    for line_number, line in enumerate(file, start=1):
        data = line.strip().split("|")
        PRIVATE_KEY = data[1]
        SENDER_ADDRESS = data[0]
        KAIA().get_transaction_receipt(SENDER_ADDRESS)
        
