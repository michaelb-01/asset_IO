import sys
import os
import json
import subprocess

import maya.cmds as mc

windowName = 'TBA_assetExporter'

types = [ 'Geometry', 'Camera', 'Light', 'FX', 'Rig' ]

class maya_asset_exporter():
    def __init__(self):
        print('init maya_asset_exporter')

        self.main()

    def refresh(self, *args):
        updateAssetList()
        updateVersionsList()

    def updateAssetList(self):
        # publish directory
        exportDir = self.getExportDir()

        # bail if scene not valid
        if not exportDir:
            return

        # get sorted list of assets in the folder
        assets = sorted(os.listdir(exportDir))

        # rebuild the textScrollList with the asset names
        mc.textScrollList(windowName + '_assets', e=1, removeAll=1)

        if not assets:
            return

        for asset in assets:
            mc.textScrollList(windowName + '_assets', e=1, append=asset)

        self.updateVersionsList()

    def updateVersionsList(self):
        # store selected index
        selVersion = mc.textScrollList(windowName + '_versions', q=1, selectItem=1)

        # remove items in asset list - this will be rebuilt later if a match is found
        mc.textScrollList(windowName + '_versions', e=1, removeAll=1)

        # publish directory
        exportDir = getExportDir()

        # asset
        asset = mc.textFieldGrp(windowName + '_assetName', q=1, text=1)

        # type
        type = mc.optionMenuGrp(windowName + '_type', q=1, value=1).lower()

        assetPath = os.path.join(exportDir, asset, type)

        if not os.path.isdir(assetPath):
            print 'Could not find asset folder for ' + asset + ' in ' + assetPath
            return

        # get sorted list of versions in the folder
        versions = sorted(os.listdir(assetPath))

        if not versions:
            return

        for version in versions:
            mc.textScrollList(windowName + '_versions', e=1, append=version)

        # if version mode is set to auto verison scroll to last item and update 'writeVersion'
        if mc.radioButtonGrp(windowName + '_version_radio', q=1, select=1) == 1:
            mc.textScrollList(windowName + '_versions', e=1, showIndexedItem=len(versions))

            # update selected version
            versionNum = int(filter(str.isdigit, str(versions[-1])))
            # increment
            versionNum += 1

            version = 'v' + str(versionNum).zfill(3)

            mc.textFieldGrp(windowName + '_selVersion', e=1, text=version)

        # if version mode is 'overwrite' then re-select selected text
        else:
           if selVersion:
               mc.textScrollList(windowName + '_versions', e=1, selectItem=selVersion[0])

    def getLatestVersion(self, exportPath):
        if not os.path.isdir(exportPath):
            print 'No versions for asset found, must be the first export'
            return 0

        # get folders within export path
        dirs = os.listdir(exportPath)

        return len(dirs)

    def exportAssetJsonFile(self, assetPath, assetName, assetVersion, dryRun=None):
        # make export path for json file
        jsonPath = os.path.join(assetPath, assetName) + '.json'

        if dryRun:
            print 'Asset json export path is ' + jsonPath
            return

        # get notes
        notes = mc.scrollField(windowName + '_notes', q=1, text=1)

        # build json data
        data = {}

        data['assetName'] = assetName
        data['assetVersion'] = assetVersion
        data['notes'] = notes

        dataObjs = []

        # add selected objects
        sel = mc.ls(selection=1)

        for obj in sel:
            objData = {}
            # add short name of object
            objData['name'] = obj.split('|')[-1]
            # add unique id from root object
            objData['id'] = mc.ls(obj, uuid=1)[0]

            dataObjs.append(objData)

        data['objects'] = dataObjs

        # delete if already exists
        if os.path.exists(jsonPath):
            os.remove(jsonPath)

        # write json file
        with open(jsonPath, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)

        print 'Created a hidden json file here:'
        print outfile

        # make file hidden
        subprocess.check_call(["attrib","+H",jsonPath])

    def exportAbc(self, dryRun=None):
        # get selection
        sel = mc.ls(sl=1)

        if len(sel) < 1:
           mc.warning('Nothing selected')
           return

        # asset name
        assetName = mc.textFieldGrp(windowName + '_assetName', q=1, text=1)

        # start and end range
        start = mc.intFieldGrp(windowName + '_range_startEnd', q=1, value1=1)
        end = mc.intFieldGrp(windowName + '_range_startEnd', q=1, value2=1)

        # check if using current frame
        range = mc.radioButtonGrp(windowName + '_range_radio', q=1, select=1)

        if range == 1:
            currentFrame = mc.currentTime(q=1)
            start = currentFrame
            end = currentFrame

        # publish directory
        exportDir = getExportDir()

        # type
        type = mc.optionMenuGrp(windowName + '_type', q=1, value=1).lower()

        exportPath = os.path.join(exportDir, assetName, type)

        # increment version if set to autoversion
        if mc.radioButtonGrp(windowName + '_version_radio', q=1, select=1) == 1:
            versionNum = getLatestVersion(exportPath) + 1
            version = ('v' + str(versionNum).zfill(3))
        else:
            version = mc.textFieldGrp(windowName + '_selVersion', q=1, text=1)

        exportPath = os.path.join(exportPath, version)

        if dryRun:
            print 'Asset alembic export path is ' + exportPath
            exportAssetJsonFile(exportPath, assetName, version, dryRun)
            return

        root = ''

        for obj in sel:
            root += ' -root ' + obj

        if not os.path.exists(exportPath):
            os.makedirs(exportPath)

        # export asset json file
        self.exportAssetJsonFile(exportPath, assetName, version, dryRun)


        # add asset name with format
        exportPath = os.path.join(exportPath, assetName + '.abc')

        command = "-frameRange " + str(start) + " " + str(end) + " -uvWrite -worldSpace" + root + " -file " + exportPath

        mc.AbcExport ( jobArg = command )

        if os.path.exists(exportPath):
            mc.confirmDialog(title='Export Successfull', message='Asset Exported Successfully', button='Ok')

        # for some reason the alembic command is exporting a folder named 'alembic'
        # this will remove it as long as its empty
        os.rmdir(os.path.join(exportDir, 'alembic'))

        # create set
        tbaSet = 'TBA_asset_' + assetName
        if mc.objExists(tbaSet):
            mc.delete(tbaSet)

        mc.sets( sel, name=tbaSet )

        # add assetVersion attribute
        mc.addAttr( tbaSet , shortName='assetVersion', dataType='string')
        # update attrs on meta node (and lock them)
        mc.setAttr( tbaSet +'.assetVersion', version, type='string')

        self.updateVersionsList()

        print 'Exported alembic to: ' + exportPath

    def setAssetOutlineColour(self):
        sel = mc.ls(sl=1)

        colour = [0.4, 0.7, 1]

        for obj in sel:
            mc.setAttr(obj + '.outlinerColor', colour[0], colour[1], colour[2] )
            mc.setAttr(obj + '.useOutlinerColor', 1)

    def exportAsset(self, *args):
        exportDir = self.getExportDir()

        # bail if scene not valid
        if not exportDir:
            return

        format = mc.optionMenuGrp(windowName + '_format', q=1, value=1)

        dryRun = mc.checkBox(windowName + '_dryRun', q=1, value=1)

        if dryRun:
            print 'Doing dry run'

        if format == 'abc':
            exportAbc(dryRun)
        else:
            print 'format not currently supported'
            return

        # set the colour of the select objects in the outliner to signify a TBA asset
        self.setAssetOutlineColour()

        #mc.deleteUI(windowName)

        #updateVersionsList()
        #updateAssetList()

    def updateVersion(self):
        exportDir = self.getExportDir()

        # bail if scene not valid
        if not exportDir:
            return

        type = mc.optionMenuGrp(windowName + '_type', q=1, select = 1)

        # get versions of that type

    def onAssetSelected(self, *args):
        asset = mc.textScrollList(windowName + '_assets', q=1, selectItem=1)

        print asset

        if asset:
            # set name to be selected asset
            mc.textFieldGrp(windowName + '_assetName', e=1, text=asset[0])
            print str(asset[0]) + ' selected'
        else:
            print 'No asset selected'
            mc.textScrollList(windowName + '_versions', e=1, removeAll=1)
            return

        TBA_set = 'TBA_asset_' + asset[0]

        if mc.objExists(TBA_set):
            nodes = mc.sets(TBA_set, q=1)

            if nodes:
                mc.select(nodes, replace=1)

        updateVersionsList()

    def onAssetNameChange(self, assetName):
        # enable button if there is text
        mc.button(windowName + '_exportButton', e=1, enable=(len(assetName) > 0))

        updateVersionsList()

    def onTypeChange(self, *args):
        # get selected type
        range = mc.radioButtonGrp(windowName + '_range_radio', q=1, select = 1)

        # enable if range is third option (start/end)
        mc.intFieldGrp(windowName + '_startEnd', e=1, enable=(range==3))
        mc.floatFieldGrp(windowName + '_range_step', e=1, enable=(range==3))

        updateVersion()

    def onRangeChange(self, *args):
        # get selected radio button
        range = mc.radioButtonGrp(windowName + '_range_radio', q=1, select = 1)

        # enable if range is third option (start/end)
        mc.intFieldGrp(windowName + '_range_startEnd', e=1, enable=(range==3))
        mc.floatFieldGrp(windowName + '_range_step', e=1, enable=(range==3))

        updateVersion()

    def onVersionTypeChange(self, *args):
        mode = mc.radioButtonGrp(windowName + '_version_radio', q=1, select=1)

        mc.textScrollList(windowName + '_versions', e=1, enable=(mode==2))

        updateVersionsList()

    def onVersionSelected(self, *args):
        selVersion = mc.textScrollList(windowName + '_versions', q=1, selectItem=1)

        versionNum = int(filter(str.isdigit, str(selVersion[0])))

        version = 'v' + str(versionNum).zfill(3)

        mc.textFieldGrp(windowName + '_selVersion', e=1, text=version)

    def onVersionSelected(self, *args):
        selVersion = mc.textScrollList(windowName + '_versions', q=1, selectItem=1)

        versionNum = int(filter(str.isdigit, str(selVersion[0])))

        version = 'v' + str(versionNum).zfill(3)

        mc.textFieldGrp(windowName + '_selVersion', e=1, text=version)

    def getExportDir(self):
        # current scene
        scene = mc.workspace(q=1,fullName=1)

        publishing = mc.checkBox(windowName + '_publish', q=1, v=1)

        # publish3d/assets folder - should be directly above the maya folder, if not create it
        if publishing:
            exportDir = os.path.join(os.path.dirname(scene), '_published3d', 'assets')
        else:
            exportDir = os.path.join(scene, 'exports')

        if not os.path.exists(exportDir):
            if publishing:
                print('Could not find a _published3d scene above the maya folder: {0}'.format(exportDir))
            else:
                print('Could not find an exports folder in the maya project folder: {0}'.format(exportDir))
            return False
        else:
            return exportDir

    def initType(self):
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

    def initUI(self):
        self.initType()

    def main(self):
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
        window = mc.window(windowName, title="TBA Asset Exporter", iconName=windowName, widthHeight=(windowWidth, windowHeight) )

        mc.frameLayout( labelVisible=0, marginWidth=5, marginHeight=5 )
        mc.columnLayout()

        # new asset name
        mc.rowLayout(numberOfColumns=2)

        mc.textFieldGrp( windowName + '_assetName',
                         label = 'Asset Name:',
                         columnWidth2=[colWidth1, colWidth2],
                         columnAlign=[1,'left'],
                         textChangedCommand=onAssetNameChange)

        # refresh button
        mc.button( windowName + '_refresh', label='Refresh', command=refresh)

        mc.setParent('..')

        # current assets list
        mc.text( label='Existing Assets:' )
        mc.textScrollList( windowName + '_assets',
                           numberOfRows=4,
                           selectCommand=onAssetSelected )

        # auto version up or overwrite old version
        mc.radioButtonGrp( windowName + '_version_radio',
                             labelArray2=['Auto Version', 'Overwrite'],
                             numberOfRadioButtons=2,
                             columnWidth2=[windowWidth/2, windowWidth/2],
                             columnAlign=[1,'left'],
                             changeCommand=onVersionTypeChange,
                             select=1 )

        # selected asset versions
        mc.text( label='Asset Versions:' )
        mc.textScrollList( windowName + '_versions',
                           numberOfRows=4,
                           selectCommand=onVersionSelected,
                           enable=0 )

        # selected version
        mc.textFieldGrp( windowName + '_selVersion',
                         label = 'Write Version:',
                         text = 'v001',
                         columnWidth2=[colWidth1, colWidth2],
                         columnAlign=[1,'left'],
                         enable=0)

        # asset type
        mc.optionMenuGrp( windowName + '_type',
                                        label='Type:',
                                        columnWidth2=[colWidth1, colWidth2],
                                        columnAlign=[1,'left'],
                                        changeCommand="updateVersion()")

        for type in types:
            mc.menuItem( label = type )

        # formats
        mc.optionMenuGrp( windowName + '_format',
                                        label='Format:',
                                        columnWidth2=[colWidth1, colWidth2],
                                        columnAlign=[1,'left'],
                                        changeCommand="updateVersion()")
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
                             changeCommand=onRangeChange,
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
        mc.button( windowName + '_exportButton', label='Export', command=exportAsset, width=windowWidth, enable=0 )

        # checkbox for dryRun (for dev purposes)
        mc.checkBox( windowName + '_dryRun', label='Dry Run', value=0 )

        # publish
        mc.checkBox( windowName + '_publish', label='Publish', value=0 )

        mc.window(window, e=1, width=windowWidth, height=windowHeight)

        exportDir = self.getExportDir()

        # bail if scene not valid
        if not exportDir:
            return

        self.initUI()
        self.updateAssetList()

        mc.showWindow( window )

