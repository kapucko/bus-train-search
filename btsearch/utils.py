import re

def slugify(s):
   s = s.lower()
   return re.sub(r'\W+', '_', s)

def time_helper(date, time):
   hour, minute = time.strip().split(':')
   try:
      hour = int(hour)
      minute = int(minute)
      return date.replace(hour=hour, minute=minute)
   except ValueError:
      return date