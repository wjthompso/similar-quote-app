import asyncio
import aiohttp
import os
import time
import json

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

def find_quote_by_id(id):
    all_quotes = get_all_quotes()
    quote_dict = {quote["_id"]: quote for quote in all_quotes}
    return quote_dict[id]


def find_similar_quote(quote, all_quotes):
    "Takes a flattened list of dictionaries containing quote data"
    given_quote_tags = set(quote['tags'])
    for quote_candidate in all_quotes:
        quote_candidate_tags = set(quote_candidate['tags'])
        if given_quote_tags.issubset(quote_candidate_tags) and quote['quote_id'] != quote_candidate["quote_id"]:
            return quote_candidate
    return None


if __name__ == "__main__":
    all_quotes = get_all_quotes()
    print("hey")
    # single_quote = all_quotes[90]
    # print()
    # # print(find_similar_quote(single_quote, all_quotes))
    # print(find_quote_by_id('nkftU-0YuUP6'))
    # print()
    # # print(single_quote)
    # print("hey")