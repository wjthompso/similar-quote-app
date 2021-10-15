import asyncio
import aiohttp
import os
import time
import json

def get_pages_of_quotes(session):
    tasks = []
    for i in range(1, 96):
        url = "https://api.quotable.io/quotes?" + f"page={i}"
        tasks.append(session.get(url, ssl=False))
    return tasks

async def get_all_pages_of_quotes():
    async with aiohttp.ClientSession() as session:
        tasks = get_pages_of_quotes(session)
        responses = await asyncio.gather(*tasks)
        return responses

start = time.time()
# This code is identical to the following code
# responses = get_all_pages_of_quotes()
results = asyncio.run(get_all_pages_of_quotes())
json_results = [asyncio.run(result.json()) for result in results]
# Older example with the event_loop
# loop = asyncio.get_event_loop()
# results = loop.run_until_complete(get_symbols())
# loop.close()

end = time.time()
total_time = round((end - start), 2)
print(f"It took us {total_time} seconds to get our results")
print(len(results))