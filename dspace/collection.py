from dspace import *

# FIXME: This has to be a pure data class, e.g. it should not have a functionality for sending requests and so on


class Collection(object):

    def __init__(self, handle):
        """

        :param str handle: handle ID string ('prefix/suffix')
        """
        self.__handle = handle              # type: str
        self.__coll_metadata = None         # type: list
        self.__items = None                 # type: list

        # self.__initialize()

    @property
    def handle(self):
        return self.__handle

    @property
    def collection_metadata(self):
        return self.__coll_metadata

    @collection_metadata.setter
    def collection_metadata(self, value):
        self.__coll_metadata = value

    @property
    def items(self):
        return self.__items

    @items.setter
    def items(self, value):
        self.__items = value

