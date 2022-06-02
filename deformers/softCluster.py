from maya import cmds
from maya import mel
from maya import OpenMaya
from functools import reduce

def softCluster():
    selectionVrts = cmds.ls(selection = True, flatten = True)
    if selectionVrts:
        posVtx = _getAverage(selectionVrts)
        cmds.softSelect(sse=True)
        softElementData = _softSelection()
        selection = ["%s.vtx[%d]" % (el[0], el[1])for el in softElementData ] 
        model = selectionVrts[0].split('.')[0]
        cmds.select(model, r=True)
        cluster = cmds.cluster(name = '%s_cls' % model, relative=False, bindState = True)
        clusterGrp = cmds.createNode('transform', name = '%s_grp' % cluster[1])
        cmds.xform(cluster, rotatePivot = posVtx, scalePivot = posVtx, objectSpace = True)
        cmds.xform(clusterGrp, rotatePivot = posVtx, scalePivot = posVtx, objectSpace = True)
        cmds.parent(cluster[1], clusterGrp)
        cmds.connectAttr('%s.worldInverseMatrix' % clusterGrp, '%s.bindPreMatrix' % cluster[0])
        weight = [0.0]
        zero = 0.0
        VertexNb = cmds.polyEvaluate(model, v=1) - 1
        for x in range(VertexNb):
            weight.append(zero)
        cmds.setAttr('{0}.weightList[0].weights[0:{1}]'.format(cluster[0], VertexNb), *weight, size=len(weight))
        shape = cmds.listRelatives(cluster[1], shapes = True)[0]
        cmds.setAttr('%s.originX' % shape, posVtx[0])
        cmds.setAttr('%s.originY' % shape, posVtx[1])
        cmds.setAttr('%s.originZ' % shape, posVtx[2])
        for i in range(len(softElementData)):
            cmds.percent(cluster[0], selection[i], v=softElementData[i][2])
        cmds.select(cluster[1], r=True)

def _softSelection():
    selection = OpenMaya.MSelectionList()
    softSelection = OpenMaya.MRichSelection()
    OpenMaya.MGlobal.getRichSelection(softSelection)
    softSelection.getSelection(selection)
    dagPath = OpenMaya.MDagPath()
    component = OpenMaya.MObject()
    iter = OpenMaya.MItSelectionList( selection,OpenMaya.MFn.kMeshVertComponent )
    elements = []
    while not iter.isDone(): 
        iter.getDagPath( dagPath, component )
        dagPath.pop()
        node = dagPath.fullPathName()
        fnComp = OpenMaya.MFnSingleIndexedComponent(component)
        for i in range(fnComp.elementCount()):
            elements.append([node, fnComp.element(i), fnComp.weight(i).influence()] )
        iter.next()
    return elements

def _getAverage(selection):
    average = []
    listX = []
    listY = []
    listZ = []
    for item in selection:
        pos = cmds.xform(item, query = True, translation = True, worldSpace = True)
        listX.append(pos[0])
        listY.append(pos[1])
        listZ.append(pos[2])
    aveX = reduce(lambda x, y: x + y, listX) / len(listX)
    aveY = reduce(lambda x, y: x + y, listY) / len(listY)
    aveZ = reduce(lambda x, y: x + y, listZ) / len(listZ)
    average.append(aveX)
    average.append(aveY)
    average.append(aveZ)
    return average
    
softCluster()