#!/usr/bin/env python3

import json
import os
import datetime
from web3 import Web3
import argparse

CACHE_FILE = "block_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def date_to_block(web3: Web3, target_date: datetime.datetime) -> int:
    target_timestamp = int(target_date.timestamp())
    
    latest_block = web3.eth.get_block('latest')
    latest_block_number = latest_block['number']
    latest_block_timestamp = latest_block['timestamp']
    
    # Binary search to find the closest block
    low = 0
    high = latest_block_number
    
    while low <= high:
        mid = (low + high) // 2
        mid_block = web3.eth.get_block(mid)
        mid_block_timestamp = mid_block['timestamp']
        
        if mid_block_timestamp < target_timestamp:
            low = mid + 1
        elif mid_block_timestamp > target_timestamp:
            high = mid - 1
        else:
            return mid  # Exact match

    # Determine the closest block (low or high)
    low_block = web3.eth.get_block(low)
    high_block = web3.eth.get_block(high)
    
    if abs(low_block['timestamp'] - target_timestamp) < abs(high_block['timestamp'] - target_timestamp):
        return low_block['number']
    else:
        return high_block['number']

def main():
    parser = argparse.ArgumentParser(description="Convert date to Ethereum block number.")
    parser.add_argument('date', type=str, help="The date to convert (YYYY-MM-DD).")
    args = parser.parse_args()

    # Parse the date as UTC
    target_date = datetime.datetime.strptime(args.date, "%Y-%m-%d")
    target_date = target_date.replace(tzinfo=datetime.timezone.utc)
    
    # Load cache
    cache = load_cache()
    
    # Check if date is in cache
    if args.date in cache:
        print(f"Block number for {args.date} (cached): {cache[args.date]}")
        return
    
    # Initialize web3
    node_url = node_url = os.environ.get('NODE_URL')
    web3 = Web3(Web3.HTTPProvider(node_url))

    # Find the block number
    block_number = date_to_block(web3, target_date)
    
    # Update cache
    cache[args.date] = block_number
    save_cache(cache)
    
    print(f"The closest block to {args.date} is {block_number}")

if __name__ == "__main__":
    main()
