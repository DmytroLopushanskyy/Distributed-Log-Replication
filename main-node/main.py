import os
import httpx
from fastapi import FastAPI, Body

from services.consul_service import ConsulService
from application.custom_logger import logger
from data_access import DataAccess


app = FastAPI()
consul_service = ConsulService()
data_access = DataAccess()


@app.put('/append')
async def append(msg: str = Body(..., title="msg", embed=True)):
    try:
        data_access.save_data(msg)
        logger.info(f'Successfully added msg {msg}')
    except Exception as err:
        logger.error(f'Adding failed. There was the following error: {err}')
        return {'status': 'false'}

    secondary_name = 'secondary-node'
    secondary_services = consul_service.get_service_urls(secondary_name)
    logger.info(f'secondary services found: {secondary_services}')

    async with httpx.AsyncClient() as client:
        for dest_url in secondary_services:
            try:
                response = await client.put(f"{dest_url}/append", json={"msg": msg}, timeout=30)
                response = response.json()
                logger.info(response.get('status'))
            except Exception as err:
                logger.error(err)

    return {'status': 'ok'}


@app.get('/list')
async def list_messages():
    messages = data_access.get_data()
    return {'status': 'ok', 'list': f"{', '.join(messages)}"}


@app.on_event("shutdown")
def shutdown():
    logger.info('Deregistering from Consul')
    consul_service.deregister()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=int(os.getenv('APP_PORT')))
