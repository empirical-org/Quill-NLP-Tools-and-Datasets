import argparse
import json
import importlib.util
import sys
import os

# Set up argument parsing
parser = argparse.ArgumentParser(description="Convert Python passage to JSON file.")
parser.add_argument(
    "data_file_path", type=str, help="Path to the Python data file (e.g., data.py)"
)

# Parse the command-line arguments
args = parser.parse_args()

# Dynamically load the module specified by the command line argument
module_name = "data_module"
module_spec = importlib.util.spec_from_file_location(module_name, args.data_file_path)
if module_spec is None:
    print("Can't find the specified data file.", file=sys.stderr)
    sys.exit(1)

module = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(module)

# Extract the passage
try:
    passage = module.passage
except AttributeError:
    print(
        "The specified module does not contain a 'passage' variable.", file=sys.stderr
    )
    sys.exit(1)

# Generate the output file name based on the imported file name
base_name = os.path.basename(args.data_file_path)
output_file_name = os.path.splitext(base_name)[0] + ".json"

# Write the passage to a JSON file
with open(output_file_name, "w") as json_file:
    json.dump(passage, json_file, indent=4)

print(f"Passage has been successfully written to {output_file_name}")
