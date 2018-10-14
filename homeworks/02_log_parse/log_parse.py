# -*- encoding: utf-8 -*-

import re
from os import path
from types import SimpleNamespace
from collections import Counter
from urllib import parse as urlparse
from time import strptime


def parse_url(log, args):
    """URL parsing in parameters dependence"""
    url_items = urlparse.urlsplit(log.request_url)

    if args.ignore_files and url_items.path.split('/')[-1] != '':
        return False

    if args.ignore_www and url_items.hostname[:3] == 'www':
        r_value = url_items.hostname[4:] + url_items.path
    else:
        r_value = url_items.hostname + url_items.path

    if args.start_at or args.stop_at:
        date_format = '%d/%b/%Y %H:%M:%S'
        start_datetime = strptime(args.start_at, date_format) if args.start_at else False
        end_datetime = strptime(args.stop_at, date_format) if args.stop_at else False
        log_datetime = strptime(log.request_date + " " + log.request_time, date_format)

        if args.start_at:
            if args.stop_at and not (start_datetime <= log_datetime <= end_datetime) or \
                    not args.stop_at and log_datetime < start_datetime:
                r_value = False
        elif log_datetime > end_datetime:
            r_value = False

    return r_value


def parse_log(line, log, args):
    """Checking that a line is a log line and do parse parameters if so"""
    re_log = r'^\[(\d{1,2}/\w+/\d{4})[ ](\d{1,2}:\d{1,2}:\d{1,2})][ ]\"(\w+)[ ](.*)[ ](.*)\"[ ](\d+)[ ](\d+)'

    r_value = re.match(re_log, line)

    if not r_value:
        return False

    log.request_date = r_value.group(1)
    log.request_time = r_value.group(2)
    log.request_type = r_value.group(3)
    log.request_url = r_value.group(4)
    log.request_protocol = r_value.group(5)
    log.response_code = int(r_value.group(6))
    log.response_time = int(r_value.group(7))

    if args.request_type and log.request_type.lower() != args.request_type.lower():
        return False

    url = parse_url(log, args)

    if not url or args.ignore_urls and url in args.ignore_urls:
        return False
    else:
        return url


def calc_avgtime(urls_count, urls_resptime):
    """Calculating average time for records in urls response time storage"""
    for url, count in urls_count.items():
        if count == 1:
            continue
        urls_resptime[url] //= count


def parse(
    ignore_files=False,
    ignore_urls=[],
    start_at=None,
    stop_at=None,
    request_type=None,
    ignore_www=False,
    slow_queries=False
):
    """Main function for log file processing"""
    log_file = 'log.log'  # Log filename
    if not path.isfile(log_file):
        print("File {} not found".format(log_file))
        exit(1)

    # Human-readable format for log items
    log = SimpleNamespace(
        request_date=None,
        request_time=None,
        request_type=None,
        request_url=None,
        request_protocol=None,
        response_code=None,
        response_time=None
    )

    # Save arguments for convenient access
    args = SimpleNamespace(
        ignore_files=ignore_files,
        ignore_urls=ignore_urls,
        start_at=start_at,
        stop_at=stop_at,
        request_type=request_type,
        ignore_www=ignore_www,
        slow_queries=slow_queries
    )

    out_lst = []  # Output list
    urls_count = Counter()  # URL: count storage
    if args.slow_queries:
        urls_resptime = Counter()  # URL: sum response time storage

    f = open(log_file)  # Open log file

    while True:
        line = f.readline()  # Read a line from the log file

        if line == '':  # Check that the end of the file is reached
            break

        log_url = parse_log(line.rstrip(), log, args)  # Check that the line is a log line and parse it if so

        if not log_url:
            continue
        else:
            urls_count[log_url] += 1
            if args.slow_queries:
                urls_resptime[log_url] += log.response_time

    # end of for

    f.close()  # Close opened file
    top = 5  # TOP-# records from urls

    if args.slow_queries:
        calc_avgtime(urls_count, urls_resptime)  # Calculating average response time for records
        out_lst = [tup[1] for tup in urls_resptime.most_common(top)]
    else:
        out_lst = [tup[1] for tup in urls_count.most_common(top)]

    return out_lst


if __name__ == '__main__':
    parse()
