import unittest
import subprocess
import filecmp
import os
import pandas as pd

SCRIPT_NAME = "convert_to_dataframe.py"

class TestConvertToDataFrame(unittest.TestCase):

    def setUp(self):
        # Adjust paths to be relative to the script directory
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.cmd_dir = os.path.abspath(os.path.join(self.script_dir, '..'))
        self.config_file = os.path.join(self.script_dir, 'test_config.yml')
        self.generated_output_file = os.path.join(self.script_dir, 'generated_output.csv')
        self.reference_output_file = os.path.join(self.script_dir, 'reference_output.csv')

        # Ensure the reference file exists
        self.assertTrue(os.path.exists(self.reference_output_file), f"Reference file {self.reference_output_file} does not exist")
        # Ensure the config file exists
        self.assertTrue(os.path.exists(self.config_file), f"Config file {self.config_file} does not exist")

    def test_output_file_generation(self):
        # Command to run the cd.py script
        command = ['python3', os.path.join(self.cmd_dir, SCRIPT_NAME), self.config_file, self.generated_output_file, '-format', 'csv']
        
        # Print the command for debugging
        #print("Executing command:", " ".join(command))
        
        # Run the cd.py script with the specified config file and output format
        result = subprocess.run(command, capture_output=True, text=True)
        
        # Print the output for debugging
        print("stdout:", result.stdout)
        #print("stderr:", result.stderr)
        
        # Check that the process completed successfully
        self.assertEqual(result.returncode, 0, f"Process failed with output: {result.stderr}")

        # Check that the generated file exists
        self.assertTrue(os.path.exists(self.generated_output_file), f"Generated file {self.generated_output_file} does not exist")
        # Compare the generated file with the reference file
        self.compare_csv_files(self.generated_output_file, self.reference_output_file)

        
    

    def compare_csv_files(self, generated_file, reference_file):
        generated_df = pd.read_csv(generated_file)
        reference_df = pd.read_csv(reference_file)

        # Ensure both DataFrames have the same shape
        self.assertEqual(generated_df.shape, reference_df.shape, f"Generated file shape {generated_df.shape} does not match reference file shape {reference_df.shape}")

        # Compare each element
        mismatches = []
        for row in range(generated_df.shape[0]):
            for col in generated_df.columns:
                
                if generated_df.at[row, col] != reference_df.at[row, col]:
                    mismatches.append((row, col, generated_df.at[row, col], reference_df.at[row, col]))

        # Print detailed mismatch information
        for mismatch in mismatches:
            
            row, col, gen_val, ref_val = mismatch
            print(f"Mismatch at row {row}, column '{col}': generated value = {gen_val}, reference value = {ref_val}")

        # Assert no mismatches
        self.assertTrue(len(mismatches) == 0, f"{len(mismatches)} mismatches found between generated file and reference file")

    def tearDown(self):
        # Clean up the generated file after the test
        if os.path.exists(self.generated_output_file):
            self.assertTrue(os.path.exists(self.generated_output_file), f"Generated file {self.generated_output_file} does not exist")
            os.remove(self.generated_output_file)

if __name__ == '__main__':
    unittest.main()
