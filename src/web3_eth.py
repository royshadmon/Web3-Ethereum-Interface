
from web3.providers import HTTPProvider
from web3 import Web3
import os
import glob
from subprocess import Popen
from eth_account.signers.local import LocalAccount
import solcx


# Class object to interact with Ethereum Contracts
class Web3_Eth:
    def __init__(self, provider: str, solidity_version='0.8.17', private_key=None, connection_timeout=600):
        self.provider = provider
        self.private_key = private_key
        self.solidity_version = solidity_version
        self.connection_timeout = connection_timeout
        self.w3 = self.web3_connect(provider)

    def web3_connect(self, provider):
        w3 = Web3(HTTPProvider(provider, request_kwargs={'timeout': self.connection_timeout}))
        try:
            assert(w3.is_connected())
        except AssertionError:
            print(f"Failed to connect to {provider}")
            exit(-1)
        return w3

    def compile_contract(self, contract_path, output_directory, private_key, solidity_version="0.8.17"):


        with open(contract_path, 'r') as f:
            source = f.read()

        solcx.install_solc(version='0.8.17')
        solcx.set_solc_version('0.8.17')
        compiled = solcx.compile_source(source, output_values=['abi', 'bin'])
        id, interface = compiled.popitem()
        return id, interface



    def get_contract_abi_bin(self, contract_abi_path, contract_bin_path):
        contract_instance = {}
        with open(contract_abi_path) as f:
            contract_instance['abi'] = f.read()
        with open(contract_bin_path) as f:
            contract_instance['bin'] = f.read()
        return contract_instance

    def deploy_contract(self, interface, account_private_key, *constructor_params, value=0):
        user = self.get_eth_user(account_private_key)

        if not self.w3.is_address(user.address):
            print(f'Account not valid')
            exit(-1)

        transaction = self.w3.eth.contract(abi=interface['abi'],
            bytecode=interface['bin']).constructor(*constructor_params).build_transaction(
            {
                'from': user.address,
                'chainId': 1337,  # Ganache chain id
                'nonce': self.getTransactionCount(user),
                'value': value,
            }
        )

        signed_tx = self.signTransaction(transaction, account_private_key)
        tx_hash = self.sendRawTransaction(signed_tx)
        tx_receipt = self.waitForTransactionReceipt(tx_hash)
        contract_address = self.getContractAddressFromTxReceipt(tx_receipt)

        store_var_contract = self.w3.eth.contract(address=contract_address, abi=interface["abi"])
        # print(f'address is {contract_address}')
        return contract_address, store_var_contract

    def signTransaction(self, transaction, private_key):
        sender_account = self.get_eth_user(private_key)
        if not self.w3.is_address(sender_account.address):
            print(f"Account address and private key doesn't match sender")
            exit(-1)

        signed_tx = sender_account.sign_transaction(transaction)
        return signed_tx

    def sendRawTransaction(self, signed_tx):
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash

    def waitForTransactionReceipt(self, tx_hash):
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

    def getContractAddressFromTxReceipt(self, tx_receipt):
        return tx_receipt.contractAddress

    def verify_acct_addr_matches_p_key(self, acct_address, private_key):
        sender_account = self.get_eth_user(
            private_key).address
        return acct_address == sender_account

    def get_eth_user(self, private_key):
        return self.w3.eth.account.from_key(private_key)

    def getTransactionCount(self, user: LocalAccount):
        # return self.w3.eth.getTransactionCount(user.address)
        return self.w3.eth.get_transaction_count(user.address)

    def toCheckSumAddress(self, address):
        return self.w3.to_checksum_address(address)
