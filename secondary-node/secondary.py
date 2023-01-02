import os
import asyncio
from fastapi import FastAPI, Body

from services.consul_service import ConsulService
from application.custom_logger import logger
from data_access import DataAccess

app = FastAPI()
consul_service = ConsulService()
data_access = DataAccess()


@app.put('/append')
async def append(msg: str = Body(..., title="msg", embed=True),
                 msg_id: int = Body(..., title="msg", embed=True)):
    try:
        delay = int(os.getenv("DELAY"))
        await asyncio.sleep(delay)

        data_access.save_data(msg, msg_id)
        logger.info(f'Successfully added msg {msg}')
    except Exception as err:
        logger.error(f'Adding failed. There was the following error: {err}')
        return {'status': 'false'}

    return {'status': 'ok'}


@app.get('/list')
async def list_messages():
    messages = data_access.get_data()
    return {'status': 'ok', 'list': f"{', '.join(messages)}"}


@app.get('/health')
async def health_check():
    logger.info('Health request!')
    return {'status': 'ok'}


@app.on_event("shutdown")
def shutdown():
    # Might not run due to this bug: https://github.com/encode/uvicorn/issues/1116
    logger.info('Deregistering from Consul')
    consul_service.deregister()
