from dspace import *

# FIXME: This has to be a pure data class, e.g. it should not have a functionality for sending requests and so on


class Item(object):

    def __init__(self, identifier, data):
        """

        :param int identifier:
        :param str name:
        :param str handle:
        :param str link:
        """
        self.__identifier = identifier                          # type: int
        self.__item_data = data                                 # type: dict
        self.__item_metadata = None
        self.__sis_files_data = None                            # type: list
        self.__bitstreams = None                                # type: list
        self.__sis_files = None                                 # type: list
        self.__bitstreams_data = None                           # type: list

    @property
    def identifier(self):
        return self.__identifier

    @property
    def name(self):
        return self.__item_data['name']

    @property
    def handle(self):
        return self.__item_data['handle']

    @property
    def link(self):
        return self.__item_data['link']

    @property
    def item_data(self):
        return self.__item_data

    @item_data.setter
    def item_data(self, value):
        self.__item_data = value

    @property
    def bitstreams_data(self):
        return self.__bitstreams_data

    @bitstreams_data.setter
    def bitstreams_data(self, value):
        self.__bitstreams_data = value

    @property
    def metadata(self):
        return self.__item_metadata

    @metadata.setter
    def metadata(self, value):
        self.__item_metadata = value

    @property
    def did(self):
        for meta_item in self.metadata['metadata']:
            if meta_item['key'] == 'dc.identifier.repId':
                return meta_item['value']
            else:
                continue
        return None

    @property
    def bitstreams(self):
        return self.__bitstreams

    @bitstreams.setter
    def bitstreams(self, value):
        self.__bitstreams = value

    @property
    def sis_files(self):
        return self.__sis_files

    @sis_files.setter
    def sis_files(self, value):
        self.__sis_files = value

    @property
    def sis_files_data(self):
        return self.__sis_files_data

    @sis_files_data.setter
    def sis_files_data(self, value):
        self.__sis_files_data = value
