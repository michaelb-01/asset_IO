import sys

path = '/Library/Python/2.7/site-packages'

if path not in sys.path:
    sys.path.append(path)

from pymongo import MongoClient

def test():
	print('test')

class db():
	client = MongoClient('localhost', 27017)
	db = client.tba

	@staticmethod
	def export_asset(asset):
		print('tba_utils - export asset')
		print(asset)

		print(db.client)
		print(db.db)

		# copy current asset to assets_prev
		asset_curr = db.db.assets.find_one({
			'assetName':asset['assetName'], 
			'assetStage':asset['assetStage'],
			'assetEntity':asset['assetEntity']
		}, {'_id': False})

		if asset_curr:
			asset_id = db.db.assets_versions.insert_one(asset_curr).inserted_id

		asset_id = db.db.assets.insert_one(asset).inserted_id