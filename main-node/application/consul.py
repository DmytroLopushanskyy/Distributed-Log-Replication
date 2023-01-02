import os
import time
import consul
import requests
from dotenv import load_dotenv

from application.custom_logger import logger

load_dotenv(dotenv_path='./main-node.env')


class Consul:
    def __init__(self):
        self.__consul_client = consul.Consul(
            host=os.getenv("CONSUL_HOST"),
            port=os.getenv("CONSUL_PORT")
        )

        self.service_id = f'{os.getenv("APP_HOST")}:{os.getenv("APP_PORT")}'

        while True:
            try:
                self.__consul_client.agent.service.register(
                    name=os.getenv("APP_NAME"),
                    service_id=self.service_id,
                    address=os.getenv("APP_HOST"),
                    port=int(os.getenv("APP_PORT"))
                )
                break
            except requests.exceptions.ConnectionError as exception:
                logger.info('Unable to connect to Consul. Retrying in 5 seconds...')
                logger.error(exception)
                time.sleep(5)

    def get_value(self, key: str):
        _, data = self.__consul_client.kv.get(key, index=None)
        return data["Value"].decode("utf-8") if data else None

    def get_service_urls(self, service_name):
        _, data = self.__consul_client.catalog.service(service_name)
        urls = [f"http://{item['ServiceAddress']}:{int(item['ServicePort'])}"
                for item in data]
        return urls

    def get_health_report(self, service_name):
        checks = self.__consul_client.health.checks(service_name)[1]
        results = dict()
        for check in checks:
            results[check.get('ServiceID')] = check.get('Status')
        return results

    def get_healthy_urls(self, service_name):
        checks = self.__consul_client.health.checks(service_name)[1]
        results = list()
        for check in checks:
            if check.get('Status') == 'passing':
                results.append(f"http://{check['ServiceID']}")
        return results

    def deregister(self):
        self.__consul_client.agent.service.deregister(self.service_id)
