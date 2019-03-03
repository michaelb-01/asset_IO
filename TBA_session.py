import sys

path = '/Library/Python/2.7/site-packages'

if path not in sys.path():
	sys.path.append(path)

from pymongo import MongoClient

class TBA_session():
	print('TBA_Session')

	mongo_client = MongoClient('localhost', 27017)

	