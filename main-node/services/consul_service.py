from application.consul import Consul


class ConsulService:
    def __init__(self):
        self.__consul = Consul()

    def get_value(self, key):
        return self.__consul.get_value(key)

    def get_service_urls(self, service_name):
        return self.__consul.get_service_urls(service_name)

    def get_health_report(self, service_name):
        return self.__consul.get_health_report(service_name)

    def get_healthy_urls(self, service_name):
        return self.__consul.get_healthy_urls(service_name)

    def deregister(self):
        self.__consul.deregister()
