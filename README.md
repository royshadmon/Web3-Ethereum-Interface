# Web3-Ethereum-Interface

This interface simplifies and abstracts interacting with and deploying Ethereum smart contracts.

This interface does not rely on default account management like the `w3.eth.default_account`. Instead, users of this interface 
need to maintain their own account managment and specify the private key. This is intended to provide a more program-aware interface.
The hope is that this prevents accidental transactions from default accounts. 

To use this code:
```
import importlib.util

file_path = '[path_to]/Web3-Ethereum-Interface/src/web3_eth.py'

# Specify the module name
module_name = 'Web3_Eth'

# Load the module from the file path
spec = importlib.util.spec_from_file_location(module_name, file_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

ganache_url = "http://127.0.0.1:8545"
web3_interface = module.Web3_Eth(ganache_url)
```

## Available functions
```
class Web3_Eth
    def __init__(self, provider: str, account=None, solidity_version='0.8.17', private_key=None, connection_timeout=600):

    def web3_connect(self, provider)

    def compile_contract(self, contract_path, output_directory, solidity_version="0.8.17")

    def get_contract_abi_bin(self, contract_abi_path, contract_bin_path):

    def deploy_contract(self, interface, account_private_key, *constructor_params, value=0)

    def signTransaction(self, transaction, private_key)

    def sendRawTransaction(self, signed_tx)

    def waitForTransactionReceipt(self, tx_hash)

    def getContractAddressFromTxReceipt(self, tx_receipt)

    def verify_acct_addr_matches_p_key(self, acct_address, private_key)

    def get_eth_user(self, private_key)

    def getTransactionCount(self, user: LocalAccount)

    def toCheckSumAddress(self, address)

```
