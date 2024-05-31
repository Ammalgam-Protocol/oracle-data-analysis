# Oracle Data Analysis

This code was used o better understand how different versions of oracles approximate a price of a
trading pair at a given time. For a first pass I looked at the Uniswap V2 ETH-POOL pair.

I looked at two methods of collecting data, pulling events from a [local node](src/local_node) and
using [The Graph](https://thegraph.com). Using a node to pull events was very slow, but it was able
to  complete prior to me wrapping up the code to pull indexed data from The Graph.

Much of main flow of code was hacked together in test files. More work is required to make this a 
finished production product.

## Load Notebook

This repo uses [Poetry](https://python-poetry.org/) to manage dependencies within a python virtual
environment. You can install the dependencies and run [jupyter-lab](https://jupyter.org/) with the
comands.

```bash
poetry install
poetry run jupyter-lab
```

from jupyter-lab you can navigate to the [notebook](data-analysis.ipynb). 


## Overview - Scanner Script Runner

This utility is designed to scan Uniswap V2 events within a specified range of Ethereum blocks and output the results to a local JSON file. This file can then be used for further processing

## Usage

There is a script runner file located here [run_scanner](src/cmd/run_scanner.py). To run the scanner utility, use the following command:

```bash
./run_scanner.py -c ./uni-eth.yml
```

## Configuration File (uni-eth.yml)

```yaml
# Uniswap V2 Configuration File

# Description: Configuration file for the Uniswap V2 scanner utility.
# This file specifies parameters such as the range of blocks to scan,
# the Ethereum node URL, the contract address, and the output filename.

blocks_to_scan:
  # Specifies the range of blocks to scan.
  # 'first' denotes the starting block number.
  # 'last' denotes the ending block number.
  first: 19008564
  last: 19550182

# Specifies the URL of the Ethereum node API to use.
# If the 'NODE_URL' environment variable is set, it will override this value.
node_url: ${NODE_URL}

# Specifies the address of the Uniswap V2 contract.
contract_address: "0xd3d2E2692501A5c9Ca623199D38826e513033a17"

# Specifies the name of the output JSON file.
output_filename: uni_eth_state_v0.json
