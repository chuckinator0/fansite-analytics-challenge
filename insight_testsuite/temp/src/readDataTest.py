# outputPath = 'log_output/my_output'

# output = open(outputPath, 'w')
# with open(logPath, 'r') as logFile:
#     for line in logFile:
#         line = line.split()
#         print(line)
#         # print(line[5][1:], file = output) #prints 'Get' or 'Post' to an output file.
# output.close()

'''Data Description from logFile (list of strings after splitting each line in the logFile):
Index 0: 'host'
Index 1: '-'
Index 2: '-'
Index 3: '[DD/Mon/YYYY:HH:MM:SS' (need to splice to get rid of leading bracket)
Index 4: '-0400]' (need to splice to get rid of ending bracket)
Index 5: '"POST' or '"GET'
Index 6: 'resource' (login, load site, etc)
Index 7: 'HTTP/1.0"' (this index is sometimes omitted and I'm not sure why)
Index 8: 'reply code'
Index 9: 'bytes' in reply (where '-' means 0)
'''

logPath = 'log_input/log.txt'
hoursPath = 'log_output/hours.txt'
hostsPath = 'log_output/hosts.txt'
blockedPath = 'log_output/blocked.txt'
resourcesPath = 'log_output/resources.txt'

'''Open input and output files'''
hoursFile = open(hoursPath, 'w')
hostsFile = open(hostsPath, 'w')
blockedFile = open(blockedPath, 'w')
resourcesFile = open(resourcesPath, 'w')

'''topTen function'''


# This function takes a {key : value} dictionary and produces a top ten list in descending order by value.
# Each element of the top ten list has the form [key, value].
# This function will be used in features 1 and 2.
def topTen(dictionary):
    topTen = []
    for key in dictionary:
        value = dictionary[key]
        entry = [key, value]
        if len(topTen) < 10:
            topTen.append(entry)
            continue
        # sort topTen in increasing order of value
        topTen.sort(key=lambda x: x[1])
        # set minimum number of accesses in the topTen list
        minimum = topTen[0][1]
        # replace minimum element of topTen if a bigger accessCount comes along.
        if value > minimum:
            topTen[0] = entry
    # sort topTen one last time
    topTen.sort(key=lambda x: x[1])
    # reverse topTen to give the results in descending order
    topTen.reverse()
    return topTen


'''Feature 1'''
# Create host dictionary of the form {host : number of accesses by host}
hostDict = {}
with open(logPath, 'r') as logFile:
    for line in logFile:
        lineSplit = line.split()
        host = lineSplit[0]
        # if new host is already in the dictionary, add 1 to the number of accesses.
        if host in hostDict:
            hostDict[host] += 1
        # if new host is not in the dictionary yet, put it in the dictionary and set number of accesses to 1
        else:
            hostDict[host] = 1

# create a topTen list in descending order by number of accesses
topHosts = topTen(hostDict)
# output to hosts.txt.txt
for x in topHosts:
    print(x[0] + ',' + str(x[1]), file=hostsFile)

'''Feature 2'''
# Create resource dictionary of the form {resource : bytes over network}
resourceDict = {}
with open(logPath, 'r') as logFile:
    for line in logFile:
        lineSplit = line.split()
        # ignore 404 errors that give '-' for bytes
        if lineSplit[-1] != '-':
            resource = lineSplit[6]
            dataBytes = int(lineSplit[-1])
            if resource in resourceDict:
                resourceDict[resource] += dataBytes
            else:
                resourceDict[resource] = dataBytes
        else:
            continue

# Create a topTen list in descending order by bytes.
topResources = topTen(resourceDict)
# Output to resources.txt.txt
for x in topResources:
    print(x[0], file=resourcesFile)

'''Feature 3'''
# The requirements say, 'A 60-minute window can be any 60 minute long time period, windows don't have to start at a time
# when an event occurs.' However, a window that doesn't start with an event is always less busy than the window that
# begins at the next event, so this comment in the requirements seems superfluous.

# This feature keeps in mind that the data is given in chronological order with the same time zone.

# The datetime module will help test if a time is within an hour of another time.
import datetime


# monthNumber translates the 3-letter month abbreviation to the month number.
def monthNumber(abbrev):
    return {
        'Jan': 1,
        'Feb': 2,
        'Mar': 3,
        'Apr': 4,
        'May': 5,
        'Jun': 6,
        'Jul': 7,
        'Aug': 8,
        'Sep': 9,
        'Oct': 10,
        'Nov': 11,
        'Dec': 12
    }[abbrev]


