#!/usr/bin/env python3

import sys
import os
from decimal import Decimal, getcontext, ROUND_UP



# Add the parent directory of the current file to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import yaml
import hashlib
import pandas as pd
import argparse
import logging
from src.local_node.event_scanner import JSONifiedState
from src.local_node.process_state_to_df import ProcessStateToDF




logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))





def save_dataframe_to_pickle(state_df, output_file):
    # Save DataFrame to pickle file
    state_df.to_pickle(output_file)
    logger.info(f"DataFrame saved to {output_file}")

    # Calculate checksum of the pickle file
    with open(output_file, "rb") as f:
        pkl_checksum = hashlib.md5(f.read()).hexdigest()
        logger.info(f"Checksum of {output_file}: {pkl_checksum}")

def save_dataframe_to_csv(state_df, output_file):
    # Save DataFrame to CSV file
    state_df.head()
    state_df.to_csv(output_file)
    logger.info(f"DataFrame saved to {output_file}")

    # Calculate checksum of the CSV file
    with open(output_file, "rb") as f:
        csv_checksum = hashlib.md5(f.read()).hexdigest()
        logger.info(f"Checksum of {output_file}: {csv_checksum}")



def convert_to_standard_units(value, decimals):    
    if Decimal(value) == 0: ## incase it comes thru as a string - probably overkill for this context.
        return '0'
    
    getcontext().prec = decimals + 10  # Set precision to accommodate the full number plus decimals
    value = Decimal(value)
    factor = Decimal(10) ** Decimal(decimals)
    result = value / factor
    q_result = result.quantize(Decimal(10) ** -decimals, rounding=ROUND_UP)
    return q_result
     

def convert_to_dataframe(state, pair, decimals):
    records = []

    for block_number, transactions in state.items():
        for txhash, logs in transactions.items():
            pre_swap_reserve0 = pre_swap_reserve1 = None
            post_swap_reserve0 = post_swap_reserve1 = None

            for log_index, event_data in sorted(logs.items(), key=lambda x: int(x[0])):
                if 'reserve0' in event_data and 'reserve1' in event_data:
                    pre_swap_reserve0 = event_data['reserve0']
                    pre_swap_reserve1 = event_data['reserve1']

                if 'amount0In' in event_data or 'amount1In' in event_data:
                    

                    amount0In = event_data.get("amount0In", 0)
                    amount1In = event_data.get("amount1In", 0)
                    amount0Out = event_data.get("amount0Out", 0)
                    amount1Out = event_data.get("amount1Out", 0)
                    #print(f"Its a SWAP baby {pair[0]} IN {amount0In}  OUT {amount0Out}")
                    #print(f"Its a SWAP baby {pair[1]} IN {amount1In} OUT {amount1Out}")

                    # Convert reserves and swap amounts to standard units
                    pre_swap_reserve0_standard = convert_to_standard_units(pre_swap_reserve0, decimals[pair[0]])
                    pre_swap_reserve1_standard = convert_to_standard_units(pre_swap_reserve1, decimals[pair[1]])                    
                    amount0In_standard = convert_to_standard_units(amount0In, decimals[pair[0]])
                    amount1In_standard = convert_to_standard_units(amount1In, decimals[pair[1]])
                    amount0Out_standard = convert_to_standard_units(amount0Out, decimals[pair[0]])
                    amount1Out_standard = convert_to_standard_units(amount1Out, decimals[pair[1]])

                    # Calculate post-swap reserves in standard units
                    post_swap_reserve0 = pre_swap_reserve0  + amount0In - amount0Out
                    post_swap_reserve1  = pre_swap_reserve1 + amount1In - amount1Out


                    post_swap_reserve0_standard = convert_to_standard_units(post_swap_reserve0, decimals[pair[0]])
                    post_swap_reserve1_standard = convert_to_standard_units(post_swap_reserve1, decimals[pair[1]])
                    # Calculate the price of UNI in USDC
                     
                    pair0_cost_per_token = post_swap_reserve0_standard / post_swap_reserve1_standard
                    pair1_cost_per_token = post_swap_reserve1_standard / post_swap_reserve0_standard
                    
                    record = {
                        "block_number": block_number,
                        "transaction_hash": txhash,
                        "log_index": log_index,
                        "sender": event_data.get("sender", ""),
                        "to": event_data.get("to", ""),
                        "amount0In": amount0In_standard,
                        "amount1In": amount1In_standard,
                        "amount0Out": amount0Out_standard,
                        "amount1Out": amount1Out_standard,
                        "pre_swap_reserve0": pre_swap_reserve0,
                        "pre_swap_reserve1": pre_swap_reserve1,
                        "post_swap_reserve0": post_swap_reserve0,
                        "post_swap_reserve1": post_swap_reserve1,
                        
                        "pair0": pair[0],
                        "pair0_cost": pair0_cost_per_token,
                        "pair1": pair[1],
                        "pair1_cost": pair1_cost_per_token,
                    }

                    records.append(record)

    df = pd.DataFrame(records)
    return df   

def main(config_file, output_file=None, output_format='pkl'):
    # Load configuration
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)

    # Read JSON state file
    json_state = JSONifiedState(config['output_filename'])
    json_state.restore()
    state = json_state.state
    pair = [config['pair']['0'], config['pair']['1']]
    decimals = {config['pair']['0']: config['decimals'][config['pair']['0']], 
                config['pair']['1']: config['decimals'][config['pair']['1']]}

    state_df = convert_to_dataframe(state["blocks"], pair, decimals)

    if output_file is None:
        output_file = os.path.splitext(config['output_filename'])[0] + f'.{output_format}'

    if output_format == 'csv':
        save_dataframe_to_csv(state_df, output_file)
    else:
        save_dataframe_to_pickle(state_df, output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert JSON state file to a pickle or CSV file")
    parser.add_argument('config_file', type=str, help='Path to the configuration file')
    parser.add_argument('output_file', type=str, nargs='?', help='Optional output file name')
    parser.add_argument('-format', choices=['csv', 'pkl'], default='pkl', help='Output format: csv or pkl (default: pkl)')

    # Customize the error message for missing required arguments
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    main(args.config_file, args.output_file, args.format)
