try:
    import maya.cmds as mc
    import maya.api.OpenMaya as om
except:
    print('tba_maya_api - Not in maya, cant import')

def export_maya_set(assetName):
    print('tba_maya_api - export_maya_set')
    # get corresponding set
    tba_set = mc.ls('tba_asset_' + assetName, type='objectSet')

    if not tba_set:
        return False

    # get set contents
    objs = mc.sets( tba_set, q=True )

    print('export objects: {0}'.format(objs))

def create_tba_sets():
    # get maya selection
    sel = mc.ls(sl=1, transforms=1)

    tba_sets = []

    for obj in sel:
        # selected must be a group (cant have any child shapes)
        shapes = mc.listRelatives(obj, shapes=1)

        if shapes:
            print('Skipping {0} since it is not a group node'.format(obj))
            continue

        # strip grp from name
        assetName = obj.split('|')[-1]
        assetName = assetName.lower().split('grp')[0].rstrip('_')

        tbaSet = 'tba_asset_' + assetName

        # create maya set if it doesnt already exist
        if not mc.objExists(tbaSet):
            tbaSet = mc.sets(obj, name=tbaSet)
            # lock set so it cant be renamed
            #mc.lockNode( tbaSet )

        tba_sets.append(assetName)

    return tba_sets

def get_maya_assets():
    return mc.ls('tba_asset*', type='objectSet')

def nameChangedCallback(*args):
    """
    :param args[0]: [MObject] the node whose name changed
    :param args[1]: [string] the old name
    :param args[2]: [object] User defined data
    """
    node = args[0]

    # if node is a dag node
    if node.hasFn( om.MFn.kDagNode ):
        path = om.MDagPath.getAPathTo( node )

        # convert the MObject to a dep node
        depNode = om.MFnDependencyNode(node)
        oldName = args[1]

        print('----\nNameChangedCallback')
        print('newName: {0}'.format(depNode.name()))
        print('oldName: {0}'.format(oldName))
        print('type: {0}'.format(depNode.typeName))

def set_asset_callbacks():
    # returns [MObjects] pointing to maya sets beginning with tba_asset_*
    #return mc.ls('tba_asset*', type='objectSet')

    search = 'tba_asset_*'
    selection = om.MSelectionList()
    selection.add(search)

    # filter by name wildcard and by kSet (maya set)
    iter = om.MItSelectionList(selection, om.MFn.kSet )

    cbIds = []

    while not iter.isDone():
        node = iter.getDependNode()

        # gives an internal failure...
        #path = iter.getDagPath()

        cbIds.append(om.MNodeMessage.addNameChangedCallback(node, nameChangedCallback))

        iter.next()

    return

def export_selected():
    print('TBA :: export_selected')

    # get selection
    sel = mc.ls(sl=1)

    if len(sel) < 1:
        mc.warning('Nothing selected')
        return

    print('Export selection: ')
    print(sel)

def nameChangedCallback(*args):
    """
    :param args[0]: [MObject] the node whose name changed
    :param args[1]: [string] the old name
    :param args[2]: [object] User defined data
    """
    node = args[0]

    # if node is a dag node
    if node.hasFn( om.MFn.kDagNode ):
        path = om.MDagPath.getAPathTo( node )

        # convert the MObject to a dep node
        depNode = om.MFnDependencyNode(node)
        oldName = args[1]

        print('----\nNameChangedCallback')
        print('newName: {0}'.format(depNode.name()))
        print('oldName: {0}'.format(oldName))
        print('type: {0}'.format(depNode.typeName))
