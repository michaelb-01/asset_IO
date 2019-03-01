import os
import maya.cmds as mc
from maya import OpenMaya as om

def nameToNode( name ):
	"""Takes a node name(string) and returns an MObject"""

	try:
		selectionList = om.MSelectionList()
		selectionList.add( name )
		node = om.MObject()
		selectionList.getDependNode( 0, node )
		return node	
	except:
		raise RuntimeError('NameToNode() failed on %s' % name)
		
def tbaNameChanged(*args):
    print('tbaNameChanged')
    node = args[0]
    # convert the MObject to a dep node
    depNode = om.MFnDependencyNode(node)
    oldName = args[1]
 
    print '----\nNameChangedCallback'
    print 'newName: ', depNode.name()
    print 'oldName', oldName
    print 'type', depNode.typeName()

def exportAbc(filepath, rootObjs, start, end):
    root = ''
    
    if not isinstance(rootObjs, list):
        root = ' -root ' + rootObjs

    else:
        for obj in rootObjs:
            root += ' -root ' + obj

    abcCmd = " -frameRange {0} {1} -uvWrite -worldSpace{2} -file {3}".format(start, end, root, filepath)
    #abcCmd = " -frameRange " + str(startFrame) + " " + str(endFrame) + " -uvWrite -worldSpace" + root + " -file " + exportPath

    print(abcCmd)
    
def exportDb(doc):
    print('Save doc')
    
def export():
    sel = mc.ls(sl=1, long=1)
    
    if not sel:
        print('Nothing selected')
        return
    
    scene = mc.workspace(q=1,fullName=1)
    
    # find publish folder relative to vfx folder in job
    parts = scene.split(os.sep)
    
    if not 'vfx' in parts:
        print('Could not find "vfx" in your file path')
        return
        
    vfxIdx = parts.index('vfx')
    
    # publish folder
    stage = parts[vfxIdx+1]
    entity = parts[vfxIdx+2]
    
    entityPath = os.sep.join(parts[:vfxIdx+3])
    entityPublishPath = os.path.join(entityPath, '_published3d')
    
    # asset type (selected from UI combobox)
    assetType = 'model'
    
    # export each selected object
    for obj in sel:
        # strip grp from name
        assetName = obj.split('|')[-1]
        assetName = assetName.lower().split('grp')[0].rstrip('_')
        
        assetTypePath = os.path.join(entityPublishPath, assetName, assetType)
        
        assetVersionInt = 1
        # find versions
        # create asset publish folder if it doesnt exist
        if not os.path.isdir(assetTypePath):
            print('Creating asset publish folder for ' + assetName + ' at ' + assetTypePath)
            os.makedirs(assetTypePath)
        # otherwise find the latest version
        else:
            versions = os.listdir(assetTypePath)
            # probably should check if these are actually version folders
            assetVersionInt = len(versions) + 1
        
        # 3 zero padded version string
        assetVersionStr = 'v' + str(assetVersionInt).zfill(3)
        
        # frame range - NEED TO GET THIS FROM UI
        startFrame = 1
        endFrame = 1
        
        assetPath = os.path.join(assetTypePath, assetVersionStr)
        abcPath = os.path.join(assetPath, assetName + '.abc')
        
        #### export alembic ####
        exportAbc(abcPath, obj, startFrame, endFrame)
        
        
        #### export to database ####
        assetDoc = {
            'assetName': assetName
        }
        
        #### create maya sets ####
        tbaSet = 'tba_asset_' + assetName + '_' + assetType
        
        if not mc.objExists(tbaSet):
            tbaSet = mc.sets(obj, name=tbaSet)
            
        #### create node callbacks ####
        mObj = nameToNode(obj)
        cb = om.MNodeMessage.addNameChangedCallback(mObj, tbaNameChanged)
            
        
        print('Export alembic to: ' + abcPath)
        
    
export()

print cb

om.MNodeMessage.removeCallback(cb)
    