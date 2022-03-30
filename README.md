# holiday_calendar
A US equities trading &amp; settlement calendar command-line tool

The tool is described here: https://medium.com/@preraksanghvi/7bfe0d9019c7

```
$ python holiday_calendar.py --help
usage: holiday_calendar.py [-h] [--settlement | --trading] [--action {is_holiday,is_half_day,t_plus_n}] [DATE] [action_args [action_args ...]]

positional arguments:
  DATE                  Ref date
  action_args           any command args
                        (for t_plus_n, a series of date offsets that 
                         are successively applied to the ref date)

optional arguments:
  -h, --help            show this help message and exit
  --settlement          use settlement days (default: None)
  --trading             use trading days (default: None)
  --action {is_holiday,is_half_day,t_plus_n}
                        action to perform (default: is_holiday)

--settlement is implied when --action is t_plus_n
```
