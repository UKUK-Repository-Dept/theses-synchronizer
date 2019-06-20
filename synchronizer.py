from configparser import ConfigParser, ExtendedInterpolation
from getopt import gnu_getopt
from sys import argv, stderr
# import database classes
from db.db import reflect
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from sqlsoup import SQLSoup
from manager.manager import Manager

if __name__ == '__main__':

    def do_start(handle, config, debug):

        # get database connection string
        sis_url = config.get('database', 'url')
        dspace_url = config.get('database', 'dspace_url')

        # default to much saner database query defaults and always
        # commit and/or flush statements explicitly
        factory = sessionmaker(autocommit=False, autoflush=False)

        # SIS database
        engine_sis = create_engine(sis_url, encoding='utf-8')
        session_sis = scoped_session(factory)
        db_sis = SQLSoup(reflect(engine_sis), session=session_sis)

        # DSpace database
        engine_dspace = create_engine(dspace_url, encoding='utf-8')
        session_dspace = scoped_session(factory)
        db_dspace = SQLSoup(reflect(engine_dspace), session=session_dspace)

        manager = Manager(handle=handle, config=config, db_sis=db_sis,
                          db_dspace=db_dspace, debug=debug)

        manager.run()

    def do_help(*args, **kwargs):
        # TODO:
        pass

    def do_version(*args, **kwargs):
        pass

    opts, args = gnu_getopt(argv, 'hVicd:', ['help', 'version', 'id=',
                                             'config=', 'debug'])

    action = do_start
    handle = None
    config_path = './config/config.ini'
    debug = False

    for k, v in opts:
        if k in ('--help', 'h'):
            action = do_help
        elif k in ('--version', 'V'):
            action = do_version

        if k in ('--id', 'i'):
            handle = v

        if k in ('--config', 'c'):
            config_path = v

        if k in ('--debug', 'd'):
            debug = True

    # Load the configuration from file.
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read(config_path)

    print("Synchronizer: HANDLE:", handle)

    if handle is None:
        action = do_help
        action()

    # Perform selected action.
    action(handle=handle, config=config, debug=debug)
