
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
            assert(w3.is_connected())
        except AssertionError:
            print(f"Failed to connect to {provider}")
            exit(-1)
        return w3

    def compile_contract(self, contract_path, output_directory, solidity_version="0.8.17"):
        contract_name = contract_path.split('/')[-1].split('.')[0]
        # Run the javascript compile contract command
        compile_command = f"solcjs --bin --abi {contract_path} --output-dir {output_directory}"
        import solcx
        self.w3.eth.default_account = self.w3.eth.accounts[0]
        with open(contract_path, 'r') as f:
            source = f.read()

        solcx.install_solc(version='0.8.17')
        solcx.set_solc_version('0.8.17')
        compiled = solcx.compile_source(source, output_values=['abi', 'bin'])
        id, interface = compiled.popitem()
        return id, interface

        # tx_hash = self.w3.eth.contract(
        #     abi=interface['abi'],
        #     bytecode=interface['bin']).constructor().transact()
        #
        #
        # address = self.w3.eth.get_transaction_receipt(tx_hash)['contractAddress']
        store_var_contract = self.w3.eth.contract(address=address, abi=interface["abi"])

        transaction = store_var_contract.functions.register().build_transaction(
            {
                # 'gas': 10000000,  # 3172000
                'chainId': 1337,  # Ganache chain id
                # 'gasPrice': int(web3_interface.w3.eth.gas_price),
                'nonce': self.w3.eth.get_transaction_count("0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"),
                # 'value': 0,
            }
        )
        signed_tx = self.w3.eth.account.sign_transaction(transaction, "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d")

        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        # result = store_var_contract.functions.register().transact()

        print(store_var_contract.events.EM_CREATED().process_receipt(tx_receipt))

        # print(compile_command.strip())
        # p = Popen(compile_command.strip(), shell=True)
        # p.communicate()
        #
        # # Remove the interface files
        # keyword = "Interface"
        # file_list = glob.glob(os.path.join(output_directory, f"*{keyword}*"))
        # for file_path in file_list:
        #     os.remove(file_path)
        #
        # # Rename files
        # for filename in os.listdir(output_directory):
        #     if filename.split('.')[-1] == 'bin':
        #         os.rename(os.path.join(output_directory, filename), os.path.join(output_directory, f'{contract_name}.bin'))
        #     elif filename.split('.')[-1] == 'abi':
        #         os.rename(os.path.join(output_directory, filename), os.path.join(output_directory, f'{contract_name}.abi'))

    def get_contract_abi_bin(self, contract_abi_path, contract_bin_path):
        contract_instance = {}
        with open(contract_abi_path) as f:
            contract_instance['abi'] = f.read()
        with open(contract_bin_path) as f:
            contract_instance['bin'] = f.read()
        return contract_instance

    def deploy_contract(self, interface, account_private_key, constructor_params=None):
        user = self.get_eth_user(account_private_key)

        if not self.w3.is_address(user.address):
            print(f'Account not valid')
            exit(-1)

        transaction = self.w3.eth.contract(abi=interface['abi'],
            bytecode=interface['bin']).constructor().build_transaction(
            {
                'chainId': 1337,  # Ganache chain id
                'nonce': self.getTransactionCount(user),
                # 'value': 0,
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
        # return self.w3.eth.account.privateKeyToAccount(
        #     private_key)
        return self.w3.eth.account.from_key(private_key)

    def getTransactionCount(self, user: LocalAccount):
        # return self.w3.eth.getTransactionCount(user.address)
        return self.w3.eth.get_transaction_count(user.address)
