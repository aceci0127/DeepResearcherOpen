"""
In this file, we will create a function that will create sub queries optimized for internet search.
"""
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client_openai = OpenAI(api_key=OPENAI_API_KEY)

with open("/Users/alfredoceci/Desktop/ATHENA SRL.l/CODING/SearchGPTonATHENA/db/prompts/subqueries.txt", "r") as file:
    prompt = file.read()

def subqueries_generator(query):
    response = client_openai.chat.completions.create(
        model="gpt-4o-mini",
         messages=[
            {"role": "system", "content": f"{prompt}"},
            {"role": "user", "content": f"\n\n\n--USER QUESTION:{query}\n\nSUBQUERIES:"}
        ],
        temperature=0.1
        )
    answer = response.choices[0].message.content
    sub_queries_list = [line.split('# ', 1)[-1] for line in answer.splitlines() if line.strip()]
    return sub_queries_list

if False:
    query = "Which companies uses or produces product with paper theraforming?"
    subqueries = subqueries_generator(query)
    print(subqueries)