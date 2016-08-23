# coding=utf-8
#
# Author: Fredrik Averpil, fredrik.averpil@gmail.com, http://fredrikaverpil.tumblr.com
# 

''' Imports regardless of Qt type '''
''' --------------------------------------------------------------------------------------------------------------------------------------------------------- '''
import os
import xml.etree.ElementTree as xml
from cStringIO import StringIO

dennistd_mayapy_path = r'V:\\temp\dennistd\maya_python'
lighting_tool_path = r'V:\tools\lighting\lighting_tool\lightingTool'

import sys

if dennistd_mayapy_path not in sys.path:
    sys.path.append(dennistd_mayapy_path)

if lighting_tool_path not in sys.path:
    sys.path.append(lighting_tool_path)

import pymel.core as pm

''' CONFIGURATION '''
''' --------------------------------------------------------------------------------------------------------------------------------------------------------- '''

# Check Maya version
# If Maya version >= 2014 use PySide
# If Maya version < 2014 use PyQt if installed

mayaVersion = str(pm.versions.current())[0:4]

if int(mayaVersion) >= 2014:
    QtType = 'PySide'
else:
    QtType = 'PyQt'

# General
# QtType = 'PyQt'  # Edit this to switch between PySide and PyQt
sys.dont_write_bytecode = True  # Do not generate .pyc files
uiFile = os.path.join(os.path.dirname(__file__), 'snap_tool3.ui')  # The .ui file to load

windowTitle = 'Snap Animation Tool'  # The visible title of the window
windowObject = 'snapToolUI'  # The name of the window object
dockObject = "snapToolDock"

# Standalone settings
darkorange = False  # Use the 'darkorange' stylesheet

# Maya settings
launchAsDockedWindow = False  # False = opens as free floating window, True = docks window to Maya UI

# Nuke settings
launchAsPanel = False  # False = opens as regular window, True = opens as panel

# Site-packages location:
site_packages_Win = ''  # Location of site-packages containing PySide and pysideuic and/or PyQt and SIP
site_packages_Linux = ''  # Location of site-packages containing PySide and pysideuic and/or PyQt and SIP
site_packages_OSX = ''  # Location of site-packages containing PySide and pysideuic and/or PyQt and SIP
# site_packages_Win = 'C:/Python26/Lib/site-packages'						# Example: Windows 7
#site_packages_Linux = '/usr/lib/python2.6/site-packages'					# Example: Linux CentOS 6.4
#site_packages_OSX = '/Library/Python/2.7/site-packages'					# Example: Mac OS X 10.8 Mountain Lion

''' Run mode '''
''' --------------------------------------------------------------------------------------------------------------------------------------------------------- '''

runMode = 'maya'

try:
    import maya.cmds as cmds
    import maya.OpenMayaUI as omui
    import shiboken

    runMode = 'maya'

except StandardError:
    pass

''' PySide or PyQt '''
''' --------------------------------------------------------------------------------------------------------------------------------------------------------- '''
if (site_packages_Win != '') and ('win' in sys.platform): sys.path.append(site_packages_Win)
if (site_packages_Linux != '') and ('linux' in sys.platform): sys.path.append(site_packages_Linux)
if (site_packages_OSX != '') and ('darwin' in sys.platform): sys.path.append(site_packages_OSX)

if QtType == 'PySide':
    from PySide import QtCore, QtGui
    import pysideuic
elif QtType == 'PyQt':
    from PyQt4 import QtCore, QtGui, uic
    import sip
print 'This app is now using ' + QtType

''' Auto-setup classes and functions '''
''' --------------------------------------------------------------------------------------------------------------------------------------------------------- '''


class PyQtFixer(QtGui.QMainWindow):
    def __init__(self, parent=None):
        """Super, loadUi, signal connections"""
        super(PyQtFixer, self).__init__(parent)
        print 'Making a detour (hack), necessary for when using PyQt'


def loadUiType(uiFile):
    """
    Pyside lacks the "loadUiType" command, so we have to convert the ui file to py code in-memory first
    and then execute it in a special frame to retrieve the form_class.
    """
    parsed = xml.parse(uiFile)
    widget_class = parsed.find('widget').get('class')
    form_class = parsed.find('class').text

    with open(uiFile, 'r') as f:
        o = StringIO()
        frame = {}

        if QtType == 'PySide':
            pysideuic.compileUi(f, o, indent=0)
            pyc = compile(o.getvalue(), '<string>', 'exec')
            exec pyc in frame

            #Fetch the base_class and form class based on their type in the xml from designer
            form_class = frame['Ui_%s' % form_class]
            base_class = eval('QtGui.%s' % widget_class)

        elif QtType == 'PyQt':
            form_class = PyQtFixer
            base_class = QtGui.QMainWindow
    return form_class, base_class

