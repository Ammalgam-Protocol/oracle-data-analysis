import os
import logging
import sys
import unittest
import hashlib
import tempfile
from unittest import TestCase

from eth_typing import Address
from pandas import DataFrame
from pandas.util.testing import assert_frame_equal
from web3 import Web3
import pandas as pd


from src.local_node.event_scanner import JSONifiedState
from src.local_node.process_state_to_df import ProcessStateToDF
from src.local_node.scanner_runner import ScannerRunner
from src.uniswap_v2_pair_abi import UNISWAP_V2_PAIR_ABI

this_log = logging.getLogger(__name__)
this_log.setLevel(logging.INFO)
this_log.addHandler(logging.StreamHandler(sys.stdout))


class TestScannerWithNode(TestCase, ScannerRunner):
    ETH_POOL_UNI_V2_CONTRACT_ADDRESS: Address = "0x85Cb0baB616Fe88a89A35080516a8928F38B518b"
    FIRST_BLOCK = 11876000
    NODE_URL = "http://1.1.1.1:1111"
    ABI = UNISWAP_V2_PAIR_ABI

    def setUp(self):
        # Create the directory if it doesn't exist
        if not os.path.exists('./state'):
            os.makedirs('./state')

    def test_web_3_sync(self):


        w3 = Web3(Web3.HTTPProvider(os.getenv('NODE_URL', self.NODE_URL), request_kwargs={'timeout': 60}))
        self.assertTrue(w3.isConnected())

        contract = w3.eth.contract(address=self.ETH_POOL_UNI_V2_CONTRACT_ADDRESS, abi=self.ABI)

        print(contract)
        event_filter = contract.events.Sync.createFilter(fromBlock=16478475-1000, toBlock=16478475)
        events = event_filter.get_all_entries()
        self.assertEqual(len(events), 2)
        self.assertEqual(set(events[0].keys()), {'address', 'args', 'blockHash', 'blockNumber', 'event', 'logIndex',
                                                 'transactionHash', 'transactionIndex'})
        self.assertEqual(events[0]["event"], 'Sync')
        self.assertEqual(set(events[0]["args"].keys()), {'reserve0', 'reserve1'})
        print(events[0]["args"])

        event_filter = contract.events.Swap.createFilter(fromBlock=16478475 - 1000, toBlock=16478475)
        swaps = event_filter.get_all_entries()
        print(len(swaps))
        print(swaps[0]["args"].keys())


    def test_read_json_state_and_save_to_csv(self):
        json_state = JSONifiedState("test-state.json")
        json_state.restore()
        state = json_state.state
        state_df = ProcessStateToDF.process_state(state["blocks"], self)

        # Check if DataFrame is created
        self.assertTrue(isinstance(state_df, DataFrame))
        
        # Save DataFrame to CSV file
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
            csv_filename = temp_file.name
            state_df.to_csv(csv_filename)
            # Check if CSV file is created
            self.assertTrue(os.path.exists(csv_filename))
            # Check if checksum matches
            
        # Calculate checksum of the CSV file
        expected_checksum = "e6078227af70572b2b4f89e44d60eb2d"  # Generate using : md5sum file.csv
        with open(csv_filename, "rb") as f:
            csv_checksum = hashlib.md5(f.read()).hexdigest()
            self.assertEqual(csv_checksum, expected_checksum, "Checksums do not match")


    def test_read_json_state_and_pickle(self):
        json_state = JSONifiedState("test-state.json")
        json_state.restore()
        state = json_state.state
        state_df = ProcessStateToDF.process_state(state["blocks"], self)

        # Check if DataFrame is created
        self.assertTrue(isinstance(state_df, DataFrame))

         # Save DataFrame to CSV file
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as temp_file:
            pkl_filename = temp_file.name
            state_df.to_pickle(pkl_filename)
            # Check if CSV file is created
            self.assertTrue(os.path.exists(pkl_filename))
            # Check if checksum matches
            
        # Calculate checksum of the CSV file
        expected_checksum = "9b59cb3e402118452023c6b44fc7146d"  # Generate using : md5sum file.csv
        with open(pkl_filename, "rb") as f:
            pkl_checksum = hashlib.md5(f.read()).hexdigest()
            self.assertEqual(pkl_checksum, expected_checksum, "Checksums do not match")
        
       


            


