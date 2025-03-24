import requests

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