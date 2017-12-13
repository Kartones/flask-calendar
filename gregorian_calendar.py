from calendar import Calendar, monthrange
from datetime import date, datetime, timedelta


class GregorianCalendar:

    MONTH_NAMES = ["January",
                   "February",
                   "March",
                   "April",
                   "May",
                   "June",
                   "July",
                   "August",
                   "September",
                   "October",
                   "November",
                   "December"]

    @staticmethod
    def previous_month_and_year(year, month):
        previous_month_date = date(year, month, 1) - timedelta(days=2)
        return previous_month_date.month, previous_month_date.year

    @staticmethod
    def next_month_and_year(year, month):
        last_day_of_month = monthrange(year, month)[1]
        next_month_date = date(year, month, last_day_of_month) + timedelta(days=2)
        return next_month_date.month, next_month_date.year

    @staticmethod
    def current_date():
        today_date = datetime.date(datetime.now())
        return today_date.day, today_date.month, today_date.year

    @staticmethod
    def month_days(year, month):
        return Calendar().itermonthdates(year, month)

    @staticmethod
    def month_days_with_weekday(year, month):
        return Calendar().monthdayscalendar(year, month)
