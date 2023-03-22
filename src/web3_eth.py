
from web3.providers import HTTPProvider
from web3 import Web3
import os
import glob
from subprocess import Popen
from eth_account.signers.local import LocalAccount


# Class object to interact with Ethereum Contracts
class Web3_Eth:
    def __init__(self, provider: str, account=None, solidity_version='0.8.17', private_key=None):
        self.provider = provider
        self.private_key = private_key
        self.solidity_version = solidity_version
        self.w3 = self.web3_connect(provider)

        if account:
            if self.w3.isAddress(account):
                self.account = account # public key
            else:
                print("Specified Account isn't valid")
                exit(-1)
        else:
            self.account = None

    def web3_connect(self, provider):
        w3 = Web3(HTTPProvider(provider))
        try:
            assert(w3.isConnected())
        except AssertionError:
            print(f"Failed to connect to {provider}")
            exit(-1)
        return w3

    def compile_contract(self, contract_path, output_directory, solidity_version="0.8.17"):
        contract_name = contract_path.split('/')[-1].split('.')[0]
        # Run the javascript compile contract command
        compile_command = f"solcjs --bin --abi {contract_path} --output-dir {output_directory}"

        print(compile_command.strip())
        p = Popen(compile_command.strip(), shell=True)
        p.communicate()

        # Remove the interface files
        keyword = "Interface"
        file_list = glob.glob(os.path.join(output_directory, f"*{keyword}*"))
        for file_path in file_list:
            os.remove(file_path)

        # Rename files
        for filename in os.listdir(output_directory):
            if filename.split('.')[-1] == 'bin':
                os.rename(os.path.join(output_directory, filename), os.path.join(output_directory, f'{contract_name}.bin'))
            elif filename.split('.')[-1] == 'abi':
                os.rename(os.path.join(output_directory, filename), os.path.join(output_directory, f'{contract_name}.abi'))

    def get_contract_abi_bin(self, contract_abi_path, contract_bin_path):
        contract_instance = {}
        with open(contract_abi_path) as f:
            contract_instance['abi'] = f.read()
        with open(contract_bin_path) as f:
            contract_instance['bin'] = f.read()
        return contract_instance

    def deploy_contract(self, abi, bin, account_private_key, account_addr=None, constructor_params=None):

        if not self.w3.isAddress(account_addr):
            if not self.account:
                print(f'No account specified')
                exit(-1)

            else:
                account_addr = self.account

        Contract = self.w3.eth.contract(abi=abi, bytecode=bin)

        user = self.get_eth_user(account_private_key)
        if not user.address == account_addr:
            print(f"User doesn't match private key")
            exit(-1)

        transaction = Contract.constructor().buildTransaction({
            'from': user.address,
            'nonce': self.getTransactionCount(user),
            'gas': 2000000,
            'gasPrice': self.w3.toWei('50', 'gwei')
        })

        signed_tx = self.signTtransaction(user.address, account_private_key, transaction)

        tx_hash = self.sendRawTransaction(signed_tx)

        tx_receipt = self.waitForTransactionReceipt(tx_hash)

        contract_address = self.getContractAddressFromTxReceipt(tx_receipt)
        return contract_address

    def signTtransaction(self, account_addr, private_key, transaction):
        if not self.verify_acct_addr_matches_p_key(account_addr, private_key):
            print(f"Account address and private key doesn't match sender")
            exit(-1)
        sender_account = self.get_eth_user(private_key)
        signed_tx = sender_account.sign_transaction(transaction)
        return signed_tx

    def sendRawTransaction(self, signed_tx):
        tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return tx_hash

    def waitForTransactionReceipt(self, tx_hash):
        tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
        return tx_receipt

    def getContractAddressFromTxReceipt(self, tx_receipt):
        return tx_receipt.contractAddress

    def verify_acct_addr_matches_p_key(self, acct_address, private_key):
        sender_account = self.get_eth_user(
            private_key).address
        return acct_address == sender_account

    def get_eth_user(self, private_key):
        return self.w3.eth.account.privateKeyToAccount(
            private_key)

    def getTransactionCount(self, user: LocalAccount):
        return self.w3.eth.getTransactionCount(user.address)
