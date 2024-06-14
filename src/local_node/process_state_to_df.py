import time
from logging import error, info
from typing import Callable
from unittest import TestCase

import pandas as pd
from pandas import DataFrame
from tqdm import tqdm


class ProcessStateToDF:
    RESERVE_KEYS = {'reserve0', 'reserve1'}
    SWAP_KEYS = {'sender', 'to', 'amount0In', 'amount1In', 'amount0Out', 'amount1Out'}

    @staticmethod
    def get_progress_callback(blocks: int) -> Callable:
        with tqdm(total=blocks, ascii=True) as progress_bar:
            def update_callback(current, chunk_size):
                progress_bar.set_description(f'Current block: {current}')
                progress_bar.update(chunk_size)
        return update_callback


    @classmethod
    def process_state(cls, data: dict, test_self: TestCase) -> DataFrame:
        swaps = []
        reserve0 = 0
        reserve1 = 0
        start = time.time()
        blocks = sorted(data.keys())
        progress_callback = cls.get_progress_callback(len(blocks))
        print(f"data = {data}")
        for block in sorted(data.keys()):
            current_block = block
            progress_callback(current_block, 1)
            txns_list = [data[block][hash_key] for hash_key in data[block]]
            for txn_dict in txns_list:
                reserve0, reserve1 = cls.process_txn(block, reserve0, reserve1, swaps, test_self, txn_dict)
        duration = time.time() - start
        info(f"Scanned blocks in {duration} seconds")
        return pd.DataFrame(swaps)

    @classmethod
    def process_txn(cls, block, reserve0, reserve1, swaps, test_self, txn_dict):
        txns = sorted((txn_key for txn_key in txn_dict), key=int)
        while len(txns) > 0:
            if len(txns) > 1:
                if txn_dict[txns[0]].keys() == cls.RESERVE_KEYS and txn_dict[txns[1]].keys() == cls.SWAP_KEYS:
                    txn1 = txns.pop(0)
                    txn2 = txns.pop(0)
                    reserve0, reserve1 = cls.process_swap(
                        block, reserve0, reserve1, swaps, txn_dict, txn1, txn2)
                elif txn_dict[txns[0]].keys() == cls.RESERVE_KEYS:
                    reserve0, reserve1 = cls.process_reserve(reserve0, reserve1, txns.pop(0), txn_dict)
                else:
                    msg = f'Unknown txns {txn_dict[txns.pop(0)]}'
                    error(msg)
                    test_self.fail(msg)
            elif len(txns) == 1:
                if txn_dict[txns[0]].keys() == cls.RESERVE_KEYS:
                    reserve0, reserve1 = cls.process_reserve(reserve0, reserve1, txns.pop(0), txn_dict)
                else:
                    msg = f'Unknown txns {txn_dict[txns.pop(0)]}'
                    error(msg)
                    test_self.fail(msg)
        print(f"returing {reserve0} and {reserve1}")            
        return reserve0, reserve1

    @classmethod
    def process_reserve(cls, reserve0, reserve1, txn, txn_dict):
        reserve = txn_dict[txn]
        reserve0, reserve1 = cls._process_reserves(reserve0, reserve1, reserve)
        return reserve0, reserve1

    @classmethod
    def process_swap(cls, block, reserve0, reserve1, swaps, txn_dict, txn1, txn2):
        reserve = txn_dict[txn1]
        swap = txn_dict[txn2]
        swap['block'] = block
        swap['reserve0'] = reserve0
        swap['reserve1'] = reserve1
        swaps.append(swap)
        reserve0 += swap['amount0In'] - swap['amount0Out']
        reserve1 += swap['amount1In'] - swap['amount1Out']
        reserve0, reserve1 = cls._process_reserves(reserve0, reserve1, reserve)
        return reserve0, reserve1

    @classmethod
    def _process_reserves(cls, reserve0, reserve1, entry):
        _reserve0 = entry['reserve0']
        _reserve1 = entry['reserve1']
        if _reserve0 > reserve0 and _reserve1 > reserve1:
            info(f"Mint {_reserve0-reserve0}, {_reserve1-reserve1}")
        elif _reserve0 < reserve0 and _reserve1 < reserve1:
            info(f"Burn {reserve0 - _reserve0}, {reserve1 - _reserve1}")
        elif _reserve0 != reserve0 or _reserve1 != reserve1:
            error(f"Not sure what this is, "
                  f"\n\treserve0: {reserve0} -> {_reserve0}"
                  f"\n\treserve1: {reserve1} -> {_reserve1}")
        return _reserve0, _reserve1

