import os
import getpass
import datetime

import maya.cmds as mc

import tba_utils

## ASSETS ##
def get_tba_assets():
    tba_sets = mc.ls('tba_asset*', type='objectSet')

    tba_assets = []

    for tba_set in tba_sets:
        asset = {}

        # populate string attributes
        for attr in ['name', 'type', 'stage', 'entity', 'author', 'dateCreated', 'dateUpdated', 'version', 'tags']:
            asset[attr] = mc.getAttr(tba_set + '.' + attr)

        tba_assets.append(asset)

    return tba_assets

def create_tba_assets():
    # get maya selection
    sel = mc.ls(sl=1, transforms=1)

    if not sel:
        print('Selection must be transform nodes')
        return []

    # get environment data
    scene = get_scene_path()

    data = tba_utils.parse_job_path(scene)

    print('Data is {}'.format(data))

    tba_assets = []

    for obj in sel:
        # selected must be a group (cant have any child shapes)
        shapes = mc.listRelatives(obj, shapes=1)

        if shapes:
            print('Skipping {0} since it is not a group node'.format(obj))
            continue

        # strip grp from name
        assetName = obj.split('|')[-1]
        assetName = assetName.lower().split('grp')[0].rstrip('_')

        # create asset object
        asset = {
            'name': assetName,
            'type': data['task'],
            'version': 0,
            'stage': data['stage'],
            'entity': data['entity'],
            'tags': [],
            'author': getpass.getuser(),
            'dateCreated': datetime.datetime.utcnow(),
            'dateUpdated': datetime.datetime.utcnow()
        }

        tbaSet = 'tba_asset_' + assetName

        # ignore if set already exists
        if mc.objExists(tbaSet):
            continue

        tbaSet = mc.sets(obj, name=tbaSet)
        tba_assets.append(asset)

        # set string attributes on maya set
        for attr in ['name', 'type', 'stage', 'entity', 'author', 'dateCreated', 'dateUpdated']:
            mc.addAttr(tbaSet, longName=attr, dataType='string')
            mc.setAttr(tbaSet + '.' + attr, asset[attr], type='string')

        # set tags
        mc.addAttr(tbaSet, longName='tags', dataType='stringArray')
        mc.setAttr(tbaSet + '.tags', 0, type='stringArray')

        # set version
        mc.addAttr(tbaSet, longName='version', attributeType='byte')
        mc.setAttr(tbaSet + '.version', 1)

        # lock set so it cant be renamed
        #mc.lockNode( tbaSet )

    return tba_assets

def get_set_contents(name):
    print('tba_maya_api - get_set_contents')
    # get corresponding set
    tba_set = mc.ls('tba_asset_' + name, type='objectSet')

    if not tba_set:
        return False

    # get set contents
    objs = mc.sets( tba_set, q=True )

    if not objs:
        return False

    return objs

## END ASSETS ##

## FILE ##
def get_scene_path():
    return os.path.abspath(mc.file(q=1, sn=1))


## ABC ##
def export_abc(asset):
    '''
    param: asset [asset] - asset to be exported
    return: success - filepath
    '''

    tba_set = 'tba_asset_' + asset['name']

    rootObjs = get_set_contents(asset['name'])

    if not rootObjs:
        print('TBA set does not contain any valid objects')
        return

    # version up
    asset['version'] += 1

    # create directory if it doesn't exist
    export_dir = os.path.dirname(asset['filepath'])

    if not os.path.exists(export_dir):
        os.makedirs(export_dir)

    root = ''

    for obj in rootObjs:
        root += ' -root ' + obj

    command = '-uvWrite -worldSpace{0} -file {1}'.format(root, asset['filepath'])

    mc.AbcExport ( jobArg = command )

    # update maya set
    tba_sets = mc.ls('tba_asset*', type='objectSet')

    return True
