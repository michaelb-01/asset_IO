import sys
import os

path = '//prospero/apps/utilities/Python27/Lib/site-packages'

if path not in sys.path:
    sys.path.append(path)

from pymongo import MongoClient

sceneDirNames = ['scene', 'scenes', 'hip']

def parse_job_path(path):
    # initialize all to empty string
    job = stage = entity = task = job_path = ''

    parts = path.split(os.sep)

    if 'vfx' in parts:
        vfx_index = parts.index('vfx')

        job = parts[vfx_index - 1]
        stage = parts[vfx_index + 1]
        entity = parts[vfx_index + 2]
    else:
        print("VFX directory not found. Some data is missing")

    # work backwards..
    scene = parts[-1]
    # 'task' should be parent directory of the scene
    task = parts[-2]
    # ignore it if that folder is a scenes directory
    if task.lower() in sceneDirNames:
        task = ''

    return {
        'job': job,
        'stage': stage,
        'entity': entity,
        'task': task,
        'job_path': os.sep.join(parts[:vfx_index])
    }

class db():
	client = None
	db = None

	def __init__(self, host='tbavm1', port=27017, db_name='tag_model'):
		self.client = MongoClient(host, port)
		self.db = self.client[db_name]

	def get_db(self):
		return self.db

	def export_asset(self, new_asset):
		print('tba_utils - export asset')

		# get job tags
		#job_tags =

		# copy current asset to assets_prev
		asset_curr = self.db.assets_curr.find_one({
			'assetName':new_asset['assetName'],
			'assetStage':new_asset['assetStage'],
			'assetEntity':new_asset['assetEntity']
		}, {'_id': False})

		if asset_curr:
			asset_id = self.db.assets_prev.insert_one(asset_curr).inserted_id

			print('tba_utils - Current asset_id: {}'.format(asset_id))

			# update asset_curr
			self.db.assets_curr.update({ '_id': asset_curr['_id'] }, new_asset)
		else:
			asset_id = self.db.assets_curr.insert_one(new_asset).inserted_id

# create class instance
db = db()
