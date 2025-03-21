"""
In this file, we will create a function that will be responsible for handling the chat's responses.
"""
from openai import OpenAI
import os
from research import Searcher
from subqueries_generator import subqueries_generator
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client_openai = OpenAI(api_key=OPENAI_API_KEY)

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
client_deepseek = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

with open("/Users/alfredoceci/Desktop/ATHENA SRL.l/CODING/SearchGPTonATHENA/db/prompts/chatbase.txt", "r") as file:
    prompt = file.read()

def chat(query, text):
    response = client_deepseek.chat.completions.create(
    #response = client_openai.chat.completions.create(
        model="deepseek-reasoner",
        #model="gpt-4o-mini",
         messages=[
            {"role": "system", "content": f"{prompt}"},
            {"role": "user", "content": f"\n\n\n--USER QUESTION:{query}\n\n--TEXT EXTRACTED:{text}."}
        ],
        temperature=0.1
        )
    answer = response.choices[0].message.content
    return answer