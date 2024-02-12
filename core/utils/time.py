
from datetime import datetime
from core.types import FutureDatetimeInterval, WeeklyTimeSchedule
from dateutil import rrule
from ..enums import day_mapper

class TimeUtil:


    @staticmethod
    def generate_intervals(schedule: WeeklyTimeSchedule, start_at_schedule: datetime, end_at_schedule: datetime) -> FutureDatetimeInterval:
        """
            function to generate a list of datetime intervals on same specified days of the week

            @param schedule: a specficiation of time intervals for each day of the week
            @param start_at_schedule: the start date of the schedule
            @param end_at_schedule: the end date of the schedule

            @return: a list of datetime intervals for each day of the week
        """

        intervals: FutureDatetimeInterval = {
            'sunday': [],
            'monday': [],
            'tuesday': [],
            'wednesday': [],
            'thursday': []
        } 
        for day in schedule:
            for interval in day:
                start_at_interval, end_at_interval = interval
                start_at_interval = datetime.combine(start_at_schedule, start_at_interval)
                end_at_interval = datetime.combine(start_at_schedule, end_at_interval)

                start_at_intervals = list(rrule.rrule(rrule.WEEKLY, dtstart=start_at_interval, until=end_at_schedule, byweekday= day_mapper[day]))
                end_at_intervals = list(rrule.rrule(rrule.WEEKLY, dtstart=end_at_interval, until=end_at_schedule, byweekday= day_mapper[day]))

                intervals[day] = (list(zip(start_at_intervals, end_at_intervals)))
                    

        return intervals