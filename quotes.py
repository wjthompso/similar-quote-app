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
    # TODO: Clean this up!
    start = time.time()
    # This code is identical to the following code
    # responses = get_all_pages_of_quotes()
    results = asyncio.run(get_all_quote_responses())
    json_results = [asyncio.run(result.json()) for result in results]
    # quotes = [*result['results'] for result in json_results]
    quotes = [quote for sublist in json_results for quote in sublist["results"]]

    # Older example with the event_loop
    # loop = asyncio.get_event_loop()
    # results = loop.run_until_complete(get_symbols())
    # loop.close()

    # end = time.time()
    # total_time = round((end - start), 2)
    # print(f"It took us {total_time} seconds to get our results")
    # print(len(results))

    return quotes

# def add_all_quotes

def find_quote_by_id(id):
    all_quotes = get_all_quotes()
    quote_dict = {quote["_id"]: quote for quote in all_quotes}
    return quote_dict[id]

def find_nth_largest_number(nth, unsorted_list):
    """Find the second largest number means nth = 2
    Find the third largest number means nth = 3, and so on."""
    unsorted_list = unsorted_list
    sorted_list = sorted(list(unsorted_list), reverse = True) # Starts from largest to smallest
    return unsorted_list.index(sorted_list[nth - 1])


def find_similar_quote(quote, all_quote_ids):
    # "Takes a flattened list of dictionaries containing quote data"
    # print()
    # print()
    # print("Here's the quote", quote)
    # print()
    # print()
    quote_similarities = quote["quote_similarities"][quote["quote_id"]]
    idx_max = find_nth_largest_number(1, quote_similarities) #index of max value, the most similar quote
    quote_id = all_quote_ids[idx_max] #The quote_id using the index of the maximum similarity score
    nth = 1
    while True:
        if QuoteHistory.query.filter_by(quote_id = quote_id).count() == 0: #Is the quote in our history? No? Carry on
            return Quote.query.filter_by(quote_id = quote_id).first().__dict__
        else: #You mean it's already in our quote history? Get another quite, just slightly less similar, but still similar.
            nth += 1
            nth_idx_max = find_nth_largest_number(nth, quote_similarities)
            quote_id = all_quote_ids[nth_idx_max]
        

# def find_similar_quote(quote, all_quotes):
#     "Takes a flattened list of dictionaries containing quote data"
#     given_quote_tags = set(quote['tags'])
#     for quote_candidate in all_quotes:
#         quote_candidate_tags = set(quote_candidate['tags'])
#         if given_quote_tags.issubset(quote_candidate_tags) and quote['quote_id'] != quote_candidate["quote_id"]:
#             if QuoteHistory.query.filter_by(quote_id = quote_candidate["quote_id"]).count() == 0:
#                 return quote_candidate
#     return None

def format_times(all_quotes):
    for idx, quote in enumerate(all_quotes):
        all_quotes[idx]["formatted_time"] = quote["time_of_rating"].strftime("%B %-d, %Y at %I:%M %p (UTC)")

    return all_quotes

if __name__ == "__main__":
    all_quotes = {"all_content": get_all_quotes()}
    df = pd.read_csv("sentence_similarity_matrix.csv", index_col = "index")
    
    with open('all_quotes.json', 'w', encoding ='utf8') as json_file: 
        json.dump(all_quotes, json_file, ensure_ascii = False) 
        
    print("Hey")