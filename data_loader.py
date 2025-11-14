# data_loader.py
import pandas as pd
import requests
import ast
from typing import List, Dict, Any

#URL = "https://november7-730026606190.europe-west1.run.app/messages"
URL = os.getenv("MESSAGES_API_URL", "https://november7-730026606190.europe-west1.run.app/messages")

def fetch_messages() -> List[Dict[str, Any]]:
    """
    Fetch messages from the API endpoint and return as a list of dicts.
    """
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, dict) and "items" in data:
            # Normalize structure
            items = data["items"]
            if isinstance(items, list):
                return items
            if isinstance(items, str):
                # Some responses may serialize list as a string
                return ast.literal_eval(items)
        return data if isinstance(data, list) else []
    except Exception as e:
        print("❌ Error fetching messages:", e)
        return []

def load_messages_as_df() -> pd.DataFrame:
    """
    Alternative function to load messages as a Pandas DataFrame.
    """
    msgs = fetch_messages()
    return pd.DataFrame(msgs)
