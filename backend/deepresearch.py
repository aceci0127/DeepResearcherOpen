"""
In this file, we will create a function that will be responsible for handling the chat's responses.
"""
from openai import OpenAI
import os
from dotenv import load_dotenv
import trafilatura
import requests
load_dotenv()

brave_api_key = os.getenv('BRAVE_API_KEY')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
client_deepseek = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def brave_search(query, key):
    try:
        res = requests.get(
            "https://api.search.brave.com/res/v1/web/search", 
            params={"q": query}, 
            headers={"X-Subscription-Token": key, "Accept": "application/json"},
            timeout=10  # opzionale, per evitare richieste pendenti
        )

        res.raise_for_status()  # solleva eccezioni per errori HTTP

        json_data = res.json()

        # Controllo che la chiave 'web' e 'results' siano presenti
        if "web" not in json_data or "results" not in json_data["web"]:
            print(f"[BraveSearch] Unexpected response format: {json_data}")
            return []

        urls = [item['url'] for item in json_data["web"]["results"] if 'url' in item]
        return urls

    except requests.exceptions.RequestException as e:
        print(f"[BraveSearch] Request failed: {e}")
        return []

    except ValueError as e:
        print(f"[BraveSearch] Invalid JSON: {e}")
        return []

    except KeyError as e:
        print(f"[BraveSearch] Missing expected key: {e}")
        return []

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

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
prompt_dir = os.path.join(BASE_DIR, 'db', 'prompts')
with open(os.path.join(prompt_dir, "reports.txt"), "r") as file:
    reports_prompt = file.read()
with open(os.path.join(prompt_dir, "summary.txt"), "r") as file:
    summary_prompt = file.read()
with open(os.path.join(prompt_dir, "answer.txt"), "r") as file:
    answer_prompt = file.read()
with open(os.path.join(prompt_dir, "subqueries.txt"), "r") as file:
    subqueries_prompt = file.read()
with open(os.path.join(prompt_dir, "reasoner.txt"), "r") as file:
    reasoner_prompt = file.read()

def open_url(url):
    body = trafilatura.fetch_url(url)
    content = trafilatura.extract(body)
    return content

def search_engine(query):
    urls = brave_search(query, brave_api_key)
    bodies = ""
    for url in urls[:5]:
        content = open_url(url)
        if content:
            bodies += content[:2000]
            bodies += "\n\n"
    return bodies

def subqueries(query):
    subqueries = []
    user_data = "User query: " + str(query)
    data = chat(reasoner_prompt, user_data)
    reasoning_data = "Data: " + str(data)
    subqueries = chat(subqueries_prompt, reasoning_data)
    sub_queries_list = [line.split('# ', 1)[-1] for line in subqueries.splitlines() if line.strip()]
    return sub_queries_list

def generate_summary(content, query):
    # Ask the LLM to summarize the content based on the user query
    website_data = f"Website Content: {content}\nUser Query: {query}\n"
    summary = chat(summary_prompt, website_data)
    return summary

def generate_report(summaries):
    # Ask the LLM to generate a structured report from the summaries
    summaries_data = f" Summaries: \n{str(summaries)}"
    report = chat(reports_prompt, summaries_data)
    return report

def sub_agentic_search_and_report(query):
    urls = brave_search(query, brave_api_key)  # Note: ensure correct spelling of brave_search if needed.
    bodies = ""
    # Process each URL (limit to first 5)
    for url in urls[:5]:
        content = open_url(url)
        if content:
            bodies += "Summary: \n"
            summary = generate_summary(content, query)
            bodies += summary + "\n\n"
    report = generate_report(bodies)
    # Combine all reports
    return {"Report": report, "Bodies": bodies}

import concurrent.futures

def full_agentic_search(query):
    subs = subqueries(query)
    final_content = ""
    
    # Use ThreadPoolExecutor to parallelize the subqueries processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(5, len(subs))) as executor:
        # Submit all tasks and map them to their corresponding subquery
        future_to_sub = {executor.submit(sub_agentic_search_and_report, sub): sub for sub in subs}
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_sub):
            result = future.result()
            final_content += result['Report']
            final_content += "\n\n"
    
    return final_content

def agent_fast_reply(query):
    final_content = full_agentic_search(query)
    return final_content