"""
Generic utility custom pydnatic types 
"""
import datetime
from typing import List, Tuple, Optional
from pydantic import BaseModel as Model, model_validator


class TimeInterval(Model):
    start_at: datetime.time
    end_at: datetime.time

    @model_validator(mode='after')
    def validate_dates(self):
        if self.start_at > self.end_at:
            raise ValueError('start_at must be less than end_at')
        return self

class DatetimeInterval(Model):
    start_at: datetime.datetime
    end_at: datetime.datetime

    @model_validator(mode='after')
    def validate_dates(self):
        if self.start_at > self.end_at:
            raise ValueError('start_at must be less than end_at')
        return self



class WeeklyTimeSchedule(Model):
    """
        Used to store time-only weekly schedules
    """
    sunday: Optional[List[TimeInterval]] = None
    monday: Optional[List[TimeInterval]] = None
    tuesday: Optional[List[TimeInterval]] = None
    wednesday: Optional[List[TimeInterval]] = None
    thursday: Optional[List[TimeInterval]] = None


class DatetimeWeeklySchedule(DatetimeInterval):
    """
        Used to store absolte date-time schedules
    """
    sunday: Optional[List[Tuple[datetime.datetime, datetime.datetime]]]
    monday: Optional[List[Tuple[datetime.datetime, datetime.datetime]]]
    tuesday: Optional[List[Tuple[datetime.datetime, datetime.datetime]]]
    wednesday: Optional[List[Tuple[datetime.datetime, datetime.datetime]]]
    thursday: Optional[List[Tuple[datetime.datetime, datetime.datetime]]]
