from datetime import date, timedelta
import re
startdate='2021-03-23'
enddate='2021-04-12'

startdate_fragments = re.split("-", startdate)
enddate_fragments = re.split("-", enddate)

sdate = date(int(startdate_fragments[0]), int(startdate_fragments[1]), int(startdate_fragments[2]))   # start date
edate = date(int(enddate_fragments[0]), int(enddate_fragments[1]), int(enddate_fragments[2]))   # end date

delta = edate - sdate       # as timedelta

for i in range(delta.days + 1):
    currentdate = re.split("-", str(sdate + timedelta(days=i)))
    year = int(currentdate[0])  # type: Optional[int]
    month = int(currentdate[1])  # type: Optional[int]
    day = int(currentdate[2])  # type: Optional[int]

    print(year,month,day)
