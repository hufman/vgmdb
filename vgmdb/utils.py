
def parse_date_time(time):
	""" 
	Receives a string like Mar 23, 1223
	Returns 1223-03-23

	Receives a string like Mar 23, 1223 01:33 PM
	Returns 1223-03-23T13:33
	"""
	months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', \
	          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
	month = time[0:3]
	month = months.index(month) + 1
	comma = time.find(',')
	day = int(time[4:comma])
	year = int(time[comma+2:comma+2+4])
	timepos = comma+2+4+1
	if timepos >= len(time):		# there is not a time to parse
		return "%02d-%02d-%02d"%(year,month,day)
	else:
		hour = int(time[timepos:timepos+2])
		minute = int(time[timepos+3:timepos+5])
		ampm = time[timepos+6:timepos+8]
		if ampm == 'PM':
			hour += 12
		return "%02d-%02d-%02dT%02d:%02d"%(year,month,day,hour,minute)

