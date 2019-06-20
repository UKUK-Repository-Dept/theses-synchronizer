from dspace import *

# FIXME: This has to be a pure data class, e.g. it should not have a functionality for sending requests and so on


class Bitstream(object):

    def __init__(self, identifier, data):
        self.__id = identifier
        self.__bitstream_data = data

    @property
    def name(self):
        return self.__bitstream_data['name']

    @property
    def handle(self):
        return self.__bitstream_data['handle']

    @property
    def link(self):
        return self.__bitstream_data['link']

    @property
    def bundle(self):
        return self.__bitstream_data['budnleName']

    @property
    def description(self):
        return self.__bitstream_data['description']

    @property
    def mime_type(self):
        return self.__bitstream_data['mimeType']

    @property
    def checksum_type(self):
        return self.__bitstream_data['checkSum']['checkSumAlgorithm']

    @property
    def checksum_value(self):
        return self.__bitstream_data['checkSum']['value']
