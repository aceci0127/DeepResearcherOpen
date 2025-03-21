"""
This script is used to :
1. Create sub queries from the main query;
2. Search on google using the sub queries;
3. Open the urls returned by the search;
4. Split the content of the urls in chunks;
5. Calculate the similarity between the query and the chunks;
6. Return the results.

Something else that could be done to further improve the script would be to take all the chunks from all the results and calculate the similarity between the real query and all the chunks.
Then rerank the results and return the top k results.

Another approach to subsitute the chunks could be to summarize the content of the page based on the subquery. 
This could be done using the langchain_summarizer library.
I should test this.


Also, we need a more efficient way to search on the internet, the sub queries are a good idea but we need to find a way to get more relevant results.
"""

from googleapiclient.discovery import build
from langchain_text_splitters import RecursiveCharacterTextSplitter
import trafilatura
from dotenv import load_dotenv
import os
from calculate_similarity import calculate_similarity
from subqueries_generator import subqueries_generator
import concurrent.futures
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

class Searcher():
    def __init__(self, query, kx):
        self.query = query
        self.kx = kx  # Number of urls to search
        self.api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        self.cse_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        self.calculate_similarity = calculate_similarity
        self.subqueries_generator = subqueries_generator
        
        # Validate API credentials
        if not self.api_key or not self.cse_id:
            logging.error("Missing Google Search API credentials")
            raise ValueError("Missing Google Search API credentials. Please check your .env file.")

    def google_search(self, subquery, **kwargs):
        try:
            service = build("customsearch", "v1", developerKey=self.api_key)
            res = service.cse().list(q=subquery, cx=self.cse_id, **kwargs).execute()
            answer = [item['link'] for item in res.get('items', [])]
            logging.info(f"Found {len(answer)} URLs for subquery: {subquery}")
            return answer
        except Exception as e:
            logging.error(f"Error in google_search: {str(e)}")
            return []

    def open_url(self, url):
        try:
            logging.info(f"Fetching content from URL: {url}")
            body = trafilatura.fetch_url(url)
            if not body:
                logging.warning(f"Failed to fetch URL content: {url}")
                return None
                
            content = trafilatura.extract(body)
            if not content or len(content.strip()) < 100:  # Check for meaningful content
                logging.warning(f"Extracted content too short or empty: {url}")
                return None
                
            logging.info(f"Successfully extracted {len(content)} characters from {url}")
            return content
        except Exception as e:
            logging.error(f"Error in open_url for {url}: {str(e)}")
            return None

    def chunker(self, text, size, overlap):
        """
        This function will take in a text and return a list of chunks of the text.
        """
        # Check if text is valid before chunking
        if not text or not isinstance(text, str):
            logging.warning(f"Invalid text provided to chunker: {type(text)}")
            return []
            
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=size,
            chunk_overlap=overlap,
            length_function=len,
            is_separator_regex=False,
        )
        
        try:
            chunks = splitter.create_documents([text])
            logging.info(f"Created {len(chunks)} chunks from text of length {len(text)}")
            return chunks
        except Exception as e:
            logging.error(f"Error in chunker: {str(e)}")
            return []

    def process_url(self, url):
        try:
            content = self.open_url(url)
            if not content:
                return url, "No valid content could be extracted from this URL."
                
            chunks = self.chunker(content, 2000, 200)
            if not chunks:
                return url, "Content was retrieved but couldn't be properly chunked."
                
            # Log the number of chunks for debugging
            logging.info(f"Processing similarity for {len(chunks)} chunks from {url}")
            
            results = self.calculate_similarity(self.query, chunks, k=3)
            return url, results
        except Exception as e:
            logging.error(f"Error processing URL {url}: {str(e)}")
            return url, f"Error processing this URL: {str(e)}"

    def run(self):
        urls_list = []
        results_list = []
        final_answers_list = []
        
        # Generate subqueries
        subqueries = self.subqueries_generator(self.query)
        logging.info(f"Generated {len(subqueries)} subqueries")
        
        # Collect all unique URLs from all subqueries
        all_urls = set()
        for subquery in subqueries:
            urls = self.google_search(subquery, num=10)
            for url in urls[:self.kx]:
                all_urls.add(url)
        
        logging.info(f"Found {len(all_urls)} unique URLs across all subqueries")
        
        # Process URLs in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self.process_url, url): url for url in all_urls}
            for future in concurrent.futures.as_completed(futures):
                url = futures[future]
                try:
                    url, results = future.result()
                    urls_list.append(url)
                    results_list.append(results)
                except Exception as e:
                    logging.error(f"Exception processing result from {url}: {str(e)}")
                    urls_list.append(url)
                    results_list.append(f"Error: {str(e)}")
        
        # Organize results
        for i, url in enumerate(urls_list):
            final_answer = f"URL: {url}\n\n\nRESULTS: {results_list[i]}\n\n\n"
            final_answers_list.append(final_answer)
        
        return final_answers_list

if True:
    prompt = "Quali sono competitor di FEPA Srl"
    prompt2 = "Cosa è l'AI?"
    searcher = Searcher(prompt, 10)
    results = searcher.run()
    print(results)


"""
There is this website: https://www.verifiedmarketresearch.com/blog/best-thermoformed-plastic-manufacturers/
where you can find a lot of information about marketr researches about lots of stuff. 
It could be integrated in the search function to get more information.
"""