import datetime
from dateutil.rrule import rrule, MONTHLY


def get_submission_dates(start_date, end_date, submission_date):
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    dates = [(date + datetime.timedelta(days=submission_date - 1)).strftime('%Y-%m-%d') for date in rrule(MONTHLY, dtstart=start_date, until=end_date)]
    return dates
