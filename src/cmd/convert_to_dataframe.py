#!/usr/bin/env python3

import sys
import os

# Add the parent directory of the current file to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


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

def main(json_state_file, output_file=None):
    json_state = JSONifiedState(json_state_file)
    json_state.restore()
    state = json_state.state
    state_df = ProcessStateToDF.process_state(state["blocks"], None)

    if output_file is None:
        output_file = os.path.splitext(json_state_file)[0] + '.pkl'

    save_dataframe_to_pickle(state_df, output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert JSON state file to a pickle file")
    parser.add_argument('json_state_file', type=str, help='Path to the JSON state file')
    parser.add_argument('output_file', type=str, nargs='?', help='Optional output pickle file name')

    # Customize the error message for missing required arguments
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()

    main(args.json_state_file, args.output_file)
