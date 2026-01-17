import asyncio
import sys
import aiohttp


async def fetch_url(url, session):
    async with session.get(url) as resp:
        return resp.status


async def fetch_worker(que, session, name):
    cnt = 0
    while True:
        url = await que.get()
        if url is None:
            break

        try:
            status = await fetch_url(url, session)
            print("fetch_worker:", name, "url:", url, "status:", status)
        except (
            aiohttp.ClientError, aiohttp.InvalidURL,
            asyncio.TimeoutError, RuntimeError
        ):
            print("Invalid url:", url)

        cnt += 1

    print("fetch_worker finished", name, cnt)


async def run(filepath, num_workers):
    que = asyncio.Queue(maxsize=num_workers)

    async with aiohttp.ClientSession() as session:
        tasks = [
            asyncio.create_task(fetch_worker(que, session, f"fetcher_{i}"))
            for i in range(num_workers)
        ]

        with open(filepath, "r", encoding="utf-8") as file:
            for line in file:
                url = line.strip()
                if url:
                    await que.put(url)

        for _ in range(num_workers):
            await que.put(None)

        await asyncio.gather(*tasks)


if __name__ == "__main__":

    file_path = sys.argv[-1]

    temp = sys.argv[-2]
    try:
        workers = int(temp)
        if workers < 1:
            raise ValueError("Invalid number of workers")
    except Exception as exc:
        raise ValueError("Invalid number of workers") from exc
    asyncio.run(run(file_path, workers))
