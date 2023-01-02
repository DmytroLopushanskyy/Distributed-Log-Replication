import json
import random
import asyncio
import aiohttp

from application.custom_logger import logger
from application.count_down_latch import CountDownLatch


class RequestService:
    def __init__(self, write_concern, timeout=20):
        self.timeout = timeout
        self.latch = CountDownLatch(write_concern)

    async def send_payload(self, urls, consul_service, secondary_name, payload):
        for url in urls:
            asyncio.create_task(self.async_request(
                url=url,
                consul_service=consul_service,
                secondary_name=secondary_name,
                payload=payload
            ))

        await self.latch.wait()

    async def async_request(self, url, consul_service, secondary_name, payload):
        conn = aiohttp.TCPConnector(limit=None, ttl_dns_cache=300)
        session = aiohttp.ClientSession(connector=conn)

        backoff_s = 1
        exp = 0
        while True:  # implementing endless retries
            if self.check_if_url_is_healthy(consul_service, secondary_name, url):
                try:
                    async with session.put(url, json=payload, ssl=False) as response:
                        obj = await response.read()
                        json_response = json.loads(obj.decode('utf-8'))
                        logger.info(f"Response code received: {json_response}")
                        # Potentially can also check for response.status == 200, but it is less strict than getting ok
                        # response from the server
                        if json_response.get('status') == 'ok':
                            await self.latch.count_down()
                            logger.info("Request finished")
                            break

                        logger.error(f"Response not OK: status {response.status}, text: {json_response}")
                except Exception as err:
                    logger.error(f"Request exception raised: {err}")
            else:
                logger.error(f"Service is marked unhealthy, no request is made")

            delay_s = backoff_s * 1.5 ** exp + random.uniform(0, 1)
            await asyncio.sleep(delay_s)
            if delay_s < 30:
                exp += 1
            logger.error(f"Running a retry after waiting for {delay_s} seconds...")

        await session.close()
        await conn.close()

    @staticmethod
    def check_if_url_is_healthy(consul_service, secondary_name, url):
        healthy_services = consul_service.get_healthy_urls(secondary_name)
        test_domain = url.replace('http://', '').split('/')[0]

        for healthy_url in healthy_services:
            healthy_domain = healthy_url.replace('http://', '').split('/')[0]
            if test_domain == healthy_domain:
                return True
        return False
