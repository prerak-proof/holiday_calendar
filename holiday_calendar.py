import argparse
from datetime import date, datetime

import pandas as pd
from exchange_calendars.exchange_calendar_xnys import XNYSExchangeCalendar
from pandas.tseries.holiday import USColumbusDay, Holiday, sunday_to_monday


class USSettlementCalendar(XNYSExchangeCalendar):
    @property
    def regular_holidays(self):
        holidays = super().regular_holidays
        holidays.rules.extend([
            USColumbusDay,
            Holiday("Veterans Day", month=11, day=11, observance=sunday_to_monday),
        ])
        return holidays


def get_calendar(options, look_back=5) -> XNYSExchangeCalendar:
    ref_date = options.pd_date
    start_default = ref_date + pd.Timedelta(days=-look_back)
    end_default = ref_date + pd.Timedelta(days=look_back)
    # print(f"ref={options.pd_date}, look_back={look_back}, start={start_default}, end={end_default}")
    if options.settlement:
        return USSettlementCalendar(start=start_default, end=end_default)
    return XNYSExchangeCalendar(start=start_default, end=end_default)


def is_weekend(options):
    return options.pd_date.dayofweek >= 5


def is_holiday(options):
    # is_weekend exists to avoid creating the calendar if we don't need to (because it's so slow)
    ans = is_weekend(options) or not get_calendar(options).is_session(options.pd_date)
    print_result(options, ans)
    return ans


def is_half_day(options):
    ans = options.pd_date in get_calendar(options).early_closes
    print_result(options, ans)
    return ans


def t_plus_n(options):
    """
    Take a ref date and a series of integer arguments to arrive at the business date.
    For example, action_args=["-1", "2"], will calculate T+2 for the date at T-1, where T is the ref date.
    """
    if not options.action_args:
        options.action_args = [2]

    n_series = list(map(int, options.action_args))
    d = options.pd_date
    look_back = int(abs(sum(n_series)) * 1.5 + 5)
    cal = get_calendar(options, look_back)

    for n in n_series:
        i = abs(n)
        offset_amount = n / i
        while i > 0:
            d = d + pd.DateOffset(offset_amount)
            if cal.is_session(d):
                i -= 1

    print(d.strftime("%Y%m%d"))
    return True


def print_result(options, ans):
    is_settlement = "Settlement " if options.settlement else ""
    print(f'{is_settlement}{options.action}({", ".join(options.action_args)}) for {options.date}: {ans}')


def parse_date(x):
    return datetime.strptime(x, '%Y%m%d').date()


def process_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('date', metavar='DATE', default=date.today(), type=parse_date, help="Ref date", nargs='?')
    parser.add_argument('action_args', help="any command args", nargs='*')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--settlement', default=None, dest='settlement', action='store_true', help='use settlement days')
    group.add_argument('--trading', default=None, dest='settlement', action='store_false', help='use trading days')
    parser.add_argument('--action', choices=['is_holiday', 'is_half_day', 't_plus_n'],
                        default='is_holiday', help="action to perform")
    options = parser.parse_intermixed_args()

    options.pd_date = pd.to_datetime(options.date).tz_localize('UTC')
    if options.settlement is None:
        options.settlement = options.action in ['t_plus_n']

    return options


if __name__ == '__main__':
    opts = process_args()
    answer = locals()[opts.action](opts)
    exit(0 if answer else 1)
