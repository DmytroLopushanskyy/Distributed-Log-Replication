import os
import math
from fastapi import FastAPI, Body

from data_access import DataAccess
from application.custom_logger import logger
from services.consul_service import ConsulService
from services.request_service import RequestService


app = FastAPI()
consul_service = ConsulService()
data_access = DataAccess()
secondary_name = 'secondary-node'


@app.put('/append')
async def append(msg: str = Body(..., title="msg", embed=True),
                 write_concern: int = Body(..., title="write_concern", embed=True)):
    if write_concern <= 0:
        return {'status': 'false', 'error': 'Write concerns needs to be a positive integer'}

    secondary_services = consul_service.get_service_urls(secondary_name)
    healthy_services = consul_service.get_healthy_urls(secondary_name)
    logger.info(f'secondary services: {secondary_services}')

    if len(healthy_services) + 1 < math.ceil((1 + len(secondary_services)) / 2):
        logger.warn("Quorum not satisfied, read-only mode activated")
        return {'status': 'false', 'message': 'Quorum is not satisfied as majority nodes is unhealthy. '
                                              'The service is read-only. Try again to append later.'}

    try:
        assigned_id = data_access.save_data(msg)
        write_concern -= 1
    except Exception as err:
        logger.error(f'Adding failed. There was the following error: {err}')
        return {'status': 'false'}

    urls = [f"{dest_url}/append" for dest_url in secondary_services]
    req_service = RequestService(write_concern)
    await req_service.send_payload(urls, consul_service, secondary_name, {"msg": msg, "msg_id": assigned_id})

    # will either return ok or wait forever for write_concern to be satisfied
    return {'status': 'ok'}


@app.get('/list')
async def list_messages():
    messages = data_access.get_data()
    return {'status': 'ok', 'list': f"{', '.join(messages)}"}


@app.get('/health')
async def health_check():
    health_report = consul_service.get_health_report(secondary_name)
    return {'status': 'ok', 'Health report': health_report}


@app.on_event("shutdown")
def shutdown():
    logger.info('Deregistering from Consul')
    consul_service.deregister()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=int(os.getenv('APP_PORT')))
