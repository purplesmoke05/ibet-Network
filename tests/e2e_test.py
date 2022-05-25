"""
Copyright BOOSTRY Co., Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.

You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

See the License for the specific language governing permissions and
limitations under the License.

SPDX-License-Identifier: Apache-2.0
"""
import json
from typing import Dict, Callable, Any
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.datastructures import AttributeDict
from web3.exceptions import ContractLogicError
from web3.types import (
    RPCEndpoint,
    RPCResponse
)

from tests.config import (
    ZERO_ADDRESS,
    WEB3_HTTP_PROVIDER,
    CHAIN_ID,
    TX_GAS_LIMIT,
    DEPLOYED_CONTRACT_ADDRESS
)
from tests.util import (
    TestAccount,
    ContractUtils
)

web3 = Web3(Web3.HTTPProvider(WEB3_HTTP_PROVIDER))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)


# NOTE:
# Called JSON-RPC list.
# - eth_call
# - eth_blockNumber
# - eth_getBlockByNumber
# - eth_getLogs
# - eth_getTransactionCount
# - eth_getTransactionReceipt
# - eth_sendRawTransaction
# - eth_syncing
# - txpool_inspect(Geth API)
# - personal_listAccounts(Geth API)
# - personal_unlockAccounts(Geth API)
# - eth_sendTransaction
# - eth_getCode
class TestE2E:

    ###########################################################################
    # Normal Case
    ###########################################################################

    # <Normal_1_1>
    # deploy setting
    # - eth_getTransactionCount
    # - eth_sendRawTransaction
    # - eth_getTransactionReceipt
    # - eth_call
    def test_normal_1_1(self):

        args = [
            True,
            "0x0123456789abcDEF0123456789abCDef01234567",
            "test text",
            1,
            2,
            b'0123456789abcdefghijklmnopqrstuv'
        ]
        contract_address, _, _ = ContractUtils.deploy_contract(args)
        contract = ContractUtils.get_contract(contract_address)

        # Assertion
        assert contract.functions.item1_bool().call() is True
        assert contract.functions.item1_address().call() == "0x0123456789abcDEF0123456789abCDef01234567"
        assert contract.functions.item1_string().call() == "test text"
        assert contract.functions.item1_uint().call() == 1
        assert contract.functions.item1_int().call() == 2
        assert contract.functions.item1_bytes().call() == b'0123456789abcdefghijklmnopqrstuv'

    # <Normal_1_2>
    # deploy setting(deployed contract)
    # - eth_call
    def test_normal_1_2(self):
        if DEPLOYED_CONTRACT_ADDRESS == ZERO_ADDRESS:
            return

        # Assertion
        contract = ContractUtils.get_contract(DEPLOYED_CONTRACT_ADDRESS)
        assert contract.functions.item3_bool().call() is False
        assert contract.functions.item3_address().call() == "0x0123456789ABCDeF0123456789aBcdEF01234568"
        assert contract.functions.item3_string().call() == "test text2"
        assert contract.functions.item3_uint().call() == 4
        assert contract.functions.item3_int().call() == 8
        assert contract.functions.item3_bytes().call() == b'456789abcdefghijklmnopqrstuvwxyz'

    # <Normal_2_1>
    # call setter/getter function
    # - eth_getTransactionCount
    # - eth_sendRawTransaction
    # - eth_getTransactionReceipt
    # - eth_call
    def test_normal_2_1(self, contract):

        args = [
            False,
            "0x0123456789ABCDeF0123456789aBcdEF01234568",
            "test text2",
            4,
            8,
            b'456789abcdefghijklmnopqrstuvwxyz'
        ]
        tx = contract.functions.setItem2(*args, 0).buildTransaction(
            transaction={
                "chainId": CHAIN_ID,
                "from": TestAccount.address,
                "gas": TX_GAS_LIMIT,
                "gasPrice": 0
            }
        )
        ContractUtils.send_transaction(tx, TestAccount.private_key)

        # Assertion
        assert contract.functions.item2_bool().call() is False
        assert contract.functions.item2_address().call() == "0x0123456789ABCDeF0123456789aBcdEF01234568"
        assert contract.functions.item2_string().call() == "test text2"
        assert contract.functions.item2_uint().call() == 4
        assert contract.functions.item2_int().call() == 8
        assert contract.functions.item2_bytes().call() == b'456789abcdefghijklmnopqrstuvwxyz'
        assert contract.functions.getItemsValueSame().call() == 5

    # <Normal_2_2>
    # call setter/getter function(deployed contract)
    # - eth_getTransactionCount
    # - eth_sendRawTransaction
    # - eth_getTransactionReceipt
    # - eth_call
    def test_normal_2_2(self):
        if DEPLOYED_CONTRACT_ADDRESS == ZERO_ADDRESS:
            return

        # Pre-assertion
        contract = ContractUtils.get_contract(DEPLOYED_CONTRACT_ADDRESS)
        assert contract.functions.getItemsValueOther().call() == 5

        args = [
            False,
            "0x0123456789ABCDeF0123456789aBcdEF01234568",
            "test text2",
            16,
            8,
            b'456789abcdefghijklmnopqrstuvwxyz'
        ]
        tx = contract.functions.setItem2(*args, 0).buildTransaction(
            transaction={
                "chainId": CHAIN_ID,
                "from": TestAccount.address,
                "gas": TX_GAS_LIMIT,
                "gasPrice": 0
            }
        )
        ContractUtils.send_transaction(tx, TestAccount.private_key)

        # Assertion
        assert contract.functions.item2_bool().call() is False
        assert contract.functions.item2_address().call() == "0x0123456789ABCDeF0123456789aBcdEF01234568"
        assert contract.functions.item2_string().call() == "test text2"
        assert contract.functions.item2_uint().call() == 16
        assert contract.functions.item2_int().call() == 8
        assert contract.functions.item2_bytes().call() == b'456789abcdefghijklmnopqrstuvwxyz'
        assert contract.functions.getItemsValueSame().call() == 17

    # <Normal_3_1>
    # Get events
    # - eth_blockNumber
    # - eth_getTransactionCount
    # - eth_sendRawTransaction
    # - eth_getTransactionReceipt
    # - eth_getLogs
    def test_normal_3_1(self, contract):

        block_from = web3.eth.blockNumber
        args = [
            False,
            "0x0123456789ABCDeF0123456789aBcdEF01234568",
            "test text2",
            4,
            8,
            b'456789abcdefghijklmnopqrstuvwxyz'
        ]
        tx = contract.functions.setItem2(*args, 0).buildTransaction(
            transaction={
                "chainId": CHAIN_ID,
                "from": TestAccount.address,
                "gas": TX_GAS_LIMIT,
                "gasPrice": 0
            }
        )
        ContractUtils.send_transaction(tx, TestAccount.private_key)
        block_to = web3.eth.blockNumber
        events = contract.events.SetItem.getLogs(
            fromBlock=block_from,
            toBlock=block_to
        )

        # Assertion
        assert len(events) == 1
        event = events[0]
        args = event["args"]
        assert args["item_bool"] is False
        assert args["item_address"] == "0x0123456789ABCDeF0123456789aBcdEF01234568"
        assert args["item_string"] == "test text2"
        assert args["item_uint"] == 4
        assert args["item_int"] == 8
        assert args["item_bytes"] == b'456789abcdefghijklmnopqrstuvwxyz'

    # <Normal_3_2>
    # Get events(deployed contract)
    # - eth_call
    # - eth_getLogs
    def test_normal_3_2(self):
        if DEPLOYED_CONTRACT_ADDRESS == ZERO_ADDRESS:
            return

        contract = ContractUtils.get_contract(DEPLOYED_CONTRACT_ADDRESS)
        block_number = contract.functions.optional_item().call()
        events = contract.events.SetItem.getLogs(
            fromBlock=block_number,
            toBlock=block_number
        )

        # Assertion
        assert len(events) == 1
        event = events[0]
        args = event["args"]
        assert args["item_bool"] is False
        assert args["item_address"] == "0x0123456789ABCDeF0123456789aBcdEF01234568"
        assert args["item_string"] == "test text2"
        assert args["item_uint"] == 4
        assert args["item_int"] == 8
        assert args["item_bytes"] == b'456789abcdefghijklmnopqrstuvwxyz'

    # <Normal_4>
    # Get block by number
    # - eth_blockNumber
    # - eth_getBlockByNumber
    def test_normal_4(self):

        block_number = web3.eth.blockNumber
        block = web3.eth.get_block(block_number)

        # Assertion
        assert block["number"] == block_number

    # <Normal_5>
    # Get sync information
    # - eth_syncing
    def test_normal_5(self, contract):

        sync = web3.eth.syncing

        # Assertion
        if not isinstance(sync, bool) and not isinstance(sync, dict) and not isinstance(sync, AttributeDict):
            assert False

    # <Normal_6>
    # Get inspected transaction pool
    # - txpool_inspect(Geth API)
    def test_normal_6(self, contract):

        txpool = web3.geth.txpool.inspect()

        # Assertion
        if not isinstance(txpool, dict) and not isinstance(txpool, AttributeDict):
            assert False

    # <Normal_7>
    # Unlock and send transaction
    # - personal_listAccounts(Geth API)
    # - personal_unlockAccounts(Geth API)
    # - eth_sendTransaction
    # - eth_getTransactionReceipt
    def test_normal_7(self, contract):
        # Import raw key
        try:
            web3.geth.personal.import_raw_key(
                TestAccount.private_key,
                TestAccount.password
            )
        except ValueError:
            pass

        # Unlock account
        eth_account = web3.geth.personal.list_accounts()[0]
        web3.geth.personal.unlock_account(
            eth_account,
            TestAccount.password,
            10
        )

        # Send transaction
        args = [
            False,
            "0x0123456789ABCDeF0123456789aBcdEF01234568",
            "test text2",
            4,
            8,
            b'456789abcdefghijklmnopqrstuvwxyz'
        ]
        tx = contract.functions.setItem2(*args, 0).buildTransaction(
            transaction={
                "chainId": CHAIN_ID,
                "from": eth_account,
                "gas": TX_GAS_LIMIT,
                "gasPrice": 0
            }
        )
        tx_hash = web3.eth.sendTransaction(tx)
        txn_receipt = web3.eth.waitForTransactionReceipt(
            transaction_hash=tx_hash,
            timeout=10
        )

        # Assertion
        assert txn_receipt["status"] == 1
        assert contract.functions.item2_bool().call() is False
        assert contract.functions.item2_address().call() == "0x0123456789ABCDeF0123456789aBcdEF01234568"
        assert contract.functions.item2_string().call() == "test text2"
        assert contract.functions.item2_uint().call() == 4
        assert contract.functions.item2_int().call() == 8
        assert contract.functions.item2_bytes().call() == b'456789abcdefghijklmnopqrstuvwxyz'
        assert contract.functions.getItemsValueSame().call() == 5

    # <Normal_8_1>
    # Get bytecode(contract address)
    # - eth_getCode
    def test_normal_8_1(self, contract):

        # Get bytecode
        bytecode = web3.eth.getCode(contract.address)

        # Assertion
        contract_json = ContractUtils.get_contract_json()
        assert bytecode.hex() == f'0x{contract_json["deployedBytecode"]}'

    # <Normal_8_2>
    # Get bytecode(EOA address)
    # - eth_getCode
    def test_normal_8_2(self, contract):

        # Get bytecode
        bytecode = web3.eth.getCode(TestAccount.address)

        # Assertion
        assert bytecode.hex() == "0x"

    ###########################################################################
    # Error Case
    ###########################################################################

    # <Error_1>
    # Occur REVERT
    # assert error
    def test_error_1(self, contract):
        err_flg = 3
        args = [
            False,
            "0x0123456789ABCDeF0123456789aBcdEF01234568",
            "test text2",
            4,
            8,
            b'456789abcdefghijklmnopqrstuvwxyz'
        ]
        tx = contract.functions.setItem2(*args, err_flg).buildTransaction(
            transaction={
                "chainId": CHAIN_ID,
                "from": TestAccount.address,
                "gas": TX_GAS_LIMIT,
                "gasPrice": 0
            }
        )
        nonce = web3.eth.getTransactionCount(TestAccount.address)
        tx["nonce"] = nonce
        signed_tx = web3.eth.account.sign_transaction(
            transaction_dict=tx,
            private_key=TestAccount.private_key
        )
        try:
            tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction.hex())
            txn_receipt = web3.eth.waitForTransactionReceipt(
                transaction_hash=tx_hash,
            )
            # Assertion
            assert txn_receipt["status"] == 0
            tx = web3.eth.getTransaction(tx_hash.hex())

            # build a new transaction to replay:
            replay_tx = {
                'to': tx['to'],
                'from': tx['from'],
                'value': tx['value'],
                'data': tx['input'],
            }

            # replay the transaction locally:
            try:
                web3.eth.call(replay_tx, tx.blockNumber - 1)
            except Exception as e:
                print(e)
                # execution reverted: UniswapV2Router: INSUFFICIENT_OUTPUT_AMOUNT
        except Exception as e:
            print(e)

    # <Error_2>
    # Occur REVERT
    # require error
    def test_error_2(self, contract):

        err_flg = 2
        args = [
            False,
            "0x0123456789ABCDeF0123456789aBcdEF01234568",
            "test text2",
            4,
            8,
            b'456789abcdefghijklmnopqrstuvwxyz'
        ]
        tx = contract.functions.setItem2(*args, err_flg).buildTransaction(
            transaction={
                "chainId": CHAIN_ID,
                "from": TestAccount.address,
                "gas": TX_GAS_LIMIT,
                "gasPrice": 0
            }
        )
        nonce = web3.eth.getTransactionCount(TestAccount.address)
        tx["nonce"] = nonce
        signed_tx = web3.eth.account.sign_transaction(
            transaction_dict=tx,
            private_key=TestAccount.private_key
        )
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction.hex())
        txn_receipt = web3.eth.waitForTransactionReceipt(
            transaction_hash=tx_hash,
            timeout=10
        )

        # Assertion
        assert txn_receipt["status"] == 0

    # <Error_3>
    # Occur REVERT
    # reverted
    def test_error_3(self, contract):

        err_flg = 3
        args = [
            False,
            "0x0123456789ABCDeF0123456789aBcdEF01234568",
            "test text2",
            4,
            8,
            b'456789abcdefghijklmnopqrstuvwxyz'
        ]
        tx = contract.functions.setItem2(*args, err_flg).buildTransaction(
            transaction={
                "chainId": CHAIN_ID,
                "from": TestAccount.address,
                "gas": TX_GAS_LIMIT,
                "gasPrice": 0
            }
        )
        nonce = web3.eth.getTransactionCount(TestAccount.address)
        tx["nonce"] = nonce
        signed_tx = web3.eth.account.sign_transaction(
            transaction_dict=tx,
            private_key=TestAccount.private_key
        )
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction.hex())
        txn_receipt = web3.eth.waitForTransactionReceipt(
            transaction_hash=tx_hash,
            timeout=10
        )

        # Assertion
        assert txn_receipt["status"] == 0

    # <Error_Ex1>
    # Occur REVERT
    # and parse json error message
    def test_error_ex1(self, contract):
        err_flg = 1
        err_msg = "this must be reverted"
        args = [
            False,
            err_msg,
        ]
        tx = contract.functions.revertTest(*args, err_flg).buildTransaction(
            transaction={
                "chainId": CHAIN_ID,
                "from": TestAccount.address,
                "gas": TX_GAS_LIMIT,
                "gasPrice": 0
            }
        )
        nonce = web3.eth.getTransactionCount(TestAccount.address)
        tx["nonce"] = nonce
        signed_tx = web3.eth.account.sign_transaction(
            transaction_dict=tx,
            private_key=TestAccount.private_key
        )
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction.hex())
        txn_receipt = web3.eth.waitForTransactionReceipt(
            transaction_hash=tx_hash,
        )
        # Assertion
        assert txn_receipt["status"] == 0
        msg_dict = inspect_tx_failure_json(tx_hash.hex())
        assert msg_dict["msg"] == err_msg

    # <Error_Ex2>
    # Occur REVERT
    # and parse json error message
    def test_error_ex2(self, contract):
        web3.middleware_onion.add(transaction_debug_middleware, "tx_debug")
        err_flg = 2
        err_msg = "this must be reverted"
        args = [
            False,
            err_msg,
        ]
        tx = contract.functions.revertTest(*args, err_flg).buildTransaction(
            transaction={
                "chainId": CHAIN_ID,
                "from": TestAccount.address,
                "gas": TX_GAS_LIMIT,
                "gasPrice": 0
            }
        )
        nonce = web3.eth.getTransactionCount(TestAccount.address)
        tx["nonce"] = nonce
        signed_tx = web3.eth.account.sign_transaction(
            transaction_dict=tx,
            private_key=TestAccount.private_key
        )
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction.hex())
        txn_receipt = web3.eth.waitForTransactionReceipt(
            transaction_hash=tx_hash,
        )

        # Assertion
        assert txn_receipt["status"] == 0
        result = inspect_tx_failure_bytecode(tx_hash.hex())
        assert result == "0x8e63a404000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000001574686973206d7573742062652072657665727465640000000000000000000000"

    # <Error_Ex3>
    # Occur REVERT
    # and parse json error message
    def test_error_ex3(self, contract):
        err_flg = 3
        msg = "this must be reverted"
        args = [
            False,
            msg,
        ]
        tx = contract.functions.revertTest(*args, err_flg).buildTransaction(
            transaction={
                "chainId": CHAIN_ID,
                "from": TestAccount.address,
                "gas": TX_GAS_LIMIT,
                "gasPrice": 0
            }
        )
        nonce = web3.eth.getTransactionCount(TestAccount.address)
        tx["nonce"] = nonce
        signed_tx = web3.eth.account.sign_transaction(
            transaction_dict=tx,
            private_key=TestAccount.private_key
        )
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction.hex())
        txn_receipt = web3.eth.waitForTransactionReceipt(
            transaction_hash=tx_hash,
        )
        # Assertion
        assert txn_receipt["status"] == 0
        result = inspect_tx_failure_string(tx_hash.hex())
        assert result == "ERR_001"


