"""
This module is responsible for getting the data for the facade service.
"""
from application.custom_logger import logger


class DataAccess:
    def __init__(self):
        self.__data = list()

    def save_data(self, msg, msg_id) -> None:
        """ Save data to local memory """
        if (msg_id, msg) not in self.__data:
            self.__data.append((msg_id, msg))
            self.__data.sort(key=lambda item: item[0])  # Sort it
            logger.info(f"Data: {[item[1] for item in self.__data]}")

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

        # Allow data to start **not** with ID=0. Will be useful if the secondary node is rebooted
        # and the in-memory list is lost. Then it will be accumulating data from some later point of time.
        if len(self.__data) > 0:
            last_id = self.__data[0][0] - 1

        for item in self.__data:
            msg_id = item[0]
            if msg_id - last_id != 1:
                return last_id + 1
            last_id = msg_id
        return last_id + 1
