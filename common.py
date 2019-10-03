import aiohttp

from db_session.db_session import Session, jobs_table

callback_host = ''
CALLBACK_PORT = 8080
callback_base = f'http://{callback_host}:{CALLBACK_PORT}/job_callback'
CALLBACK_TEMPLATE = callback_base + '/{internal_id}'
RTC_URL = 'https://data.oxylabs.io/v1/queries'

DB_SESSION_PARAMS = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'oxy_con'
}

RTC_AUTH = aiohttp.BasicAuth(login='user', password='pass')


async def update_job_status(internal_id: int, status: str):
    async with Session(**DB_SESSION_PARAMS) as db_ses:
        db_ses.exec.update()\
            .where(jobs_table.c.id == internal_id)\
            .values(status=status)