form, base = loadUiType(uiFile)


def wrapinstance(ptr, base=None):
    """
    Utility to convert a pointer to a Qt class instance (PySide/PyQt compatible)

    :param ptr: Pointer to QObject in memory
    :type ptr: long or Swig instance
    :param base: (Optional) Base class to wrap with (Defaults to QObject, which should handle anything)
    :type base: QtGui.QWidget
    :return: QWidget or subclass instance
    :rtype: QtGui.QWidget
    """
    if ptr is None:
        return None
    ptr = long(ptr)  #Ensure type

    if globals().has_key('shiboken'):
        if base is None:
            qObj = shiboken.wrapInstance(long(ptr), QtCore.QObject)
            metaObj = qObj.metaObject()
            cls = metaObj.className()
            superCls = metaObj.superClass().className()
            if hasattr(QtGui, cls):
                base = getattr(QtGui, cls)
            elif hasattr(QtGui, superCls):
                base = getattr(QtGui, superCls)
            else:
                base = QtGui.QWidget
        return shiboken.wrapInstance(long(ptr), base)

    elif globals().has_key('sip'):
        base = QtCore.QObject
        return sip.wrapinstance(long(ptr), base)
    else:
        return None


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapinstance(long(main_window_ptr), QtGui.QWidget)  # Works with both PyQt and PySide


''' Main class '''
''' --------------------------------------------------------------------------------------------------------------------------------------------------------- '''


