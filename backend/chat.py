"""
In this file, we will create a function that will be responsible for handling the chat's responses.
"""
from openai import OpenAI
import os
from research import Searcher
from subqueries_generator import subqueries_generator
from dotenv import load_dotenv
import trafilatura
from googleapiclient.discovery import build
load_dotenv()

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
client_deepseek = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def chat(prompt, context):
    response = client_deepseek.chat.completions.create(
        model="deepseek-chat",
         messages=[
            {"role": "system", "content": f"{prompt}"},
            {"role": "user", "content": f"{context}"}
        ],
        temperature=0.1
        )
    answer = response.choices[0].message.content
    return answer

prompt_dir = "/Users/alfredoceci/Desktop/ATHENA SRL.l/CODING/SearchGPTonATHENA/db/prompts/"
with open(prompt_dir + "answer.txt", "r") as file:
    init_prompt5 = file.read()
with open(prompt_dir + "subqueries.txt", "r") as file:
    init_prompt4 = file.read()
with open(prompt_dir + "reasoner.txt", "r") as file:
    init_prompt3 = file.read()


def google_search(query, **kwargs):
    api_key="AIzaSyCIxHYJn2INXTQc0NB9Mel5A8WiEtYAnnU"
    cse_id="d67999fcc3bea4cd7"
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=query, cx=cse_id, **kwargs).execute()
    urls = [item['link'] for item in res.get('items', [])]
    return urls

def open_url(url):
    body = trafilatura.fetch_url(url)
    content = trafilatura.extract(body)
    return content

def search_engine(query):
    urls = google_search(query)
    bodies = ""
    for url in urls[:5]:
        content = open_url(url)
        if content:
            bodies += content[:2000]
            bodies += "\n\n"
    return bodies

def subqueries(query):
    subqueries = []
    data_prompt = init_prompt3 + "User query: " + str(query)
    data = chat(data_prompt)
    subqueries_prompt = init_prompt4 + "Data: " + str(data)
    subqueries = chat(subqueries_prompt)
    sub_queries_list = [line.split('# ', 1)[-1] for line in subqueries.splitlines() if line.strip()]
    return sub_queries_list

def full_agentic_search(query):
    subs = subqueries(query)
    final_content=""
    for sub in subs:
        urls = google_search(sub)
        bodies = ""
        for url in urls[:5]:
            content = open_url(url)
            if content:
                bodies += content[:2000]
                bodies += "\n\n"
        final_content += bodies
        final_content += "\n\n"
    return final_content

def agent_fast_reply(query):
    final_content = full_agentic_search(query)
    final_prompt = init_prompt5 + "User query: " + str(query) + "Internet Results: " + str(final_content)
    answer = chat(final_prompt)
    return {"output": answer}