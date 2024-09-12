# importing the datetime package
import calendar
import datetime


def media_testing_from_to_time_calculation_in_seconds(time_buffer_in_seconds):
    print("\nCurrent time GMT is: " + str(datetime.datetime.utcnow()) + "\n")

    from_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=-int(time_buffer_in_seconds))
    to_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=int(time_buffer_in_seconds))

    time = {"from": calendar.timegm(from_time.timetuple()*1000), "to": calendar.timegm(to_time.timetuple()*1000)}
    return time


def media_testing_from_to_time_calculation_in_minutes(time_buffer_in_minutes):
    from_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=int(time_buffer_in_minutes))
    print(from_time)
    to_time = datetime.datetime.utcnow()
    print(to_time)

    time = {"from": calendar.timegm(from_time.timetuple()*1000), "to": calendar.timegm(to_time.timetuple()*1000)}
    return time