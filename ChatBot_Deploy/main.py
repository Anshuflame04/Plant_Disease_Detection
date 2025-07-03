from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os

# Set your API key (ensure it's kept secure and not hard-coded in production)
os.environ["GOOGLE_API_KEY"] = "AIzaSyDncRUAl5s2Y6g6uvmhDCBUWGgf2bS33vY"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your React app's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the model
try:
    model = genai.GenerativeModel("models/gemini-2.0-flash,")
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Model initialization failed: {str(e)}")

# Request body model for input validation
class ChatRequest(BaseModel):
    prompt: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # Define the context for the AI with explicit formatting instructions
    context = (
        "You are Anshu AI, a virtual assistant designed to answer questions about crops, plants, pesticides, and everything related to agriculture. "
        "When answering, please provide information in clearly defined bullet points and numbered lists without using asterisks or other symbols. "
        "Make sure to leave adequate spacing between points for better readability."
    )
    
    prompt = f"{context}\n\nUser: {request.prompt}\nAnshu AI:"
    
    try:
        response = model.generate_content(prompt)
        structured_response = format_response(response.text)
        return {"response": structured_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

def format_response(response: str) -> str:
    # Replace formatting symbols and clean up response
    response = response.replace('* ', '- ').replace('**', '')  # Replace asterisks with dashes for bullets
    response = response.replace('\n-', '\n\n-')  # Add spacing for better readability
    response = response.strip()  # Clean up any leading/trailing whitespace
    return response


# Add a basic route for testing the API
@app.get("/")
def read_root():
    return {"message": "Welcome to the Anshu Chatbot API"}