def inspect_tx_failure_bytecode(tx_hash: str) -> str:
    tx = web3.eth.getTransaction(tx_hash)

    # build a new transaction to replay:
    replay_tx = {
        'to': tx['to'],
        'from': tx['from'],
        'value': tx['value'],
        'data': tx['input'],
    }

    # replay the transaction locally:
    try:
        web3.eth.call(replay_tx, tx.blockNumber - 1)
    except ContractLogicError as e:
        if e.args[0]:
            # TODO: e.args[0]: 0x8e.....
            #     It must be decoded with ABI, but Web3.py does not provide decoder.
            msg = e.args[0]
            return msg
    except Exception as e:
        raise e
    raise Exception("Inspect transaction failure is failed. There is no message for message.")


def inspect_tx_failure_string(tx_hash: str) -> str:
    tx = web3.eth.getTransaction(tx_hash)

    # build a new transaction to replay:
    replay_tx = {
        'to': tx['to'],
        'from': tx['from'],
        'value': tx['value'],
        'data': tx['input'],
    }

    # replay the transaction locally:
    try:
        web3.eth.call(replay_tx, tx.blockNumber - 1)
    except ContractLogicError as e:
        if e.args[0]:
            msg = e.args[0].split("execution reverted: ")[1]
            return msg
    except Exception as e:
        raise e
    raise Exception("Inspect transaction failure is failed. There is no message for message.")


def inspect_tx_failure_json(tx_hash: str) -> Dict:
    tx = web3.eth.getTransaction(tx_hash)

    # build a new transaction to replay:
    replay_tx = {
        'to': tx['to'],
        'from': tx['from'],
        'value': tx['value'],
        'data': tx['input'],
    }

    # replay the transaction locally:
    try:
        web3.eth.call(replay_tx, tx.blockNumber - 1)
    except ContractLogicError as e:
        if e.args[0]:
            msg = e.args[0].split("execution reverted: ")[1]
            return json.loads(msg)
    except Exception as e:
        raise e
    raise Exception("Inspect transaction failure is failed. There is no message for message.")


def transaction_debug_middleware(
    make_request: Callable[[RPCEndpoint, Any], Any], w3: "Web3"
) -> Callable[[RPCEndpoint, Any], RPCResponse]:
    """
    Debug transaction message middleware
    """
    def middleware(method: RPCEndpoint, params: Any) -> RPCResponse:
        response = make_request(method, params)
        if response and method is "eth_call":
            if response["error"]["data"]:
                # NOTE:
                #   Insert HexBytes to msg field and then Exception contains HexBytes error msg from blockchain.
                response['error']['message'] = response["error"]["data"]
        return response
    return middleware