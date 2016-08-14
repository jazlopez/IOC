# Jaziel Lopez <juan.jaziel@gmail.com>
# Software Developer
# http://jlopez.mx

import os
import re
import sys
import datetime
import traceback
import pytz
from pytz import timezone
from sqlalchemy import create_engine, func, Table, MetaData, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import mapper
from sqlalchemy.sql.expression import null, and_
from sqlalchemy.orm.session import sessionmaker


DEFAULT_TAG_ID = 4
traceback_template = '''ERROR:\n File "%(filename)s" line: %(lineno)s,\n in %(message)s''' # Skipping the "actual line" item
tz_pacific_time = timezone('US/Pacific')


def import_raw_data(import_engine):

    import_connection = import_engine.raw_connection()
    cursor = import_connection.cursor()
    cursor.callproc("ioc_sp_import_cache")
    results = list(cursor.fetchall())
    cursor.close()
    import_connection.commit()

    print "Result after import raw data {}".format(results)

def print_analysis_exception():
    # http://docs.python.org/2/library/sys.html#sys.exc_info
    exc_type, exc_value, exc_traceback = sys.exc_info() # most recent (if any) by default

    '''
    Reason this _can_ be bad: If an (unhandled) exception happens AFTER this,
    or if we do not delete the labels on (not much) older versions of Py, the
    reference we created can linger.

    traceback.format_exc/print_exc do this very thing, BUT note this creates a
    temp scope within the function.
    '''

    traceback_details = {
        'filename': exc_traceback.tb_frame.f_code.co_filename,
        'lineno'  : exc_traceback.tb_lineno,
        'name'    : exc_traceback.tb_frame.f_code.co_name,
        'type'    : exc_type.__name__,
        'message' : exc_value.message, # or see traceback._some_str()
    }

    print "\n"
    # Ignore built in exception format message
    print traceback.format_exc()
    print traceback_template % traceback_details

metadata = MetaData()

"""
ioc_scans metadata
"""
ioc_scans = Table('ioc_scans', metadata,
                  Column('id', Integer, autoincrement=True, primary_key=True),
                  Column('process_name', String(512), nullable=False),
                  Column('exact_word', String(1024), nullable=False),
                  Column('is_scrapy_scan', Integer, nullable=False),
                  Column('results_found', Integer, nullable=False),
                  Column('updated_at', DateTime, default=datetime.datetime.now()),
                  Column('last_run_at', DateTime, default=datetime.datetime.now()))

"""
ioc_url_raw metadata
"""

ioc_url_raw = Table('ioc_url_raw', metadata,
                    Column('id', Integer, autoincrement=True, primary_key=True),
                    Column('url_id', Integer, nullable=True),
                    Column('raw', Text, nullable=True))

"""
ioc_url_raws metadata
"""
ioc_scan_raw_urls = Table('ioc_scan_raw_urls', metadata,
                          Column('id', Integer, autoincrement=True, primary_key=True),
                          Column('scan_id',Integer, nullable=False),
                          Column('raw_id',Integer, nullable=False),
                          Column('read', Integer, nullable=False))


ioc_scan_detections = Table('ioc_scan_detections', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('scan_id', Integer, default=0, nullable=False),
    Column('url_id', Integer, default=0, nullable=False),
    Column('raw_id', Integer, default=0, nullable=False),
    Column('detections', Integer, default=0, nullable=False),
    Column('created_at', DateTime, default=datetime.datetime.now()),
    Column('updated_at', DateTime, default=datetime.datetime.now()))

ioc_scan_url_raw_results = Table('ioc_scan_url_raw_results', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('scan_id', Integer, default=0, nullable=False),
    Column('url_id', Integer, default=0, nullable=False),
    Column('raw_id', Integer, default=0, nullable=False),
    Column('tag_id', Integer, default=4, nullable=False),
    Column('created_at', DateTime, default=datetime.datetime.now()),
    Column('updated_at', DateTime, default=datetime.datetime.now()),
    Column('deleted_at', DateTime, nullable=True))

ioc_view_scan_url_raw_results = Table('ioc_view_scan_url_raw_results', metadata,
                    Column('id', Integer, primary_key=True, autoincrement=True),
                    Column('url_id', Integer, primary_key=True),
                    Column('raw', Text, nullable=True))

class IocScans(object):

    def __init__(self, process_name, exact_word, is_scrapy_scan):
        self.process_name = process_name
        self.exact_word = exact_word
        self.is_scrapy_scan = is_scrapy_scan


class IocUrlRaw(object):

    def __init__(self, url_id, raw):
        self.url_id = url_id
        self.raw = raw


class IocScanDetections(object):

    def __init__(self, scan_id, url_id, raw_id, detections):
        self.scan_id = scan_id
        self.url_id = url_id
        self.raw_id = raw_id
        self.detections = detections


class IocScanUrlRawResults(object):

    def __init__(self, scan_id, url_id, raw_id, tag_id):
        self.scan_id = scan_id
        self.url_id = url_id
        self.raw_id = raw_id
        self.tag_id = tag_id


class IocViewUrlRawResults(object):

    def __init__(self,  url_id, raw):
        self.url_id = url_id
        self.raw_id = raw