# monthAbbr translates the month number to the 3-letter month abbreviation.
def monthAbbr(number):
    monthlist = [
        'Jan',
        'Feb',
        'Mar',
        'Apr',
        'May',
        'Jun',
        'Jul',
        'Aug',
        'Sep',
        'Oct',
        'Nov',
        'Dec'
    ]
    return monthlist[number - 1]


# convertdatetime takes a line of data and returns its associated Python datetime object.
def convertdatetime(line):
    lineSplit = line.split()
    # t is the time in the data
    t = lineSplit[3]
    # splice t to get the year, month, day, hour, minute, and second.
    return datetime.datetime(
        year=int(t[8:12]),
        month=monthNumber(t[4:7]),
        day=int(t[1:3]),
        hour=int(t[13:15]),
        minute=int(t[16:18]),
        second=int(t[19:21])
    )

# This function converts a datetime object to the specified output format for hours.txt.txt
def convertHours(time):
    timestr = str(time)
    year = timestr[0:4]
    month = monthAbbr(int(timestr[5:7]))
    day = timestr[8:10]
    hour = timestr[11:13]
    minute = timestr[14:16]
    second = timestr[17:19]
    return day + '/' + month + '/' + year + ':' + hour + ':' + minute + ':' + second


# Create hours.txt dictionary of the form {starting time: number of accesses to the site in the following hour}.
# Starting time is a Python datetime object.
hoursDict = {}
# The change in time for this feature is 1 hour
delta = datetime.timedelta(hours=1)
with open(logPath, 'r') as logFile:
    for line in logFile:
        time = convertdatetime(line)
        if time not in hoursDict:
            hoursDict[time] = 1
        else:
            hoursDict[time] += 1
        x = time - datetime.timedelta(seconds=1)
        while x > time - delta:
            if x in hoursDict:
                hoursDict[x] += 1
            x = x - datetime.timedelta(seconds=1)

# Make topTen list of busiest 1-hour windows
topHours = topTen(hoursDict)

# Output to hours.txt.txt
for i in topHours:
    print(convertHours(i[0]) + ' -0400,' + str(i[1]), file=hoursFile)

'''Feature 4'''

# Create dictionary to track failed logins for possible future blocking. The dictionary has the form
# {host: [list of times of attempted logins] }. This feature assumes the logins are processed in chronological order.
failed = {}

# Create dictionary for hosts who have violated the condition of 3 failures in 20 seconds to indicate that they should
# be blocked for the next 5 minutes. This dictionary has the form {host: cooldown time}. All attempted logins by the
# host before the cooldown time will be printed to blocked.txt.
blocked = {}

with open(logPath, 'r') as logFile:
    for line in logFile:
        lineSplit = line.split()
        resource = lineSplit[6]
        if resource == '/login':
            host = lineSplit[0]
            time = convertdatetime(line)
            replyCode = lineSplit[-2]
            if host in blocked:
                if time > blocked[host]:
                    del failed[host]
                    del blocked[host]
                else:
                    print(line, file=blockedFile)
                    continue
            if replyCode == '401':
                if host in failed:
                    failed[host].append(time)
                else:
                    failed[host] = []
                    failed[host].append(time)
                if len(failed[host]) >= 3 and failed[host][-1] - failed[host][-3] < datetime.timedelta(seconds=20):
                    cooldowntime = time + datetime.timedelta(minutes=5)
                    blocked[host] = cooldowntime
            elif replyCode == '200':
                if host in failed:
                    del failed[host]
                    del blocked[host]




'''Testing output structure'''
# with open(logPath, 'r') as logFile:
#     for line in logFile:
#         lineSplit = line.split()
#         byteSize = lineSplit[-1]
#         print(lineSplit[-1])

#
# # hours.txt
# print(firstLine[3][1:] + ' ' + firstLine[4][:len(firstLine[4])-1] + ',' + '%s' %'10', file=hoursFile)
#
# # hosts.txt
# print(firstLine[0] + ',' + '%s' %'6', file=hostsFile)
#
# # blocked.txt
# # here the output is just the whole line as a single string. join() undoes split()
# print(' '.join(firstLine), file=blockedFile)
#
# #resources.txt
# print(firstLine[6] , file=resourcesFile)

'''Close input and output files'''
hoursFile.close()
hostsFile.close()
blockedFile.close()
resourcesFile.close()
