'''
dogechain.info
'''
import logging

from lib import config, util

class ChainUnavailableException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def get_host():
    if config.BLOCKCHAIN_SERVICE_CONNECT:
        return config.BLOCKCHAIN_SERVICE_CONNECT
    else:
        return 'https://dogechain.info'

def check_network_config():
    if config.TESTNET:
        raise ChainUnavailableException("Dogechain.info only supports Dogecoin mainnet")
    if not config.BTC == "DOGE":
        raise ChainUnavailableException("Dogechain.info only supports Dogecoin")

def check():
    check_network_config()

def getinfo():
    result = util.get_url(get_host() + '/chain/Dogecoin/q/getblockcount', abort_on_error=True)
    return {
        "info": {
            "blocks": result
        }
    }

def listunspent(address):
    result = util.get_url(get_host() + '/api/v1/unspent/{}'.format(address), abort_on_error=True)
    if 'success' in result and result['success'] == 1:
        utxo = []
        for txo in result['unspent_outputs']:
            newtxo = {
                'address': address,
                'txid': txo['tx_hash'],
                'vout': txo['tx_output_n'],
                'ts': 1,
                'scriptPubKey': txo['script'],
                'amount': float(txo['value']) / config.UNIT,
                'confirmations': txo['confirmations'],
                'confirmationsFromCache': False
            }
            utxo.append(newtxo)
        return utxo

    return None

def getaddressinfo(address):
    balance = util.get_url(get_host() + '/api/v1/address/balance/{}'.format(address), abort_on_error=True)
    txs = util.get_url(get_host() + '/wallet/api/transactions/{}'.format(address), abort_on_error=True)

    transactions = []
    for tx in txs['transactions']:
        transactions.append(tx['hash'])

    return {
        'addrStr': address,
        'balance': float(balance['balance']),
        'balanceSat': float(balance['balance']) * config.UNIT,
        'totalReceived': float(txs['total_received']) / config.UNIT,
        'totalReceivedSat': float(txs['total_received']),
        'unconfirmedBalance': 0,
        'unconfirmedBalanceSat': 0,
        'unconfirmedTxApperances': 0,
        'txApperances': txs['total_received_n'] + txs['total_sent_n'],
        'transactions': transactions
    }
    
    return None

def gettransaction(tx_hash):
    tx = util.get_url(get_host() + '/api/v1/transaction/{}'.format(tx_hash), abort_on_error=True)
    if 'success' in tx and tx['success'] == 1:
        valueOut = 0
        for vout in tx['transaction']['outputs']:
            valueOut += float(vout['value'])

        return {
            'txid': tx_hash,
            'version': tx['transaction']['version'],
            'locktime': tx['transaction']['locktime'],
            'blockhash': tx['transaction']['block_hash'],
            'confirmations': tx['transaction']['confirmations'],
            'time': tx['transaction']['time'],
            'blocktime': tx['transaction']['time'],
            'valueOut': valueOut,
            'vin': tx['transaction']['inputs'],
            'vout': tx['transaction']['outputs']
        }

    return None


