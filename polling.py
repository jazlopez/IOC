# Jaziel Lopez <juan.jaziel@gmail.com>
# Software Developer
# http://jlopez.mx

import re
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

try:

    engine = create_engine('mysql+pymysql://homestead:secret@localhost:3306/hdv4?charset=utf8', echo=True)
    metadata = MetaData()

    """
    session factory bound to engine (connection)
    """
    sess_maker = sessionmaker(bind=engine)

    sess_polling = sess_maker()

    """
    ioc_scans metadata
    """
    ioc_scans = Table('ioc_scans', metadata,
                      Column('id', Integer, primary_key=True),
                      Column('process_name', String(512), nullable=False),
                      Column('exact_word', String(1024), nullable=False),
                      Column('is_scrapy_scan', Integer, nullable=False))

    ioc_url_raw = Table('ioc_url_raw', metadata,
                        Column('id', Integer, primary_key=True),
                        Column('raw', Text, nullable=True))

    """
    ioc_url_raws metadata
    """
    ioc_scan_raw_urls = Table('ioc_scan_raw_urls', metadata,
        Column('id', Integer, primary_key=True),
        Column('scan_id',Integer, nullable=False),
        Column('raw_id',Integer, nullable=False),
        Column('read', Integer, nullable=False))

    scans = sess_polling\
        .query(ioc_scans.c.id, ioc_scans.c.process_name, ioc_scans.c.exact_word)\
        .filter(ioc_scans.c.id == 585).all()

    print "Total Scans:{}".format(len(scans))

    for row in scans:
        # Execute updates
        print "Execute update for scan {}".format(row.id)

        # get raw pending to score for the scan
        scan_raw_urls = sess_polling.query(ioc_scan_raw_urls.c.raw_id, ioc_url_raw.c.raw)\
            .filter(ioc_scan_raw_urls.c.raw_id == ioc_url_raw.c.id)\
            .filter(ioc_scan_raw_urls.c.scan_id == row.id)\
            .filter(ioc_scan_raw_urls.c.read == 0).all()

        for raw in scan_raw_urls:
            raw_match = 0

            matches = re.finditer(row.exact_word, raw.raw)

            for match in matches:
                raw_match += 1
                # TODO: add this line to debug file log
                # print "Start at {}, ends at {}".format(match.start(), match.end())

            print "Total Occurrences of {}: {}".format(row.exact_word.encode("utf-8"), raw_match)

            separator = "{}\n".format("="*10) * 3
            print separator
            print raw.raw

            # TODO: mark this record as read

finally:
    separator = "{}\n".format("="*10) * 3
    print separator
    print "Ending..."
    # mysql+pymysql://<username>:<password>@<host>/<dbname>[?<options>]
