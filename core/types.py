import datetime
from typing import List, Tuple
from pydantic import BaseModel as Model


class TimeInterval(Model):
    start_at: datetime.time
    end_at: datetime.time

class DatetimeInterval(Model):
    start_at: datetime.datetime
    end_at: datetime.datetime

class WeeklyTimeSchedule(Model):
    sunday: List[TimeInterval]
    monday: List[TimeInterval]
    tuesday: List[TimeInterval]
    wednesday: List[TimeInterval]
    thursday: List[TimeInterval]


class FutureDatetimeInterval(DatetimeInterval):
    sunday: List[Tuple[datetime.datetime, datetime.datetime]]
    monday: List[Tuple[datetime.datetime, datetime.datetime]]
    tuesday: List[Tuple[datetime.datetime, datetime.datetime]]
    wednesday: List[Tuple[datetime.datetime, datetime.datetime]]
    thursday: List[Tuple[datetime.datetime, datetime.datetime]]
