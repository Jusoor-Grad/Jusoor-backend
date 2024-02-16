
from datetime import datetime
from typing import List, Tuple

from pytz import utc
from core.types import DatetimeInterval, DatetimeWeeklySchedule, TimeInterval, WeeklyTimeSchedule
from dateutil import rrule
from dateutil.tz import UTC
from ..enums import day_mapper

class TimeUtil:


    @staticmethod
    def generate_intervals(schedule: WeeklyTimeSchedule, schedule_interval: DatetimeInterval) -> DatetimeWeeklySchedule:
        """
            function to generate a list of datetime intervals on same specified days of the week

            @param schedule: a specficiation of time intervals for each day of the week
            @param start_at_schedule: the start date of the schedule
            @param end_at_schedule: the end date of the schedule

            @return: a list of datetime intervals for each day of the week
        """

        intervals: DatetimeWeeklySchedule = {
            'sunday': [],
            'monday': [],
            'tuesday': [],
            'wednesday': [],
            'thursday': []
        }

        schedule_dict = dict(schedule) ## convert into a dict to iterate over all keys
        schedule_end = schedule_interval.end_at
        print(schedule, schedule_interval)

        for day in [ key for key in  schedule_dict.keys() if schedule_dict[key] is not None]:
            for interval in schedule_dict[day]:
                start_at_interval = datetime.combine(schedule_interval.start_at, interval.start_at, tzinfo=utc)
                end_at_interval = datetime.combine(schedule_interval.start_at, interval.end_at, tzinfo=utc )

                
                start_at_intervals = list(rrule.rrule(rrule.WEEKLY, dtstart=start_at_interval, until=schedule_end, byweekday= day_mapper[day]))
                end_at_intervals = list(rrule.rrule(rrule.WEEKLY, dtstart=end_at_interval, until=schedule_end, byweekday= day_mapper[day]))
                
                interval_objs: list[dict[str, datetime]] = [ {'start_at': start_at, 'end_at': end_at} for start_at, end_at in zip(start_at_intervals, end_at_intervals)]
                intervals[day].extend(interval_objs)
                    

        return intervals

    
    @staticmethod
    def check_sequential_conflicts(intervals: List[TimeInterval], sort=True) -> Tuple[bool, List[List[TimeInterval]]]:
        """
            function to check if an interval conflicts with an existing interval

            @param intervals: the intervals to check
            @param sort: a boolean value indicating if the intervals should be sorted before checking for conflicts

            @return: a boolean value indicating if there is a conflict, and a list of conflicting interval pairs
        """
        if sort:
            sorted_intervals = sorted(intervals, key=lambda interval: interval, reverse=False)
        else:
            sorted_intervals = intervals

        sorted_intervals = sorted(intervals, key=lambda interval: interval.start_at, reverse=False)

        interval_conflict_pairs= []

        for i in range(len(sorted_intervals) - 1):
            current_interval = sorted_intervals[i]
            next_interval = sorted_intervals[i + 1]

            if current_interval.end_at > next_interval.start_at:
                interval_conflict_pairs.append([current_interval, next_interval])

        return len(interval_conflict_pairs) > 0, interval_conflict_pairs
