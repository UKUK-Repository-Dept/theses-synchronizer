import os
from manager import *
from datetime import datetime
import time
import requests
import logging
from sqlalchemy import and_, or_, not_
from logger.logger_handler import LoggerHandler

# FIXME: Manager will be sending requests and interacting with data classes,
# FIXME: e.g. storing data in them and geting data back


class Manager(object):

    # TODO: Improve logging, add debug log and ability to turn it on with param
    # TODO: Log only really necessary data when using self.__logger.info()
    # TODO: Log SIS identifiers of thesis that do not have the same number of
    # files in SIS and DSpace object

    def __init__(self, handle, config, db_sis, db_dspace, debug):
        self.__handle = handle
        self.__config = config
        self.__db_connection = db_sis
        self.__db_dspace = db_dspace
        self.__debug = debug
        self.__logger = None

    def get_logger(self):

        # create log names
        prefix = str(self.__handle).replace('/','_')
        log_path = self.__config.get('logging', 'log_path')
        log_format = self.__config.get('logging', 'log_format')
        output_format = self.__config.get('logging', 'log_missing_format')

        LOG_FILE_INFO = os.path.join(log_path, str(prefix) +
                                     self.__config.get('logging','logname_info'))
        LOG_FILE_ERROR = os.path.join(log_path, str(prefix) + 
                                      self.__config.get('logging','logname_error'))
        LOG_FILE_MISSING = os.path.join(log_path, str(prefix) +
                                       self.__config.get('logging','logname_missing'))

        # create root logger
        if self.__debug is True:
            loghandler = LoggerHandler(LOG_FILE_INFO, logging.DEBUG, log_format)

        else:
            loghandler = LoggerHandler(LOG_FILE_INFO, logging.INFO, log_format)
        
        # create error log handler
        loghandler.create_log_file(LOG_FILE_ERROR, mode='w', log_format=log_format, level=logging.CRITICAL)

        # create missing files output log handler
        loghandler.create_log_file(LOG_FILE_MISSING, mode='w', log_format=output_format, level=logging.ERROR)

        # return log object
        return loghandler.log

    def run(self):
        start_time = time.time() 

        try:
            self.__logger = self.get_logger()
        except Exception as e:
            raise e

        # write first line of CSV output file
        self.__logger.error('did;handle;missing_files')

        try:
            c = Collection(handle=self.__handle)
            c.collection_metadata = self.get_collection_items_data(c)
            c.items = self.create_items(c)
        except Exception as e:
            self.__logger.critical(e)
            raise e

        y = 1
        for i in c.items:
            try:
                i.metadata = self.get_item_data(i)
            except Exception as e:
                self.__logger.critical(e)
                raise e

            self.__logger.info("[{}/{}] Processing ITEM: HANDLE: {}\tDID: {}".format(y, len(c.items), i.handle, i.did))
 
            try:
                i.bitstreams_data = self.get_bitstreams_data(i)
            except Exception as e:
                self.__logger.critical(e)
                raise e

            try:
                i.bitstreams = self.create_bitstreams(i)
            except Exception as e:
                raise e

            try:
                i.sis_files_data = self.get_sis_files_data(i)
            except Exception as e:
                self.__logger.critical(e)
                raise e

            try:
                i.sis_files = self.create_sis_files(i)
            except Exception as e:
                self.__logger.critical(e)
                raise e

            try:
                comparison = self.compare_files(i)
                self.__logger.debug("COMPARISON for ITEM {}\t{}: {}".format(i.handle, i.identifier, comparison))
            except Exception as e:
                self.__logger.critical(e)
                raise e

            try:
                status = self.synchronize_files(i, comparison)
            except Exception as e:
                self.__logger.critical(e)
                raise e

            y += 1
        
        elapsed_time = time.time() - start_time

        self.finish(elapsed_time)

    def finish(self, run_time):
        pretty_time = time.strftime("%H:%M:%S", time.gmtime(run_time))
        self.__logger.info("Script finished after: {}".format(pretty_time))

    def get_collection_items_data(self, c_obj):
        """

        :param Collection c_obj:
        :return:
        """
        self.__logger.info("Getting items from DSpace collection {}...".format(c_obj.handle))
        r_url = 'https://dspace.cuni.cz/rest/handle/' + c_obj.handle + '?expand=items'
        r = requests.get(r_url)

        if r.status_code == requests.codes.ok:
            collection_data = r.json()
            return collection_data
        else:
            r.raise_for_status()

    def create_items(self, collection):

        items = list()
        for item in collection.collection_metadata['items']:
            try:
                i = Item(item['id'], item)
            except Exception as e:
                raise e
            items.append(i)

        return items

    def get_item_data(self, item):
        """

        :param Item item:
        :return:
        """

        r = requests.get('https://dspace.cuni.cz/rest/handle/' + item.handle + '?expand=all')

        if r.status_code == requests.codes.ok:
            item_data = r.json()
            return item_data
        else:
            r.raise_for_status()

    def get_bitstreams_data(self, item):
        """
        Gets item bitstreams identifiers from DSpace database and stores them in item object.
        :param Item item:
        :return:
        """
        identifier = item.identifier
        statement = "SELECT bundle2bitstream.bitstream_id" \
        " FROM metadatavalue, item, item2bundle, bundle2bitstream, bitstream" \
        " WHERE item2bundle.item_id=item.item_id AND" \
        " item2bundle.bundle_id=bundle2bitstream.bundle_id AND" \
        " bundle2bitstream.bundle_id=metadatavalue.resource_id AND" \
        " metadatavalue.text_value='ORIGINAL' AND" \
        " bitstream.bitstream_id=bundle2bitstream.bitstream_id AND" \
        " item.item_id="+str(identifier)+" GROUP BY" \
        " bundle2bitstream.bitstream_id"

        bitstreams = self.__db_dspace.execute(statement)

        return bitstreams.fetchall()

    def get_sis_files_data(self, item):
        try:

            # FIXME: there is a missing mapping between dipl2doc.ftyp and tdpriloha.kod in case of ftyp goes beyond 10 (more than 10 supplements to a thesis)
            #
            # POSSIBLE SOLUTION: get rid of the supplement number in dipl2doc.ftyp - e.g. DPR10 becomes DPR

            files = self.__db_connection.dipl2doc.filter_by(did=item.did)

            #join = self.__db_connection.join(self.__db_connection.dipl2doc, self.__db_connection.tdpriloha,
            #                                 self.__db_connection.tdpriloha.kod == self.__db_connection.dipl2doc.ftyp)

            #item_files = join.filter_by(did=item.did)
            # Aditionaly, select only file that are not marked as archived
            # (farchivni=NULL)
            item_files = files.filter_by(farchivni=None).all()

        except Exception as e:
            raise e

        return item_files

    def create_bitstreams(self, item):

        bitstreams = list()

        data = self.get_bitstreams_metadata(item)
        self.__logger.debug("DATA:\n{}".format(data))
        for bitstream_data in data:
            try:
                self.__logger.debug("Creating bitstream {}".format(bitstream_data['identifier']))
                b = Bitstream(identifier=bitstream_data['identifier'],
                              data=bitstream_data)
            except Exception as e:
                raise e

            bitstreams.append(b)

        return bitstreams

    def get_bitstreams_metadata(self, item):
        """
        :param Item item
        """
        bitstream_list = list()
        for bs in item.bitstreams_data:
            bs_id = bs.bitstream_id
            # SOME ITEMS IN DSPACE DB HAVE DUPLICATE METADATA FIELD WITH ID
            # 64, WHERE WRONG DESCRIPTION IS STORED. THIS ROW HAS
            # RESOURCE_TYPE_ID=1, SO WE CAN 'FILTER OUT' THESE ROWS BY
            # ADDING CONDITION 'WHERE resource_type_id = 0' TO SECOND
            # SELECT STATEMENT.

            statement = "SELECT resource_id, a[1] description, a[2] filename" \
            " FROM (SELECT resource_id, array_agg(text_value) a FROM metadatavalue" \
            " WHERE resource_type_id=0 GROUP BY 1 ORDER BY 1) z WHERE resource_id="+str(bs_id)

            bs_metadata = self.__db_dspace.execute(statement)

            for identifier, description, filename in bs_metadata.fetchall():

                bitstream_metadata = dict()
                bitstream_metadata.update(
                    {'identifier': identifier,
                     'description': description,
                     'filename': filename
                    }
                )
                bitstream_list.append(bitstream_metadata)

        return bitstream_list

    def create_sis_files(self, item):

        files = list()

        for file in item.sis_files_data:
            try:
                f = File(file.fid, file)
                f.ftyp_prevod = self.__db_connection.tdpriloha.filter_by(kod = re.sub("\d+$", "", f.ftyp)).one().prevod
            except Exception as e:
                raise e
            files.append(f)
        return files

    def compare_files(self, item):
        """
        Compares files.
        :param Item item:
        :return:
        """
        comparison = dict()
        #   {"TX":
        #       {"sis": "1", "dspace": "1"},
        #   "PO":
        #       {"sis": "2", "dspace": "2"},
        #   "BE":
        #       {"sis": "1", "dspace": "1"},
        #   "BA":
        #       {"sis": "1", "dspace": "1"},
        #   "ZH":
        #       {"sis": "1", "dspace": "1"}
        # }
        for file_type, description in self.__config.items('filetypes_config'):
            file_type = str(file_type).upper()

            comparison[file_type] = dict()

            self.__logger.debug("Checking for existence of filetype (from config): {}...".format(description))

            sis_files_of_type = [sis_file for sis_file in item.sis_files if sis_file.ftyp_prevod == file_type]

            dspace_files_of_type = [ds_file for ds_file in item.bitstreams if ds_file.description == description]

            comparison[file_type].update(
                {
                    'sis': len(sis_files_of_type),
                    'dspace': len(dspace_files_of_type)
                })

        self.__logger.debug(comparison)
        return comparison

    #def _get_files_of_type(self, file_source, item, file_type, description):
    #    files_of_type = list()
    #
    #    if file_source == 'sis':
    #        if file_type is None:
    #            raise
    #
    #        for sis_file in item.sis_files:
    #            ftyp_prevod = self.__db_connection.tdpriloha.filter_by(kod = re.sub("\d+$", "", sis_file.ftyp)).one().prevod
    #            if ftyp_prevod == file_type:
    #                files_of_type.append(sis_file)
    #
    #    elif file_source == 'dspace':
    #        if description is None:
    #            raise
    #
    #       files_of_type = [ds_file for ds_file in item.bitstreams if ds_file.description == description]
    #
    #
    #    else:
    #        raise Exception("Unknown file_source: " + file_source)
    #
    #    return files_of_type

    def synchronize_files(self, item, comparison):
        """

        :param Item item:
        :param comparison:
        :return:
        """
        # TODO: Do the actual synchronization (e.g. import missing files from
        # SIS)

        counts_match = True
        missing_files = list()
        self.__logger.debug('COMPARISON FOR ITEM: HANDLE:' + item.handle + ' ITEM DID: ' +
                            item.did)
        for ftype, counts in comparison.items():
            if counts['sis'] == counts['dspace']:

                self.__logger.debug(' SIS FTYP: ' + ftype + ' SIS COUNT: ' + str(counts['sis']) +
                                    ' DSPACE COUNT: ' + str(counts['dspace']) + ' - File counts match.')
                continue

            elif counts['dspace'] == 0:
                counts_match = False
                missing_files.append(ftype)

                self.__logger.debug(' SIS FTYP: ' + ftype + ' SIS COUNT: ' + str(counts['sis']) +
                                    ' DSPACE COUNT: ' + str(counts['dspace']) + ' - 0 files in DSpace ITEMS.')

                continue

            elif (counts['sis'] > counts['dspace']) and counts['dspace'] != 0:
                counts_match = False
                missing_files.append(ftype)

                self.__logger.debug(' SIS FTYP: ' + ftype + ' SIS COUNT: ' + str(counts['sis']) +
                                    ' DSPACE COUNT: ' + str(counts['dspace']) + ' - MORE files in SIS than in DSpace.')
                continue

            elif (counts['sis'] < counts['dspace']) and counts['dspace'] != 0:
                counts_match = False
                missing_files.append(ftype)

                self.__logger.debug(' SIS FTYP: ' + ftype + ' SIS COUNT: ' + str(counts['sis']) +
                                    ' DSPACE COUNT: ' + str(counts['dspace']) + ' - LESS files in SIS than in DSpace.')
                continue

            else:
                raise Exception('SIS FTYP: ' + ftype + ' SIS COUNT: ' + str(counts['sis']) +
                                ' DSPACE COUNT: ' + str(counts['dspace']) + ' - Value error.')

        # write error to output csv
        if counts_match is False:
            self.__logger.error(str(item.did)+';'+str(item.handle)+';'+'/'.join(str(e) for e in missing_files))
