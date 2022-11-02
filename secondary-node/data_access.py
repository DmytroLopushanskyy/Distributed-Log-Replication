"""
This module is responsible for getting the data for the facade service.
"""
import uuid
from application.custom_logger import logger


class DataAccess:
    def __init__(self):
        self.__data_dict = dict()

    def save_data(self, msg) -> None:
        """ Save data to local memory """
        assigned_uuid = self.__create_id()
        self.__data_dict[assigned_uuid] = msg

    @staticmethod
    def __create_id() -> str:
        """ Create unique UUID """
        return str(uuid.uuid4())

    def get_data(self):
        logger.info(list(self.__data_dict.values()))
        return list(self.__data_dict.values())
