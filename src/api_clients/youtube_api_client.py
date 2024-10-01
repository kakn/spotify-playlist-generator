from typing import List

import requests

from src.api_clients.abstract_api_client import AbstractAPIClient

class YouTubeAPIClient(AbstractAPIClient):
    def __init__(self):
        super().__init__('YOUTUBE')

    def _process_api_key(self, key: str) -> str:
        return key

    def _should_rotate(self, exception: Exception) -> bool:
        return isinstance(exception, requests.HTTPError) and exception.response.status_code in [403, 429]

    def _fetch_search_suggestions(self, query: str, language: str = 'en') -> List[str]:
        """
        Fetch search suggestions from YouTube suggest API.
        """
        suggest_url = 'https://suggestqueries.google.com/complete/search'
        params = {
            'client': 'firefox',
            'ds': 'yt',
            'q': query,
            'hl': language,
        }
        response = requests.get(suggest_url, params=params)
        response.raise_for_status()
        suggestions = response.json()[1]
        return suggestions