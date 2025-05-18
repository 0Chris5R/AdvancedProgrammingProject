from google import genai
from dotenv import load_dotenv
import os
from typing import List
import enum

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.0-flash", contents="Explain how AI works in a few words"
)
print(response.text)





class Instrument(enum.Enum):
    PERCUSSION = "Percussion"
    STRING = "String"
    WOODWIND = "Woodwind"
    BRASS = "Brass"
    KEYBOARD = "Keyboard"

# Updated schema: Expect a list of Instrument enums
from pydantic import BaseModel

class InstrumentResponse(BaseModel):
    instruments: List[Instrument]

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model='gemini-2.0-flash',
    contents='What type of instruments is a piano considered?',
    config={
        'response_mime_type': 'application/json',
        'response_schema': InstrumentResponse,
    },
)

print(response.candidates[0].content)