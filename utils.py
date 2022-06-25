import datetime
import pandas as pd
from dateutil.rrule import rrule, MONTHLY


def get_submission_dates(start_date, end_date, submission_date):
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    dates = [(date + datetime.timedelta(days=submission_date - 1)).strftime('%Y-%m-%d') for date in rrule(MONTHLY, dtstart=start_date, until=end_date)]
    return dates

def get_posting_dates(sheet, today):
    
    # today      = (datetime.datetime.today()).strftime('%Y-%m-%d')
    df_duedate = pd.DataFrame(sheet.get_all_records())
    cond = (pd.to_datetime(df_duedate['edate']) == today)
    sdate = (df_duedate[cond])['sdate']
    edate = (df_duedate[cond])['edate']
    submit_date = (df_duedate[cond])['submit_date']
    if sum(cond) > 0:
        start_date    = datetime.datetime.strptime(sdate.item(), '%Y-%m-%d')  
        end_date      = datetime.datetime.strptime(edate.item(), '%Y-%m-%d')
        submit_date   = datetime.datetime.strptime(submit_date.item(), '%Y-%m-%d')

    else:
        start_date    = datetime.datetime.strptime('1899-01-01', '%Y-%m-%d') 
        end_date      = datetime.datetime.strptime('1899-01-01', '%Y-%m-%d') 
        submit_date   = datetime.datetime.strptime('1899-01-01', '%Y-%m-%d')
    return start_date, end_date, submit_date