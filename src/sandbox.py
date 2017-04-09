import datetime

x = datetime.datetime(year=2017, month=4, day=8, hour=12, minute=59, second=59)
y = datetime.datetime(2017, 4, 8, hour=12, minute=13, second=11)

z = y - x

print(int(x.minute))

resolution = 11
def roundDown(time):
    ''''''
    secondsafterhour = (int(time.minute) * 60 + int(time.second)) % resolution
    roundedtime = time - datetime.timedelta(seconds=secondsafterhour)
    return roundedtime

print(roundDown(x))


print('hello\n', 'world')