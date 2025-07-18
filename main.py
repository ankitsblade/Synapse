import os
from pydantic import BaseModel, Field
from typing import Type
from fastapi import FastAPI
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from dotenv import load_dotenv

# --- Load environment variables from .env file ---
# This line looks for a .env file in the same directory and loads it.
load_dotenv()

# --- IMPORTANT: API Key Setup ---
# This will now read the NVIDIA_API_KEY from your .env file.
# Create a .env file in the same directory as this script with the following content:
# NVIDIA_API_KEY="nvapi-your_key_here"
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
if not NVIDIA_API_KEY:
    print("ERROR: NVIDIA_API_KEY not found in environment or .env file.")
    # In a real app, you would exit or handle this error properly.
    # For this example, we'll proceed, but the LLM call will fail.

# --- 1. Initialize FastAPI App ---
app = FastAPI(
    title="Synapse",
    description="An API that uses an LLM to analyze and refactor code collaboratively.",
    version="1.0.0"
)

# --- 2. Define API Data Structures (Pydantic Models) ---
# This Pydantic model validates the incoming JSON data from the webhook.
class CodeAnalysisRequest(BaseModel):
    """Represents the data received from the webhook."""
    user_query: str = Field(description="The natural language query from the user about the code.")
    code_file_content: str = Field(description="The raw string content of the code file to be analyzed.")

# This Pydantic model defines the exact JSON format we want the LLM to return.
class CodeAnalysisResponse(BaseModel):
    """The structured response from the LLM after analyzing the code."""
    suggestion: str = Field(description="A clear, concise explanation of the changes made or suggestions for the code.")
    edited_code: str = Field(description="The complete, modified code with the suggestions applied.")

# --- 3. The Core Processing Logic ---
def process_code_analysis_request(request_data: dict):
    """
    This function contains the core logic for processing the request.
    It uses LangChain to prompt an LLM and parse the response.
    """
    print("--- Setting up LangChain with Pydantic Output Parser ---")
    # Initialize the LLM to use the NVIDIA endpoint.
    llm = ChatOpenAI(
        model="meta/llama3-70b-instruct", 
        temperature=0,
        api_key=NVIDIA_API_KEY,
        base_url="https://integrate.api.nvidia.com/v1"
    )

    output_parser = PydanticOutputParser(pydantic_object=CodeAnalysisResponse)

    # Updated system prompt with stricter JSON formatting rules.
    system_prompt = """
    You are an expert code analysis and refactoring assistant.
    Your task is to receive a user's query about a piece of code, analyze it,
    and provide a suggestion along with the edited code.
    You MUST respond in the JSON format specified. Do not add any extra text or explanations outside of the JSON structure.
    The value for the "edited_code" field MUST be a valid JSON string, with all newlines and special characters properly escaped (e.g., using \\n for newlines).
    """

    user_prompt_template = """
    User Query: {user_query}

    --- START OF CODE FILE ---
    {code_file_content}
    --- END OF CODE FILE ---

    {format_instructions}
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_prompt_template)
    ])

    format_instructions = output_parser.get_format_instructions()
    chain = prompt | llm | output_parser

    print("--- Invoking the LLM and Parsing the Response ---")
    try:
        response = chain.invoke({
            "user_query": request_data["user_query"],
            "code_file_content": request_data["code_file_content"],
            "format_instructions": format_instructions
        })
        print("Successfully received and parsed structured response from LLM.")
        return response.model_dump()

    except Exception as e:
        print(f"An error occurred while invoking the LLM or parsing the response: {e}")
        return {"error": "Failed to get a valid response from the AI model."}

# --- 4. Define the Webhook Endpoint ---
@app.post("/analyze-code", response_model=CodeAnalysisResponse)
def handle_code_analysis(request: CodeAnalysisRequest):
    """
    This is the webhook endpoint. It receives a POST request with a JSON body
    that matches the CodeAnalysisRequest model.
    """
    print("--- Webhook endpoint /analyze-code received a request ---")
    # The request object is already a validated Pydantic model.
    # We convert it to a dictionary to pass to the processing function.
    request_data = request.model_dump()
    
    # Call the existing processing logic
    response = process_code_analysis_request(request_data)
    
    return response

# To run this server:
# 1. Save the file as `main.py`.
# 2. Install necessary packages: `pip install fastapi uvicorn langchain-openai pydantic python-dotenv`
# 3. Create a `.env` file in the same directory with your NVIDIA_API_KEY.
# 4. Run from your terminal: `uvicorn main:app --reload`
# 5. The API will be available at http://127.0.0.1:8000/docs for interactive testing.