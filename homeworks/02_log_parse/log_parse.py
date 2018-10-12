# -*- encoding: utf-8 -*-

from os import path
from types import SimpleNamespace
from urllib import parse as urlparse
from time import strptime


def is_logline(log_items):
    """Checking that a line is a log line"""
    r_value = False
    if len(log_items) == 7:
        try:
            check1 = log_items[0][0]
            check2 = log_items[1][-1]
            if check1 == '[' and check2 == ']':
                r_value = True
        except LookupError:
            pass

    return r_value


def fix_log_items(log_items):
    """Removing redundant chars from log items"""
    log_items['request_date'] = log_items['request_date'][1:]
    log_items['request_time'] = log_items['request_time'][:-1]
    log_items['request_type'] = log_items['request_type'][1:]
    log_items['request_protocol'] = log_items['request_protocol'][:-1]


def get_url(log_items, args):
    """Get url in arguments dependence. Otherwise return None"""
    url_items = urlparse.urlsplit(log_items['request_url'])

    if args.request_type and log_items['request_type'].lower() != args.request_type.lower():
        return None

    if args.ignore_files and url_items.path.split('/')[-1] != '':
        return None

    req_hostname = url_items.hostname

    if args.ignore_www and req_hostname[:3] == 'www':
        req_hostname = req_hostname[4:]

    r_value = req_hostname + url_items.path

    if args.ignore_urls and r_value in args.ignore_urls:
        return None

    if args.start_at or args.stop_at:
        date_format = '%d/%b/%Y %H:%M:%S'
        start_datetime = strptime(args.start_at, date_format) if args.start_at else None
        end_datetime = strptime(args.stop_at, date_format) if args.stop_at else None
        log_datetime = strptime(log_items['request_date'] + " " + log_items['request_time'], date_format)

        if args.start_at:
            if args.stop_at and not(start_datetime <= log_datetime <= end_datetime):
                r_value = None
            elif not args.stop_at:
                if log_datetime < start_datetime:
                    r_value = None
        else:
            if log_datetime > end_datetime:
                r_value = None

    return r_value


def url_storage_update(url_storage, **kwargs):
    """Dictionary updating for url storage: update count and response time"""
    if kwargs['url'] not in url_storage:
        url_storage[kwargs['url']] = {
            'count': 1,
            'response_time': int(kwargs['response_time'])
        }
    else:
        url_storage[kwargs['url']]['count'] += 1
        url_storage[kwargs['url']]['response_time'] += int(kwargs['response_time'])


def calc_avg_time(url_storage):
    """Calculating average response time for records in url storage"""
    for k, v in url_storage.items():
        if v['count'] == 1:
            continue
        v['response_time'] = int(v['response_time'] / v['count'])


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
    true_params = [
        'request_date',
        'request_time',
        'request_type',
        'request_url',
        'request_protocol',
        'response_code',
        'response_time'
    ]

    out_lst = []  # Output list
    url_storage = {}  # Dictionary for urls information storing

    # Open log file
    f = open(log_file)

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

    while True:
        # Get a line from the file
        line = f.readline()

        # Check that the end of the file is reached
        if line == '':
            break

        # Split the log line into items
        log_items = line.rstrip().split()

        # Check that the line is a log line
        if not is_logline(log_items):
            continue

        # Make a dictionary with human-readable format for items
        log_items = dict(zip(true_params, log_items))

        # Fix items by removing bad chars
        fix_log_items(log_items)

        # Get url in arguments dependence
        url = get_url(log_items, args)

        if url:
            # To form arguments for url storage
            store_args = {
                'url': url,
                'response_time': log_items['response_time']
            }
            url_storage_update(url_storage, **store_args)

    # end of for

    # Close opened file
    f.close()

    # TOP-# records from url storage
    top = 5

    # Calculating average response time for records
    calc_avg_time(url_storage)

    if args.slow_queries:
        sort_key = 'response_time'
    else:
        sort_key = 'count'

    for item in sorted(url_storage.items(), key=lambda x: x[1][sort_key], reverse=True):
        if top == 0:
            break
        out_lst.append(item[1][sort_key])
        top -= 1

    return out_lst


if __name__ == '__main__':
    parse()
