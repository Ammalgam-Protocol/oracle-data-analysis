#!/usr/bin/env python3

import sys
import os

# Add the parent directory of the current file to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import argparse
import logging
import yaml
from src.local_node.scanner_runner import ScannerRunner
from src.uniswap_v2_pair_abi import UNISWAP_V2_PAIR_ABI

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


def load_config(config_file):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)


def run_scanner(config):
    logger.info(f"{config['blocks_to_scan']}")
    first_block = config['blocks_to_scan']['first']
    last_block = config['blocks_to_scan']['last']
    # Check if NODE_URL environment variable is set
    if 'NODE_URL' in os.environ:
        # Output a warning message if NODE_URL is set
        node_url = os.environ.get('NODE_URL')
        print(f"WARNING: NODE_URL environment variable is set. ignoring config file and setting it to {node_url}")
    else:
        # Output an info message if NODE_URL is not set
        node_url = config['node_url']
        print("INFO: NODE_URL environment variable is not set. You can set it to customize the node URL.")

    # Access the node_url from the config dictionary
        
    contract_address = config['contract_address']
    output_filename = config['output_filename']

    # Run the scanner
    ScannerRunner.run_scanner(output_filename, first_block, node_url, UNISWAP_V2_PAIR_ABI, contract_address, last_block = last_block)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the scanner and save data locally from the blockchain for further processing")
    parser.add_argument('-c', '--config', type=str, required=True, help='Path to the configuration file')
    
    # Customize the error message for missing required arguments
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()

    config = load_config(args.config)
    run_scanner(config)
