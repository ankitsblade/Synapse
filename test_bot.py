import json
import os

# --- Import the core processing function from your main application file ---
# This assumes you have saved your main workflow script as `main.py`.
try:
    from main import process_code_analysis_request
except ImportError:
    print("Error: Could not import 'process_code_analysis_request' from main.py.")
    print("Please make sure your main application file is saved as 'main.py' in the same directory.")
    exit()

# --- Configuration ---
# File paths for the sample inputs.
QUERY_FILE_PATH = "query.txt"
CODE_FILE_PATH = "sample_code.py"

# --- 1. Create Sample Input Files (if they don't exist) ---
def create_sample_files():
    """Creates default query and code files for testing purposes."""
    if not os.path.exists(QUERY_FILE_PATH):
        print(f"Creating sample query file: {QUERY_FILE_PATH}")
        with open(QUERY_FILE_PATH, "w") as f:
            f.write("This function is hard to read. Can you add type hints and a docstring to explain what it does?")

    if not os.path.exists(CODE_FILE_PATH):
        print(f"Creating sample code file: {CODE_FILE_PATH}")
        with open(CODE_FILE_PATH, "w") as f:
            f.write("""
def process_data(user_list, threshold):
    results = []
    for user in user_list:
        if user['age'] > threshold:
            results.append(user['name'])
    return results
""")

# --- 2. Main Testing Function ---
def test_bot_logic():
    """
    Reads data from files, calls the processing function directly, and prints the response.
    """
    print("--- Starting Bot Logic Test ---")
    
    # Ensure sample files exist for the test
    create_sample_files()

    # Read the user query and code content from the files.
    try:
        with open(QUERY_FILE_PATH, "r") as f:
            user_query = f.read()
        with open(CODE_FILE_PATH, "r") as f:
            code_content = f.read()
        print("Successfully read query and code from local files.")
    except FileNotFoundError as e:
        print(f"Error: Could not find a required file. {e}")
        return

    # Construct the payload dictionary, just like the webhook would receive.
    payload = {
        "user_query": user_query,
        "code_file_content": code_content
    }

    print("\n--- Calling the process_code_analysis_request function directly ---")
    print("Input Payload:")
    print(json.dumps(payload, indent=2))

    try:
        # Directly call the imported function with the payload.
        # This bypasses the need for a running web server.
        response = process_code_analysis_request(payload)

        print("\n--- Received Structured Response from Bot Logic ---")
        # Pretty-print the JSON response from the function.
        print(json.dumps(response, indent=2))

    except Exception as e:
        print(f"\n--- An Error Occurred During Bot Processing ---")
        print(f"Error details: {e}")

# --- Run the Test ---
if __name__ == "__main__":
    test_bot_logic()

# To use this script:
# 1. Save your main workflow file (with the FastAPI code) as `main.py`.
# 2. Save this testing script as `test_bot.py` in the same directory.
# 3. Make sure you have a `.env` file with your NVIDIA_API_KEY.
# 4. Run this testing script directly from your terminal: `python test_bot.py`
# 5. You do NOT need to run the `uvicorn` server for this test.