class SnapToolUI(form, base):
    def __init__(self, parent=None):
        """Super, loadUi, signal connections"""
        super(SnapToolUI, self).__init__(parent)

        if QtType == 'PySide':
            print 'Loading UI using PySide'
            self.setupUi(self)

        elif QtType == 'PyQt':
            print 'Loading UI using PyQt'
            uic.loadUi(uiFile, self)

        self.setObjectName(windowObject)
        self.setWindowTitle(windowTitle)

        load_dlSnapToMeshNOde_plugin()

        self.nodes_manager = SnapToMeshNodeManager(self.nodeList)

        self.weightSet.setMaxLength(4)
        self.weightAdjust.setMaxLength(4)
        self.offsetWeightAdjust.setMaxLength(4)
        self.Xedit.setMaxLength(4)
        self.Yedit.setMaxLength(4)
        self.Zedit.setMaxLength(4)

        #self.weightSet.setInputMask('H')
        #self.weightAdjust.setInputMask('H')

        # signal slot

        # Ground Obj List
        self.addGround.clicked.connect(self.add_ground_obj)
        self.groundObjList.itemClicked.connect(self.select_ground_obj)
        self.weightGenSlider.valueChanged.connect(self.weight_gen_slider_changed)

        # control list
        self.addControl.clicked.connect(self.add_target_transform)
        self.controlList.itemClicked.connect(self.select_target_transform)

        # generate Node and connect
        self.generateNode.clicked.connect(self.batch_connect)

        # Node List signal slot
        self.refreshNodeList.clicked.connect(self.nodes_manager.refresh_node_view)

        self.weightAdjust.editingFinished.connect(self.weight_adj_edit_changed)
        self.weightSlider.valueChanged.connect(self.weight_adj_slider_changed)

        self.offsetWeightAdjust.editingFinished.connect(self.offset_weight_adj_edit_changed)
        self.offsetWeightSlider.valueChanged.connect(self.offset_weight_adj_slider_changed)

        self.Xedit.editingFinished.connect(self.offset_x)
        self.Yedit.editingFinished.connect(self.offset_y)
        self.Zedit.editingFinished.connect(self.offset_z)

        self.nodeList.itemClicked.connect(self.show_node_attributes)

    def batch_connect(self):

        # connect grd obj
        if self.groundObjList.item(0) is None:
            return None
        else:
            grd_mesh = pm.PyNode(self.groundObjList.item(0).text())

        if pm.objectType(grd_mesh) == "mesh":
            pass
        else:
            return None

        ctrl_list = []

        if self.controlList.item(0) is None:
            return None
        else:

            for count in range(self.controlList.count()):
                ctrl_list.append(self.controlList.item(count))

            ctrl_list = [item.text() for item in ctrl_list if item is not None]

        for item in ctrl_list:
            self.connect_attrs(grd_mesh, item)

    def connect_attrs(self, grd_mesh=None, control=None):

        if grd_mesh is None or control is None:
            return None

        pos_ctrl = None

        # create decompose for translate and parent pos
        decompose_trans = pm.createNode('decomposeMatrix')
        decompose_par = pm.createNode('decomposeMatrix')

        # if want to use seperate position node, create another decomposeMatrix
        """
        if self.inPosCheck.checkState():
            pos_ctrl = pm.PyNode(self.intPositionList.item(0).text())
            decompose_pos = pm.createNode('decomposeMatrix')
            pos_ctrl.worldMatrix[0] >> decompose_pos.inputMatrix
        """

        # select and plug in translate to decomposeMatrix
        in_translate = pm.PyNode(control)
        target = in_translate

        # get original's translate attribute
        ori_x = in_translate.translateX.get()
        ori_y = in_translate.translateY.get()
        ori_z = in_translate.translateZ.get()

        # get in_translate's parent's group
        parent = None
        in_translate_proxy = None

        relative_list = pm.listRelatives(in_translate, p=True, type='transform')

        if len(relative_list) > 0:
            parent = relative_list[0]

        # can't get rid of proxy until decompose matrix is built-in
        use_proxy = True

        # create in_translate proxy and parent it to in_translate's parent so they are sibling
        if use_proxy:
            in_translate_proxy = pm.createNode('transform', name="%s_Proxy" % in_translate)
            in_translate_proxy = pm.PyNode(in_translate_proxy)
            in_translate_proxy.translateX.set(ori_x)
            in_translate_proxy.translateY.set(ori_y)
            in_translate_proxy.translateZ.set(ori_z)

        if parent is None or use_proxy is False:
            pass
        else:
            try:
                pm.parent(in_translate_proxy, parent)
            except StandardError:
                print "fail to parent %s to %s".format(in_translate_proxy, parent)

        # connect proxy's matrix to decompose
        if in_translate_proxy is None:
            pm.PyNode(parent).worldMatrix[0] >> decompose_par.inputMatrix
        else:
            in_translate_proxy.worldMatrix[0] >> decompose_trans.inputMatrix

            # connect parentMatrix to decompose
            in_translate_proxy.parentMatrix[0] >> decompose_par.inputMatrix

        # find in_translate's keyframe source, reconnect them to proxy

        if len(pm.listConnections(in_translate, p=1, type='animCurveTL')) > 0:
            for connection in pm.listConnections(in_translate, p=1, type='animCurveTL'):
                if '_translateX' in connection.name():
                    connection >> in_translate_proxy.translateX
                    connection // in_translate.translateX
                if '_translateY' in connection.name():
                    connection >> in_translate_proxy.translateY
                    connection // in_translate.translateY
                if '_translateZ' in connection.name():
                    connection >> in_translate_proxy.translateZ
                    connection // in_translate.translateZ

            in_translate_proxy.translate >> in_translate.translate

        if pos_ctrl is None:
            pos_ctrl = in_translate
            decompose_pos = decompose_trans

        # load and check plugin, create compute node
        load_dlSnapToMeshNOde_plugin()
        compute_node = pm.createNode('dlSnapToMeshNode')

        # preserve original keyframe
        in_translate_proxy.translate >> compute_node.inLocalTranslate

        # connect mesh.worldMesh[0]
        grd_mesh.worldMesh[0] >> compute_node.inputMesh

        # connect decompose for pos to compute node
        decompose_pos.outputTranslate >> compute_node.inWorldPosition

        # connect decompose for translate to compute node
        decompose_trans.outputTranslate >> compute_node.inWorldTranslate

        # connect decompose for parent pos
        decompose_par.outputTranslate >> compute_node.inParentPos

        # connect out translate to target
        compute_node.outTranslate >> target.translate

    def select_ground_obj(self):

        node = pm.PyNode(self.groundObjList.currentItem().text())
        pm.select(node)

    def add_ground_obj(self):

        # only one object
        sel_obj = pm.ls(selection=True)[0]

        if pm.objectType(sel_obj) == "mesh":
            pass
        else:
            return None

        self.groundObjList.clear()

        ground_item = QtGui.QListWidgetItem(sel_obj.name())
        self.groundObjList.addItem(ground_item)

    def select_target_transform(self):

        node = pm.PyNode(self.controlList.currentItem().text())
        pm.select(node)

    def add_target_transform(self):

        targets = pm.ls(selection=True)

        self.controlList.clear()

        for target in targets:
            target_item = QtGui.QListWidgetItem(target.name())
            self.controlList.addItem(target_item)

    def weight_gen_slider_changed(self):

        val = float(self.weightGenSlider.value())
        val = self.normalize_val(val)

        self.weightSet.setText(str(val))

    def show_node_attributes(self):

        this_node = pm.PyNode(str(self.nodeList.currentItem().text()))
        nodes = self.nodeList.selectedItems()
        nodes = [pm.PyNode(str(node.text())) for node in nodes]

        # select node
        pm.select(nodes)

        weight = this_node.weight.get()
        offset_weight = this_node.offset_weight.get()

        self.weightAdjust.setText(str(weight))
        self.offsetWeightAdjust.setText(str(offset_weight))

        offsetX = this_node.offsetX.get()
        offsetY = this_node.offsetY.get()
        offsetZ = this_node.offsetZ.get()

        self.Xedit.setText(str(offsetX))
        self.Yedit.setText(str(offsetY))
        self.Zedit.setText(str(offsetZ))

    def weight_adj_edit_changed(self):
        val = float(self.weightAdjust.text())
        self.nodes_manager.change_weight(val)

    def weight_adj_slider_changed(self):

        val = float(self.weightSlider.value())
        val = self.normalize_val(val)

        self.weightAdjust.setText(str(val))
        self.nodes_manager.change_weight(val)

    def offset_weight_adj_slider_changed(self):

        val = float(self.offsetWeightSlider.value())
        val = self.normalize_val(val)

        self.offsetWeightAdjust.setText(str(val))
        self.nodes_manager.change_offset_weight(val)

    def offset_weight_adj_edit_changed(self):
        val = float(self.offsetWeightAdjust.text())
        self.nodes_manager.change_offset_weight(val)

    def offset_x(self):
        ctrl = self.Xedit
        self.offset_adj('X', ctrl)

    def offset_y(self):
        ctrl = self.Yedit
        self.offset_adj('Y', ctrl)

    def offset_z(self):
        ctrl = self.Zedit
        self.offset_adj('Z', ctrl)

    def offset_adj(self, axis, qt_ctrl):

        val = float(qt_ctrl.text())
        self.nodes_manager.change_offset(axis, val)

    @staticmethod
    def normalize_val(val):

        if val > 1.0:
            val /= 99
        elif val < 0.0:
            val = 0

        return val


