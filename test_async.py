import asyncio

async def fetch_data(n):
    print(f"Fetching data from {n}")
    await asyncio.sleep(10)
    print(f"Finishing data from {n}")
    return {"task": n}


async def fetch_data_two(n):
    print(f"Fetching data from {n}")
    await asyncio.sleep(2)
    print(f"Finishing data from {n}")
    return {"task": n}


async def main():
    print(f"Started main task")
    tasks = [fetch_data(1), fetch_data_two(2), fetch_data(3)]
    results = await asyncio.gather(*tasks)
    print("All tasks done", results)

asyncio.run(main())