mapper(IocScans, ioc_scans)
mapper(IocUrlRaw, ioc_url_raw)
mapper(IocViewUrlRawResults, ioc_view_scan_url_raw_results)
mapper(IocScanDetections, ioc_scan_detections)
mapper(IocScanUrlRawResults, ioc_scan_url_raw_results)

engine = create_engine('mysql+pymysql://homestead:secret@localhost:3306/hdv4?charset=utf8', echo=False)
metadata = MetaData()

"""
session factory bound to engine (connection)
"""
sess_maker = sessionmaker(bind=engine)

sess_polling = sess_maker()

try:

    import_raw_data(engine)

    scans = sess_polling\
        .query(IocScans.id, IocScans.exact_word)\
        .filter(and_(IocScans.is_scrapy_scan == 1, IocScans.id >= 0)).limit(10).all()

    print "Scans to be processed:{}".format(len(scans))

    for row in scans:

        # make persistent for commit
        processed_scan = sess_polling.query(IocScans).get(row.id)

        scan_id = row.id
        scan_exact_word = row.exact_word

        analysis_yield_results = False

        # Execute updates
        print "\tStart keyword analysis for {} from scan #: {} ".format(scan_exact_word.encode("utf-8"), scan_id)

        # get raw pending to score for the scan
        # scan_raw_urls = sess_polling.query(ioc_scan_raw_urls.c.raw_id, ioc_url_raw.c.url_id, ioc_url_raw.c.raw)\
        #     .filter(ioc_scan_raw_urls.c.raw_id == ioc_url_raw.c.id)\
        #     .filter(ioc_scan_raw_urls.c.scan_id == scan_id)\
        #     .filter(ioc_scan_raw_urls.c.read == 0).all()

        scan_raw_urls = sess_polling.query(IocViewUrlRawResults.id).all()

        for scan_raw_url in scan_raw_urls:

            raw = sess_polling.query(IocUrlRaw).get(scan_raw_url.id)

            if not raw:
                continue

            detections = 0
            raw_id = raw.id
            raw_text = raw.raw
            url_id = raw.url_id

            clean_exact_word = row.exact_word.strip()
            clean_raw_text = raw_text.strip()

            matches = re.finditer(clean_exact_word, clean_raw_text, flags=re.IGNORECASE)

            if re.findall(clean_exact_word, clean_raw_text, flags=re.IGNORECASE):
                print "By running findall found the following matches: {}"\
                    .format(len(re.findall(clean_exact_word, clean_raw_text, flags=re.IGNORECASE)))

            for match in matches:
                detections += 1

                # TODO: add this line to debug file log
                print "\t\tDetection found: match starts at character index: {} and ends at character index: {}"\
                    .format(match.start(), match.end())

            if detections:

                analysis_yield_results = True

                try:

                    print "\t\tTotal detections found of \"{}\": {}".format(row.exact_word.encode("utf-8"), detections)

                    print "\t\tAttempt to register found detections for scan {} and url {}".format(scan_id, url_id)
                    sess_polling.add(
                        IocScanDetections(scan_id=scan_id, url_id=url_id, raw_id=raw_id, detections=detections))

                    # next add found matches in scan_url_raw_results
                    is_match_stored = sess_polling.query(IocScanUrlRawResults)\
                        .filter(and_(IocScanUrlRawResults.scan_id == scan_id, IocScanUrlRawResults.url_id == url_id, IocScanUrlRawResults.deleted_at == null())).first()

                    if not is_match_stored:

                        print \
                            "\t\tAnalysis will create a key in \"ioc_scan_url_raw_results\" for scan {} and url {}"\
                            .format(scan_id, url_id)

                        sess_polling.add(
                            IocScanUrlRawResults(scan_id=scan_id, url_id=url_id, raw_id=raw_id, tag_id=DEFAULT_TAG_ID))

                        # get new total
                        scan_results = sess_polling.query(IocScanUrlRawResults)\
                            .filter(and_(IocScanUrlRawResults.scan_id == scan_id, IocScanUrlRawResults.deleted_at == null())).all()

                        total_scan_results = sum(1 for _ in scan_results)
                        processed_scan.results_found = total_scan_results

                        print "\t\tTotal Results: {1} for scan# {0}".format(scan_id, total_scan_results)

                    else:

                        print "\t\tKey of scan {} and url {} already found in \"ioc_scan_url_raw_results\""\
                            .format(scan_id, url_id)

                    print "\tCompleted analysis for scan {} and url {}".format(scan_id, url_id)

                except Exception as error:
                    raise Exception(error.message)

        processed_scan.updated_at = datetime.datetime.now()
        processed_scan.last_run_at = datetime.datetime.now()

        sess_polling.commit()

        if not analysis_yield_results:
            print "\tNothing to process for scan #: {}".format(scan_id)

    print "{}\n{}\n{}\n{}\n".format("="* 35, "Author: Jaziel Lopez", "Contact: <juan.jaziel@gmail.com>", "=" * 35)

except Exception as error:

    print_analysis_exception()
finally:

    print "Bye..."

