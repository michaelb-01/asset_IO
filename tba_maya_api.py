import maya.cmds as mc

def export_selected():
    print('TBA :: export_selected')

    # get selection
    sel = mc.ls(sl=1)

    if len(sel) < 1:
        mc.warning('Nothing selected')
        return

    print('Export selection: ')
    print(sel)
