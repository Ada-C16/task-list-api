from datetime import datetime as d1
import datetime as d2

from flask.globals import request


# datetime_object = datetime.strptime(request_body['completed_at'], '%d/%m/%y %H:%M:%S')

# time = "04/11/21 12:07:02"
# date_time_str = '18/09/19 01:55:19'

# time = str(d1.utcnow())
# <class 'datetime.datetime'>
# time_format = ''

# d1.strptime(time, '%Y-%m-%d %H:%M:%S.%f')
# time = "2021-11-04"

# request_time = str(d1.utcnow())

# request_time = "2021-11-04 21:00:13.687356"
time = d1.utcnow()
print(time)
print(type(time))

# request_time = str(d1.utcnow())
# print(d1.strptime(request_time, '%Y-%m-%d %H:%M:%S.%f'))

# d1.strptime(time, '%Y-%m-%d')


# datetime_object = datetime.strptime(time, '%d/%m/%y %H:%M:%S')

## add tests to check if datetime must be a date when creating and updating 

## I"M NOT UPDATING the database with my update routes!! add a test for this!!

# print(datetime.utcnow())


# print(isinstance(time, d2.datetime))
# print(time)
# print(type(time))

# time = 'Thu, 04 Nov 2021 21:53:34 GMT'
# d1.strptime(time, '%Y-%m-%d %H:%M:%S.%f')

# time = 'Thu, 04 Nov 2021 21:53:34 GMT'
# d1.strptime(time, '%a, %d %b %Y %H:%M:%S %z')

time = 'Thu, 04 Nov 2021 21:53:34 GMT'
print(d1.strptime(time, '%a, %d %b %Y %H:%M:%S %Z'))

# print(date)