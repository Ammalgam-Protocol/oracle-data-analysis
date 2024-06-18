#!/bin/bash

# Function to run a command and print explanation
run_command() {
  echo -e "\n# $1"
  echo "$2"
  eval "$2"
  echo -e "\n"
}

# Explanations and commands
command1_explanation="Extract data from on-chain and save it to disk for uni-eth pair, check uni-eth.yml for configuration"
command1="./run_scanner.py -c ./uni-eth.yml"

command3_explanation="Convert data configured in the uni-usdc.yml file to CSV format and save to specified path"
command3="./convert_to_dataframe.py ./uni-usdc.yml ../../uni_usdc_pair/data/uni_usdc_06132024.csv -format=csv"

command4_explanation="Convert data configured in the uni-eth.yml file to CSV format and save to specified path"
command4="./convert_to_dataframe.py ./uni-eth.yml ../../uni_usdc_pair/data/uni_eth_06182024.csv -format=csv"

command5_explanation="Convert configured in the uni-usdc.yml and save DataFrame in Pickle format"
command6="./convert_to_dataframe.py ./uni-usdc.yml ../../uni_usdc_pair/data/uni_usdc.pkl"

# Comment out the command you want to run
run_command "$command3_explanation" "$command3"
#run_command "$command2_explanation" "$command2"
#run_command "$command3_explanation" "$command3"

