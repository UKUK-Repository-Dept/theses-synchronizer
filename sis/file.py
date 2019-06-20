from dspace import *


class File(object):

    def __init__(self, fid, data):
        self.__fid = fid
        self.__data = data
        self.__ftyp_prevod = None

    @property
    def did(self):
        return self.__data.did

    @property
    def ftyp(self):
        return self.__data.ftyp

    @property
    def ftyp_prevod(self):
        return self.__ftyp_prevod

    @ftyp_prevod.setter
    def ftyp_prevod(self, value):
        self.__ftyp_prevod = value

    @property
    def fnazev(self):
        return self.__data.fnazev

