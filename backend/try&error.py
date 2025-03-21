from googleapiclient.discovery import build
from research import Searcher


query = "Do you know any companies that specialize in terraformed paper or similar?"
results = Searcher(query).run()
print(results)