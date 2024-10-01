# abstract_api_client.py

import csv
import os
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Dict, List, Set

from dotenv import load_dotenv
from tqdm import tqdm

class AbstractAPIClient(ABC):
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.api_keys = self._load_api_keys()
        self.current_key_index = 0

    def _load_api_keys(self) -> List[Any]:
        load_dotenv()
        keys = []
        i = 1
        while True:
            key = os.getenv(f'{self.service_name}_API_KEY_{i}')
            if key:
                keys.append(self._process_api_key(key))
                i += 1
            else:
                break
        if not keys:
            raise ValueError(f"No {self.service_name} API keys found in environment variables.")
        return keys

    @abstractmethod
    def _process_api_key(self, key: str) -> Any:
        """Process the API key as needed for the specific service."""
        pass

    def _get_current_key(self) -> Any:
        return self.api_keys[self.current_key_index]

    def _rotate_api_key(self):
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)

    @abstractmethod
    def _should_rotate(self, exception: Exception) -> bool:
        """Determine if the API key should be rotated based on the exception."""
        pass

    def execute_with_rotation(self, func, *args, **kwargs):
        try:
            return func(self._get_current_key(), *args, **kwargs)
        except Exception as e:
            if self._should_rotate(e):
                self._rotate_api_key()
                return self.execute_with_rotation(func, *args, **kwargs)
            else:
                raise

    def paginate(self, func: Callable, *args, total: int = None, **kwargs) -> List[Any]:
        """
        Helper method to handle pagination for API calls with progress tracking.

        Args:
            func (Callable): The function to call for each page.
            total (int): The total number of items to fetch (for progress bar).
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.

        Returns:
            List[Any]: Aggregated results from all pages.
        """
        results = []
        progress_bar = tqdm(total=total, desc="Fetching artists")
        offset = 0
        limit = min(50, total)

        while len(results) < total:
            page_results = self.execute_with_rotation(func, *args, limit=limit, offset=offset, **kwargs)
            items = page_results['items']
            results.extend(items)
            progress_bar.update(len(items))
            
            if not items or len(items) < limit:
                break
            
            offset += len(items)
            limit = min(50, total - len(results))

        progress_bar.close()
        return results[:total]

    @staticmethod
    def load_from_text(file_path: str) -> Set[str]:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                return set(line.strip() for line in file)
        return set()
    
    @staticmethod
    def save_to_text(data: List[str], file_path: str):
        sorted_data = sorted(data, key=str.lower)
        with open(file_path, 'w', encoding='utf-8') as file:
            for item in sorted_data:
                file.write(f"{item}\n")

    @staticmethod
    def save_to_csv(self, data: List[Dict[str, Any]], file_path: str):
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

    @staticmethod
    def run_multithreaded(items: List[Any], func: Callable, max_workers: int = 10, desc: str = "Processing") -> List[Any]:
        """
        Executes a function across multiple items using multi-threading.

        Args:
            items (List[Any]): The list of items to process.
            func (Callable): The function to apply to each item.
            max_workers (int): The maximum number of threads to use.
            desc (str): Description for the progress bar.

        Returns:
            List[Any]: The list of results.
        """
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_item = {executor.submit(func, item): item for item in items}
            for future in tqdm(as_completed(future_to_item), total=len(items), desc=desc):
                try:
                    result = future.result()
                    if result is not None:
                        results.append(result)
                except Exception as e:
                    print(f"Error processing item {future_to_item[future]}: {e}")
        return results