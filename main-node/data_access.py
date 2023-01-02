"""
This module is responsible for getting the data for the facade service.
"""
from application.custom_logger import logger


class DataAccess:
    def __init__(self):
        self.__data = list()
        self.last_id = -1

    def save_data(self, msg) -> int:
        """ Save data to local memory """
        assigned_id = self.last_id + 1
        if (assigned_id, msg) not in self.__data:
            self.__data.append((assigned_id, msg))
            self.__data.sort(key=lambda item: item[0])  # Sort it
            self.last_id = assigned_id
            logger.info(f'Successfully added msg {msg}')
        return assigned_id

    def get_data(self):
        gap_idx = self.find_first_gap_idx()
        # return only messages without their indexes
        return [msg[1] for msg in self.__data[:gap_idx]]

    def find_first_gap_idx(self) -> int:
        """
        Finds first gap index in the data.
        Assumes data indexing starts at 0 index.
        """
        last_id = -1
        for item in self.__data:
            msg_id = item[0]
            if msg_id - last_id != 1:
                return last_id + 1
            last_id = msg_id
        return last_id + 1
