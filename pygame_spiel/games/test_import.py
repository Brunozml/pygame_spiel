from pathlib import Path

# Get the current directory of the script being run
current_dir = Path(__file__).parent
print("Directory:", current_dir)

# Get the project root directory
project_root = Path(__file__).resolve().parents[1]
print("Project Root:", project_root)
