import asyncio
import aiohttp

from sanic import Sanic
from sanic import response as sanic_response

from db_session.db_session import job_results_table, jobs_table
from db_session.db_session import Session as DBSession
from common import DB_SESSION_PARAMS, RTC_AUTH, CALLBACK_PORT

app = Sanic()


async def fetch(url: str) -> dict:
    async with aiohttp.ClientSession(auth=RTC_AUTH) as ses:
        res = await ses.get(url)
        return await res.json()


async def put_to_db(result: dict, internal_id: int):
    async with DBSession(**DB_SESSION_PARAMS) as db_ses:
        try:
            await db_ses.insert(job_results_table,
            {
                'internal_id': internal_id,
                'content': str(result['content']),
                'status_code': result['status_code'],
                'job_id': result['job_id'],
                'url': result['url'],
                'page': result['page'],
            })
        except Exception as e:
            print(f'Results to db failure: {e!r}')


async def handle_results(result_url: str, internal_id: int):
    res = await fetch(result_url)
    try:
        result = res['results'][0]
        await put_to_db(result, internal_id)
    except(KeyError, IndexError) as e:
        print(f"Unable to find results in response: {res}")


@app.route('/job_callback/<internal_id:int>', methods=['POST'])
async def callback_handler(request, internal_id):
    try:
        res_url = request.json['results_url']
    except Exception as e:
        print(f"Exception on callback handling: {e!r} \n {request.body}")
        return sanic_response.json(
            {'error': '`results_url` not found in request'},
            status=500,
        )
    asyncio.ensure_future(handle_results(res_url, internal_id))
    return sanic_response.json(status=200, body={})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=CALLBACK_PORT)
