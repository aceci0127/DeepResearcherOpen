"""
In this file, we will create a function that will be responsible take the search results and use the chat function to generate and return an answer.
"""
from openai import OpenAI
import os
from research import Searcher
from chat import chat
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client_openai = OpenAI(api_key=OPENAI_API_KEY)

def rag(query):
    results = Searcher(query, 2).run()
    response = chat(query, results)
    return response

if True:
    #query = "Which is the football team that has the highest probability to win SerieA this year?"
    query = input("Ask Athena: ")
    response = rag(query)
    print(response)