import maya.cmds as mc

def get_maya_asset_sets():
    return mc.ls('tba_asset*', type='objectSet')

def export_selected():
    print('TBA :: export_selected')

    # get selection
    sel = mc.ls(sl=1)

    if len(sel) < 1:
        mc.warning('Nothing selected')
        return

    print('Export selection: ')
    print(sel)
