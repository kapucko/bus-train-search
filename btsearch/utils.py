import re

def slugify(s):
   s = s.lower()
   return re.sub(r'\W+', '_', s)