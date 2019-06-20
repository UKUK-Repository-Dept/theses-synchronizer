import logging

class LoggerHandler(object):

    def __init__(self, LOG_NAME='synchronizer', LOG_LEVEL=logging.INFO, LOG_FORMAT='%(asctime)s %(name)-12s %(levelname)-8s %(message)s'):
        self.LOG_NAME = LOG_NAME
        self.LOG_FORMAT = LOG_FORMAT
        self.LOG_LEVEL = LOG_LEVEL
        # creates  basic log object
        self.__log = self.__create_root_log()

    def __create_root_log(self):
        """
        Method creates a logger object and sets it up to do basic console and
        file logging. Other logfile handlers are created by create_log_file
        method.
        """
        root_log_name = 'synchronizer'
        log = logging.getLogger(root_log_name)

        formatter = logging.Formatter(self.LOG_FORMAT)

        # Creates console handler that will handle all console logging from
        # root logger
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(self.LOG_LEVEL)
        log.addHandler(console_handler)

        # Creates file handler for root logger
        filehandler = logging.FileHandler(self.LOG_NAME, mode='w')
        filehandler.setFormatter(formatter)
        filehandler.setLevel(self.LOG_LEVEL)
        log.addHandler(filehandler)

        # Sets level of root logger
        log.setLevel(self.LOG_LEVEL)

        # returns root logger object
        return log

    def create_log_file(self, log_name, mode, log_format, level):
        """
        Main method that creates file handlers for logfiles and adds them to
        root logger object.
        """
        # setup formatter
        log_formatter = logging.Formatter(log_format)
        # setup file handler, set its format, name, file mode and log level. 
        # This will ensure logging to custom files in a custom format if need
        # be, independent from root logger.
        
        file_handler = logging.FileHandler(log_name, mode=mode)
        file_handler.setFormatter(log_formatter)
        file_handler.setLevel(level)
        self.log.addHandler(file_handler)

    @property
    def log(self):
        return self.__log
