# "1083833826:AAHrO0D-wTS0HVbgzhbUpL632bH_B5yCiio"
from datetime import (
    datetime
)


def _main():
    # datetime_object = datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')
    # datetime_object = datetime.strptime("1994-08-07", "%Y-%m-%d")
    # print(datetime_object,
    #       datetime_object.year, datetime_object.month, datetime_object.day,
    #       datetime_object.hour, datetime_object.minute, datetime_object.second)
    date = datetime(2020, 3, 24, 22, 33, 25, 0)
    print(date.strftime("%Y-%m-%d"))


if __name__ == "__main__":
    _main()
