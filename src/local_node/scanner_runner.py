import json
import time
from typing import Union, Type

from tqdm import tqdm
from web3 import Web3
from web3.contract import Contract

from src.local_node.event_scanner import JSONifiedState, EventScanner


class ScannerRunner:
    @staticmethod
    def run_scanner(file_name, first_block, node_url, abi, uni_pair_contract_address, last_block=-1):
        provider = Web3.HTTPProvider(node_url, request_kwargs={'timeout': 60})
        provider.middlewares.clear()
        web3 = Web3(provider)
        abi = json.loads(abi)
        pair_contact: Union[Type[Contract], Contract] = web3.eth.contract(abi=abi)
        state = JSONifiedState(file_name)
        state.restore()
        scanner = EventScanner(
            web3=web3, 
            contract=pair_contact, 
            state=state, 
            events=[pair_contact.events.Sync, pair_contact.events.Swap],
            filters={"address": uni_pair_contract_address},
            max_chunk_scan_size=10000)
        
        chain_reorg_safety_blocks = 10
        scanner.delete_potentially_forked_block_data(state.get_last_scanned_block() - chain_reorg_safety_blocks)
        start_block = max(state.get_last_scanned_block() - chain_reorg_safety_blocks, first_block)
        # TODO(WF): add arg to overwrite
        if last_block <0:
            end_block = scanner.get_suggested_scan_end_block()
        else:
            end_block = last_block    
        blocks_to_scan = end_block - start_block
        print(f"Scanning events from blocks {start_block} - {end_block}")
        start = time.time()
        with tqdm(total=blocks_to_scan) as progress_bar:
            def _update_progress(start, end, current, current_block_timestamp, chunk_size, events_count):
                if current_block_timestamp:
                    formatted_time = current_block_timestamp.strftime("%d-%m-%Y")
                else:
                    formatted_time = "no block time available"
                progress_bar.set_description(
                    f"Current block: {current} ({formatted_time}), blocks in a scan batch: {chunk_size}, events "
                    f"processed in a batch {events_count}")
                progress_bar.update(chunk_size)

            # Run the scan
            result, total_chunks_scanned = scanner.scan(start_block, end_block, progress_callback=_update_progress)
        state.save()
        duration = time.time() - start
        print(
            f"Scanned total {len(result)} Transfer events, in {duration} seconds, total {total_chunks_scanned} chunk "
            f"scans performed")