class SnapToMeshNodeManager(object):

    def __init__(self, node_view):
        self.node_view = node_view
        self.refresh_node_view()

    def refresh_node_view(self):
        self.node_view.clear()
        self._fill_node_list()

    def _fill_node_list(self):
        node_list = self.get_node_list()

        for item in node_list:
            list_item = QtGui.QListWidgetItem(pm.PyNode(item).name())
            self.node_view.addItem(list_item)

    def get_current_item(self):
        return pm.PyNode(self.node_view.currentItem().text())

    def change_offset(self, axis, val):

        attr_name = 'offset' + axis.upper()
        node = self.get_current_item()
        pm.setAttr(node+'.'+attr_name, val)

    def change_weight(self, val=None):

        if val is None or self.node_view.currentItem() is None:
            return None

        node = self.get_current_item()

        if node is None:
            return None

        node.weight.set(val)

    def change_offset_weight(self, val=None):

        if val is None or self.node_view.currentItem() is None:
            return None

        node = self.get_current_item()

        if node is None:
            return None

        node.offset_weight.set(val)

    @staticmethod
    def get_node_list():

        return pm.ls(type="dlSnapToMeshNode")


''' Run functions '''
''' --------------------------------------------------------------------------------------------------------------------------------------------------------- '''


def source_ae_template():

    import maya.mel as mel
    import os

    ae_template_path = os.path.join(os.path.dirname(__file__), 'AEdlSnapToMeshNodeTemplate.mel')
    mel.eval(r'source "%s"' % ae_template_path.replace("\\", "/"))


def load_dlSnapToMeshNOde_plugin():

    plugin_path = os.path.join(os.path.dirname(__file__), 'dlSnapToMeshNode.py')
    pm.loadPlugin(plugin_path.replace("\\", "/"))

    source_ae_template()


def deleteDock(_ctrl=None):

    if _ctrl is None:
        try:
            cmds.deleteUI(dockObject, control=True)
        except StandardError:
            pass
    else:
        try:
            cmds.deleteUI(_ctrl, control=True)
        except StandardError:
            pass


def runMaya():

    global dock_ctrl
    global gui
    global launchAsDockedWindow

    if cmds.window(windowObject, q=True, exists=True):
        cmds.deleteUI(windowObject)

    if cmds.dockControl(dockObject, q=True, exists=True):
        deleteDock(dockObject)

    gui = SnapToolUI(maya_main_window())

    if int(mayaVersion) >= 2014:
        launchAsDockedWindow = True

    if launchAsDockedWindow:
        allowedAreas = ['right', 'left']

        if cmds.window(windowObject, q=True, exists=True):
            dock_ctrl = cmds.dockControl(dockObject, label=windowTitle, area='right',
                                         content=windowObject, allowedArea=allowedAreas)
        else:
            gui.show()
    else:
        gui.show()


if runMode == 'maya':
    runMaya()