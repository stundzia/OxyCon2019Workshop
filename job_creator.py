import asyncio
import time

import aiohttp

from db.db_session import Session as DBSession
from db.db_session import jobs_table
from common import CALLBACK_TEMPLATE, RTC_URL, RTC_AUTH, DB_SESSION_PARAMS, update_job_status


async def create_job(row):
    callback_url = CALLBACK_TEMPLATE.format(internal_id=row['id'])
    payload = {
        'source': row['target'],
        'callback_url': callback_url,
        'geo_location': row['geo_location'],
        'parse': row['parse'],
        'domain': row['domain'],
    }
    if row['target'].count('_'):
        payload['query'] = row['query']
    else:
        payload['url'] = row['url']
    async with aiohttp.ClientSession(auth=RTC_AUTH) as session:
        res = await session.post(
            url=RTC_URL,
            json=payload,
        )
        if res.status not in [200, 201, 202]:
            if 500 > res.status > 400:
                if res.status == 429:
                    await update_job_status(row['id'], 'init')
                else:
                    await update_job_status(row['id'], 'invalid')
            if 500 < res.status < 600:
                await update_job_status(row['id'], 'init')
            print(f"Error: {res.status}")


async def fetch_jobs_to_do():
    start = time.time()
    db_ses: DBSession = DBSession(**DB_SESSION_PARAMS)
    await db_ses.open()
    res = await db_ses.exec(
        jobs_table.select().where(jobs_table.c.status == 'init')
    )
    res = await res.fetchall()
    job_ids = [r['id'] for r in res]
    await db_ses.exec(
        jobs_table.update().where(jobs_table.c.id.in_(job_ids)).values(
            status='pending',
        )
    )
    await asyncio.shield(asyncio.gather(
        *[create_job(r) for r in res]
    ))
    dur = time.time() - start
    print(
        f"{len(job_ids)} jobs created in {dur} seconds "
        f"({len(job_ids)/dur} jobs/s)"
    )
    return res


async def main():
    while True:
        rows = await fetch_jobs_to_do()
        await asyncio.shield(asyncio.gather(
            *[create_job(r) for r in rows]
        ))
        await asyncio.sleep(5)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
