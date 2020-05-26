import time
import sys

while(True):
	try:
		exec(open('proto.py').read())
		time.sleep(1)
	except:
		print("something happend")
		print(sys.exc_info()[1])
		pass