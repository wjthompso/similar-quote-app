import asyncio
import aiohttp
import time
import json
import pandas as pd
from app import QuoteHistory
from app import Quote

def get_request_tasks(session):
    tasks = []
    for i in range(1, 96):
        url = "https://api.quotable.io/quotes?" + f"page={i}"
        tasks.append(session.get(url, ssl=False))
    return tasks

async def get_all_quote_responses():
    async with aiohttp.ClientSession() as session:
        tasks = get_request_tasks(session)
        responses = await asyncio.gather(*tasks)
        return responses

def get_all_quotes(): 
    results = asyncio.run(get_all_quote_responses())
    json_results = [asyncio.run(result.json()) for result in results]
    quotes = [quote for sublist in json_results for quote in sublist["results"]]
    return quotes
    
def find_quote_by_id(id):
    all_quotes = get_all_quotes()
    quote_dict = {quote["_id"]: quote for quote in all_quotes}
    return quote_dict[id]

def find_nth_extrema(nth, unsorted_list, max = True):
    """Find the second largest number means nth = 2, max = True
    Find the third largest number means nth = 3, max = True.
    Find the second smallest number means nth = 2, max = False, and so on"""
    unsorted_list = unsorted_list
    if max:
        sorted_list = sorted(list(unsorted_list), reverse = True) # Starts from largest to smallest
        return unsorted_list.index(sorted_list[nth - 1])
    if not max:
        sorted_list = sorted(list(unsorted_list), reverse = False) # Starts from smallest to largest
        return unsorted_list.index(sorted_list[nth - 1])


def find_another_quote(quote, all_quote_ids, different = False):
    "Takes a flattened list of dictionaries containing quote data"

    quote_similarities = quote["quote_similarities"][quote["quote_id"]]
    idx_max = find_nth_extrema(1, quote_similarities, max = not different) #index of max or min value, the most similar/different quote
    quote_id = all_quote_ids[idx_max] #The quote_id using the index of the maximum/minimum similarity score
    nth = 1
    while True:
        if QuoteHistory.query.filter_by(quote_id = quote_id).count() == 0: #Is the quote in our history? No? Carry on
            return Quote.query.filter_by(quote_id = quote_id).first().__dict__
        else: #The most similar quote is already in the user's quote history: Get another quote, but slightly less familiar.
            nth += 1
            nth_idx_max = find_nth_extrema(nth, quote_similarities)
            quote_id = all_quote_ids[nth_idx_max]

def format_times(all_quotes):
    for idx, quote in enumerate(all_quotes):
        all_quotes[idx]["formatted_time"] = quote["time_of_rating"].strftime("%B %-d, %Y at %I:%M %p (UTC)")

    return all_quotes

if __name__ == "__main__":
    all_quotes = {"all_content": get_all_quotes()}
    df = pd.read_csv("sentence_similarity_matrix.csv", index_col = "index")


