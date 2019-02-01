import maya.cmds as mc
import os
import json
import subprocess

windowName = 'TBA_assetImporter'

types = [ 'Geometry', 'Camera', 'Light', 'FX', 'Rig' ]

class maya_asset_importer():
    def __init__(self):

        print('init maya_asset_importer')
        self.main()

    def initUI(self):
        print 'initUI()'
        self.initType()
        self.initAssetList()

    def initType(self):
        print 'initType()'
        # get type of selection and try and initialise type optionMenu
        sel = mc.ls(sl=1)

        if len(sel) == 0:
            return

        nodes = mc.listRelatives(sel[0], children=1)

        type = None

        while not type:
            if not nodes:
                print 'No children, must be an empty transform'
                type = 'transform'
                break

            nodeType = mc.nodeType(nodes[0])

            if nodeType != 'transform':
                type = nodeType
                break

            nodes = mc.listRelatives(nodes[0], children=1)

        if type == 'mesh':
            print 'Found ' + type + ', Initialising as Geometry'
            mc.optionMenuGrp( windowName + '_type', e=1, select=1)
        elif type == 'camera':
            print 'Found ' + type + ', Initialising as Camera'
            mc.optionMenuGrp( windowName + '_type', e=1, select=2)
        elif type == 'joint':
            print 'Found ' + type + ', Initialising as Rig'
            mc.optionMenuGrp( windowName + '_type', e=1, select=5)
            mc.optionMenuGrp( windowName + '_format', e=1, select=3)
        elif 'light' in type.lower():
            print 'Found ' + type + ', Initialising as Light'
            mc.optionMenuGrp( windowName + '_type', e=1, select=3)
            mc.optionMenuGrp( windowName + '_format', e=1, select=3)

    def initAssetList(self):
        print 'initAssetList()'

        # publish directory
        publishDir = getPublishDir()

        # bail if scene not valid
        if not publishDir:
            return

        # get sorted list of assets in the folder
        assets = sorted(os.listdir(publishDir))

        # rebuild the textScrollList with the asset names
        mc.textScrollList(windowName + '_assets', e=1, removeAll=1)

        if not assets:
            return

        for asset in assets:
            mc.textScrollList(windowName + '_assets', e=1, append=asset)

        updateVersionsList()

    def onAssetSelected(self):
        print 'onAssetSelected()'
        # get selected asset from asset list
        asset = mc.textScrollList(windowName + '_assets', q=1, selectItem=1)

        if asset:
            # set name to be selected asset
            mc.textFieldGrp(windowName + '_assetName', e=1, text=asset[0])

        # update version list
        updateVersionsList()

    def onTypeChange(self):
        print 'onTypeChange()'
        # get selected type
        range = mc.radioButtonGrp(windowName + '_range_radio', q=1, select = 1)

        # enable if range is third option (start/end)
        mc.intFieldGrp(windowName + '_range_startEnd', e=1, enable=(range==3))
        mc.floatFieldGrp(windowName + '_range_step', e=1, enable=(range==3))

        updateVersionsList()

    def onRangeChange(self):
        print 'onRangeChange()'
        # get selected radio button
        range = mc.radioButtonGrp(windowName + '_range_radio', q=1, select = 1)

        # enable if range is third option (start/end)
        mc.intFieldGrp(windowName + '_range_startEnd', e=1, enable=(range==3))
        mc.floatFieldGrp(windowName + '_range_step', e=1, enable=(range==3))

    def onVersionTypeChange(self):
        print 'onVersionTypeChange()'

        mode = mc.radioButtonGrp(windowName + '_version_radio', q=1, select=1)

        #mc.textScrollList(windowName + '_versions', e=1, enable=(mode==2))

    def onVersionSelected(self):
        print 'onVersionSelected()'
        publishDir = getPublishDir()

        # bail if scene not valid
        if not publishDir:
            print 'Publish directory not found'
            return

        selVersion = mc.textScrollList(windowName + '_versions', q=1, selectItem=1)

        versionNum = int(filter(str.isdigit, str(selVersion[0])))

        version = 'v' + str(versionNum).zfill(3)

        mc.textFieldGrp(windowName + '_selVersion', e=1, text=version)

        # asset name
        assetName = mc.textFieldGrp(windowName + '_assetName', q=1, text=1)
        # type
        type = mc.optionMenuGrp(windowName + '_type', q=1, value=1).lower()
        # version
        version = mc.textFieldGrp(windowName + '_selVersion', q=1, text=1)
        # import path
        importPath = os.path.join(publishDir, assetName, type, version, assetName)

        # get json path
        jsonPath = importPath + '.json'

        # import json
        with open(jsonPath) as json_file:
            data = json.load(json_file)

        notes = data['notes']

        mc.scrollField(windowName + '_notes', e=1, text=notes)

        checkMetaNode()

    def updateVersionsList(self):
        print 'updateVersionsList()'
        # store selected version and index
        selVersion = mc.textScrollList(windowName + '_versions', q=1, selectItem=1)
        selVersionIdx = mc.textScrollList(windowName + '_versions', q=1, selectIndexedItem=1)

        # remove items in asset list - this will be rebuilt later if a match is found
        mc.textScrollList(windowName + '_versions', e=1, removeAll=1)

        # publish directory
        publishDir = getPublishDir()

        # asset
        asset = mc.textFieldGrp(windowName + '_assetName', q=1, text=1)

        # type
        type = mc.optionMenuGrp(windowName + '_type', q=1, value=1).lower()

        assetPath = os.path.join(publishDir, asset, type)

        if not os.path.isdir(assetPath):
            print 'Could not find asset folder for ' + asset + ' in ' + assetPath
            return

        # get sorted list of versions in the folder
        versions = sorted(os.listdir(assetPath))

        if not versions:
            print 'No versions found'
            # disable button
            mc.button(windowName + '_importButton', e=1, enable=0)
            mc.button(windowName + '_viewChangesButton', e=1, enable=0)
            return

        # enable the import button
        mc.button(windowName + '_importButton', e=1, enable=1)
        mc.button(windowName + '_viewChangesButton', e=1, enable=1)

        for version in versions:
            mc.textScrollList(windowName + '_versions', e=1, append=version)

        # select last version
        print 'select last version'
        if selVersion:
            # select and scroll to previously selected item
            mc.textScrollList(windowName + '_versions', e=1, selectItem=selVersion[0])
            mc.textScrollList(windowName + '_versions', e=1, showIndexedItem=selVersionIdx[0])
        if not selVersion:
            # select and scroll to last item
            mc.textScrollList(windowName + '_versions', e=1, selectItem=versions[-1])
            mc.textScrollList(windowName + '_versions', e=1, showIndexedItem=len(versions))

        onVersionSelected()
        # check meta data set
        checkMetaNode()

    def setAssetOutlineColour(self, objects):
        print 'setAssetOutlineColour()'

        colour = [0.4, 0.7, 1]

        for obj in objects:
            mc.setAttr(obj['name'] + '.outlinerColor', colour[0], colour[1], colour[2] )
            mc.setAttr(obj['name'] + '.useOutlinerColor', 1)

    def updateMetaNode(self, importPath):
        print 'updateMetaNode()'

        # get json path
        jsonPath = importPath + '.json'

        # import json
        with open(jsonPath) as json_file:
            data = json.load(json_file)

        # imported objects - assume these exist now they have been imported...
        importedObjs = []

        # update the outliner colour
        setAssetOutlineColour(data['objects'])

        # iterate over objects in json file and store their names
        for obj in data['objects']:
            importedObjs.append( obj['name'] )

        # select imported objects
        mc.select(importedObjs, replace=1)

        # create TBA meta set to store what asset version is in the scene
        # asset name
        assetName = mc.textFieldGrp(windowName + '_assetName', q=1, text=1)

        # version
        assetVersion = mc.textFieldGrp(windowName + '_selVersion', q=1, text=1)

        # metaNodeName
        metaNodeName = 'TBA_asset_' + assetName

        # remake set
        if mc.objExists(metaNodeName):
            mc.delete(metaNodeName)

        mc.sets( importedObjs, name=metaNodeName )

        # add assetVersion attribute
        mc.addAttr(metaNodeName, shortName='assetVersion', dataType='string')
        # update attrs on meta node (and lock them)
        mc.setAttr(metaNodeName+'.assetVersion', assetVersion, type='string')

    def createMetaNode(self):
        # asset name
        assetName = mc.textFieldGrp(windowName + '_assetName', q=1, text=1)

        metaNodeName = 'TBA_asset_' + assetName

        print 'Creating ' + metaNodeName + ' set for ' + assetName

        # return if meta node already exists
        if mc.objExists(metaNodeName):
            return

        # create set
        tbaSet = mc.sets(name=metaNodeName)

        #mc.createNode('unknown', name=metaNodeName)
        # create asset name attr
        #mc.addAttr(metaNodeName, shortName='assetName', dataType='string')
        # create asset version attr
        print 'add assetVersion attr to ' + tbaSet
        mc.addAttr(metaNodeName, shortName='assetVersion', dataType='string')
        # create asset objects attr
        #mc.addAttr(metaNodeName, shortName='assetObjs', dataType='string')

    def checkMetaNode(self):
        print 'checkMetaNode()'
        # asset name
        assetName = mc.textFieldGrp(windowName + '_assetName', q=1, text=1)

        metaNodeName = 'TBA_asset_' + assetName

        #  return if can't find the set
        if not mc.objExists(metaNodeName):
            print 'TBA_asset set does not exists, returning'
            return

        # get meta node objs, iterate over them and select them if they exist
        rootObjs = mc.sets( metaNodeName, q=True )

        if not rootObjs:
            print 'TBA asset set contains no children...'
            return

        mc.select(rootObjs, replace=1)

        return

        # data = mc.getAttr(metaNodeName + '.assetObjs')

        # if not data:
        #     return

        # dataJson = json.loads(data)

        # print data
        # print dataJson

        # numFound = 0

        # for obj in dataJson:
        #     # get id of object
        #     objId = obj.values()[0]

        #     print 'Object id: ' + objId

        #     objName = mc.ls(objId)

        #     if objName:
        #         if numFound == 0:
        #             mc.select(deselect=1)

        #         mc.select(objName, add=1)

    def viewChanges(self):
        publishDir = getPublishDir()

        # bail if scene not valid
        if not publishDir:
            print 'Publish directory not found'
            return

        # asset name
        assetName = mc.textFieldGrp(windowName + '_assetName', q=1, text=1)
        # type
        type = mc.optionMenuGrp(windowName + '_type', q=1, value=1).lower()
        # version
        version = mc.textFieldGrp(windowName + '_selVersion', q=1, text=1)
        # format
        assetFormat = mc.optionMenuGrp(windowName + '_format', q=1, value=1)
        # import path
        importPath = os.path.join(publishDir, assetName, type, version, assetName)

        metaNodeName = 'TBA_asset_' + assetName

        # arrays to nodes found in both, found only in maya, and found only on disk
        matchedNodes = []
        onlyMayaNodes = []
        onlyJsonNodes = []

        # array to store root (long name) nodes
        rootNodes = []

        # array to store nodes currently in maya
        mayaNodes = []

        # get meta node objs
        if mc.objExists(metaNodeName):
            mayaNodes = mc.sets( metaNodeName, q=True )
        else:
            print 'TBA asset set does not exist'

        # get json path
        jsonPath = importPath + '.json'

        # import json
        with open(jsonPath) as json_file:
            data = json.load(json_file)

        # iterate over json objects and try and find by ID in maya
        for obj in data['objects']:
            print 'Checking: ' + obj['name']

            # iterate over all maya nodes and check if their tbaAssetID matches, and check if their name changed..
            for shortName in mayaNodes:
                # ensure long name so we can check for any reparenting. Remove first vertical bar since assets are always exported at the root..
                longName = mc.ls(shortName, long=1)[0][1:]
                if not mc.attributeQuery( 'tbaAssetID', node=longName, exists=1 ):
                    print 'Counldnt find tbaAssetID on ' + shortName
                    continue

                mayaAssetId = mc.getAttr( longName + '.tbaAssetID')

                if mayaAssetId == obj['id']:
                    print 'Found match for ' + shortName + ', originally called ' + obj['name']
                    nameMisatch = shortName != obj['name']
                    parentMismatch = longName.count('|') > 0
                    matchedNodes.append({'mayaName':shortName, 'assetName':obj['name'], 'nameMisatch':nameMisatch, 'parentMismatch':parentMismatch})
                    rootNodes.append(longName)
                    break
            # if no maya node was found, the node only exists in json
            else:
                onlyJsonNodes.append(obj['name'])

        return rootNodes

        # show data
        print '\nNodes found in both:'
        print matchedNodes

        print '\nNodes found only on disk:'
        print onlyJsonNodes

        print '\nNodes found only in Maya:'
        print onlyMayaNodes

        changesWindow = 'TBA_asset_comparison'

        # variables
        windowWidth = 500
        windowHeight = 300
        colWidth = (windowWidth/2) - 2

        # if windows already exists, delete it
        if mc.window(changesWindow,exists=1):
            mc.deleteUI(changesWindow)

        # create window
        window = mc.window(changesWindow, title="TBA Asset Comparison", iconName=changesWindow, widthHeight=(windowWidth, windowHeight) )

        mc.columnLayout()

        mc.rowLayout( numberOfColumns=2, columnWidth2=(colWidth, colWidth) )

        mc.text(label='Matched Nodes')
        mc.text(label='Not found in Maya')

        mc.setParent('..')

        mc.rowLayout( numberOfColumns=2, columnWidth2=(colWidth, colWidth) )

        matchedList = mc.textScrollList( numberOfRows=4, width=colWidth )
        jsonList = mc.textScrollList( numberOfRows=4, width=colWidth )

        # create text items for matched nodes
        for node in matchedNodes:
            text = node['mayaName']
            if node['nameMisatch']:
                if node['parentMismatch']:
                    text += ' (name mismatch, parent mismatch)'
                else:
                    text += '(name mismatch)'
            elif node['parentMismatch']:
                text += ' (parent mismatch)'

            # append item
            mc.textScrollList(matchedList, e=1, append=text)

        # create text items for json only nodes
        for node in onlyJsonNodes:
            # append item
            mc.textScrollList(jsonList, e=1, append=node)

        mc.showWindow(window)

    def importAsset(self):
        publishDir = getPublishDir()

        # bail if scene not valid
        if not publishDir:
            return

        # asset name
        assetName = mc.textFieldGrp(windowName + '_assetName', q=1, text=1)

        # type
        type = mc.optionMenuGrp(windowName + '_type', q=1, value=1).lower()

        # version
        version = mc.textFieldGrp(windowName + '_selVersion', q=1, text=1)

        # format
        assetFormat = mc.optionMenuGrp(windowName + '_format', q=1, value=1)

        # import path
        importPath = os.path.join(publishDir, assetName, type, version, assetName)

        abcPath = importPath + '.' + assetFormat
        connectNodes = ''

        # if there are any nodes in the TBA asset set, try and connect them
        rootNodes = viewChanges()

        print 'Root nodes: '
        print rootNodes

        for node in rootNodes:
            connectNodes += node + ' '

        print 'Importing from ' + abcPath
        print 'Merging nodes: ' + connectNodes

        # IMPORT ASSET
        if connectNodes == '':
            mc.AbcImport(abcPath, createIfNotFound=1, removeIfNoUpdate=1)
        else:
            mc.AbcImport(abcPath, connect=connectNodes, createIfNotFound=1, removeIfNoUpdate=1)

        #### GET IMPORTED GEO ####
        # get json path
        jsonPath = importPath + '.json'

        # import json
        with open(jsonPath) as json_file:
            data = json.load(json_file)

        # iterate over objects in json file and (if they were imported correctly) add an attribute storing their export uuid
        assetIdAttr = 'tbaAssetID'

        for obj in data['objects']:
            # skip if object doesn't exist (can't have imported properly)
            if not mc.objExists(obj['name']):
                print 'Didnt find ' + obj['name']
                continue

            # if tbaAssetID attr doesn't exists add it
            if not mc.attributeQuery( assetIdAttr, node=obj['name'], exists=1 ):
                mc.addAttr(obj['name'], shortName=assetIdAttr, dataType='string')

            # make sure attr is unlocked
            mc.setAttr(obj['name'] + '.' + assetIdAttr, lock=0)
            # set id attr to the exported uuid value and lock
            mc.setAttr(obj['name'] + '.' + assetIdAttr, obj['id'], type='string', lock=1)


        # read json and check if objects exist in the scene, if so select them
        updateMetaNode(importPath)

        # set the colour of the select objects in the outliner to signify a TBA asset
        #setAssetOutlineColour()
        #updateVersionsList()
        #initAssetList()

    def getPublishDir(self):
        # current scene
        scene = mc.workspace(q=1,fullName=1)

        print 'Scene Path'
        print scene

        # publish3d/assets folder - should be directly above the maya folder, if not create it
        publishDir = os.path.join(os.path.dirname(scene), '_published3d', 'assets')

        print 'Publish Dir'
        print publishDir

        if not os.path.exists(publishDir):
            print('Could not find a _publish3d scene above the maya folder: {0}'.format(publishDir))
            return False
        else:
            return publishDir

    def main(self):
        publishDir = self.getPublishDir()

        # bail if scene not valid
        if not publishDir:
            return

        # bail if nothing is selected (currently only transforms!...)
        #sel = mc.ls(sl=True, transforms=1, shapes=1)

        #if len(sel) < 1:
        #    print 'Nothing selected'
        #    return

        # variables
        windowWidth = 260
        windowHeight = 300
        colWidth1 = 80
        colWidth2 = 100

        # if windows already exists, delete it
        if mc.window(windowName,exists=1):
            mc.deleteUI(windowName)

        # create window
        window = mc.window(windowName, title="TBA Asset Importer", iconName=windowName, widthHeight=(windowWidth, windowHeight) )
        print window
        mc.frameLayout( labelVisible=0, marginWidth=5, marginHeight=5 )
        mc.columnLayout()

        # new asset name
        mc.textFieldGrp( windowName + '_assetName',
                         label = 'Asset Name:',
                         columnWidth2=[colWidth1, colWidth2],
                         columnAlign=[1,'left'],
                         enable=0)

        # current assets list
        mc.text( label='Existing Assets:' )
        mc.textScrollList( windowName + '_assets',
                           numberOfRows=4,
                           selectCommand=lambda *args: self.onAssetSelected() )

        # auto version up or overwrite old version
        mc.radioButtonGrp( windowName + '_version_radio',
                             labelArray2=['Auto Version', 'Overwrite'],
                             numberOfRadioButtons=2,
                             columnWidth2=[windowWidth/2, windowWidth/2],
                             columnAlign=[1,'left'],
                             changeCommand=lambda *args: self.onVersionTypeChange(),
                             select=1 )

        # asset versions
        mc.text( label='Asset Versions:' )
        mc.textScrollList( windowName + '_versions',
                           numberOfRows=4,
                           selectCommand=lambda *args: self.onVersionSelected())

        # selected version
        mc.textFieldGrp( windowName + '_selVersion',
                         label = 'Import Version:',
                         text = '',
                         columnWidth2=[colWidth1, colWidth2],
                         columnAlign=[1,'left'],
                         enable=0)

        # view changes button
        mc.button( windowName + '_viewChangesButton', label='View Changes', command=lambda *args: self.viewChanges(), width=windowWidth, enable=0)

        # asset type
        mc.optionMenuGrp( windowName + '_type',
                                        label='Type:',
                                        columnWidth2=[colWidth1, colWidth2],
                                        columnAlign=[1,'left'],
                                        changeCommand=lambda *args: self.onTypeChange())

        for type in types:
            mc.menuItem( label = type )

        # formats
        mc.optionMenuGrp( windowName + '_format',
                                        label='Format:',
                                        columnWidth2=[colWidth1, colWidth2],
                                        columnAlign=[1,'left'])

        mc.menuItem( label = 'abc' )
        mc.menuItem( label = 'obj' )
        mc.menuItem( label = 'mb' )
        mc.menuItem( label = 'fbx' )

        # frame range
        mc.radioButtonGrp( windowName + '_range_radio',
                             label='Frame Range:',
                             labelArray3=['Current Frame', 'Time Slider', 'Start/End'],
                             numberOfRadioButtons=3,
                             vertical=1,
                             columnWidth2=[colWidth1, colWidth2],
                             columnAlign=[1,'left'],
                             changeCommand=lambda *args: self.onRangeChange(),
                             select=1 )

        # get start/end frame
        startFrame = mc.playbackOptions(q=1, minTime=1)
        endFrame = mc.playbackOptions(q=1, maxTime=1)
        mc.intFieldGrp( windowName + '_range_startEnd',
                          numberOfFields=2,
                          label='Start/End:',
                          value1=startFrame,
                          value2=endFrame,
                          columnWidth3=[colWidth1, 50, 50],
                          columnAlign=[1,'left'],
                          enable=0 )

        # step
        mc.floatFieldGrp( windowName + '_range_step',
                            numberOfFields=1,
                            label='Step:',
                            value1=1.0,
                            columnWidth2=[colWidth1, 50],
                            columnAlign=[1,'left'],
                            enable=0 )

        # notes
        mc.text(label='Notes:')
        mc.scrollField( windowName + '_notes', editable=True, numberOfLines=3, height=60, wordWrap=True )

        # export button
        mc.button( windowName + '_importButton', label='Import', command=lambda *args: self.importAsset(), width=windowWidth, enable=0)

        mc.window(window, e=1, width=windowWidth, height=windowHeight)

        initUI()

        mc.showWindow( window )

