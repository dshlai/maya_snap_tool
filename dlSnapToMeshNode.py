__author__ = 'Dennis SH Lai'

import maya.OpenMaya as om
import maya.OpenMayaMPx as omMPx
import pymel.core as pm

# Name the node, and give it an ID. We might want to define a range for our internal plugin

nodeName = "dlSnapToMeshNode"
nodeTypeID = om.MTypeId(0x70000)

# Define how maya create this node


def create():
    return omMPx.asMPxPtr(dlSnapToMeshNode())


def init():

    ### Input Plug and Attr Setup

    # use MFnUnit to get DoubleLinear that matches maya's transform node
    unit_type = om.MFnUnitAttribute.kDistance

    # set mesh input for worldMesh input of Ground Obj
    mesh_typed_attr = om.MFnTypedAttribute()
    dlSnapToMeshNode.INPUT_MESH = mesh_typed_attr.create("inputMesh", "in_mesh", om.MFnData.kMesh)
    mesh_typed_attr.setStorable(True)
    mesh_typed_attr.setReadable(False)

    # input transformation matrix
    double_type = om.MFnNumericData.kDouble
    matrix_attr = om.MFnMatrixAttribute()
    in_matrix = matrix_attr.create('inputMatrix', 'in_matrix', double_type)
    dlSnapToMeshNode.INPUT_MATRIX = in_matrix
    matrix_attr.setStorable(True)

    # input parent transformation matrix
    double_type = om.MFnNumericData.kDouble
    matrix_attr = om.MFnMatrixAttribute()
    in_matrix = matrix_attr.create('inputParentMatrix', 'in_par_matrix', double_type)
    dlSnapToMeshNode.INPUT_PARENT_MATRIX = in_matrix
    matrix_attr.setStorable(True)

    # input pos for calculating the closestPointOnMesh
    num_attr = om.MFnUnitAttribute()
    x_pos = num_attr.create('inWorldPositionX', 'in_wpX', unit_type)
    y_pos = num_attr.create('inWorldPositionY', 'in_wpY', unit_type)
    z_pos = num_attr.create('inWorldPositionZ', 'in_wpZ', unit_type)

    transform_attr = om.MFnNumericAttribute()
    this_data = transform_attr.create("inWorldPosition", "in_wpos", x_pos, y_pos, z_pos)
    dlSnapToMeshNode.INPUT_POS = this_data
    transform_attr.setStorable(True)

    # input the original key frames of the control
    num_attr = om.MFnUnitAttribute()
    x_trans = num_attr.create('inWorldTranslateX', 'in_wtX', unit_type)
    y_trans = num_attr.create('inWorldTranslateY', 'in_wtY', unit_type)
    z_trans = num_attr.create('inWorldTranslateZ', 'in_wtZ', unit_type)

    transform_attr = om.MFnNumericAttribute()
    this_data = transform_attr.create("inWorldTranslate", "in_wtrans", x_trans, y_trans, z_trans)
    dlSnapToMeshNode.INPUT_TRSL = this_data
    transform_attr.setStorable(True)

    # input the original key frames of the control
    num_attr = om.MFnUnitAttribute()
    x_ppos = num_attr.create('inParentPosX', 'in_ppX', unit_type)
    y_ppos = num_attr.create('inParentPosY', 'in_ppY', unit_type)
    z_ppos = num_attr.create('inParentPosZ', 'in_ppZ', unit_type)

    transform_attr = om.MFnNumericAttribute()
    this_data = transform_attr.create("inParentPos", "in_ppos", x_ppos, y_ppos, z_ppos)
    dlSnapToMeshNode.INPUT_PPOS = this_data
    transform_attr.setStorable(True)

    # input the original key frames of the control
    num_attr = om.MFnUnitAttribute()
    x_ppos = num_attr.create('inLocalTranslateX', 'in_lX', unit_type)
    y_ppos = num_attr.create('inLocalTranslateY', 'in_lY', unit_type)
    z_ppos = num_attr.create('inLocalTranslateZ', 'in_lZ', unit_type)

    transform_attr = om.MFnNumericAttribute()
    this_data = transform_attr.create("inLocalTranslate", "in_lt", x_ppos, y_ppos, z_ppos)
    dlSnapToMeshNode.INPUT_LTRSL = this_data
    transform_attr.setStorable(True)

    # weight attribute
    num_attr = om.MFnNumericAttribute()
    float_type = om.MFnNumericData.kFloat
    dlSnapToMeshNode.WEIGHT = num_attr.create("weight", "wi", float_type, 1.0)
    num_attr.setMax(1.5)
    num_attr.setMin(0.0)
    num_attr.setSoftMax(1.0)
    num_attr.setStorable(True)
    num_attr.setKeyable(True)

    # offset attribute
    num_attr = om.MFnNumericAttribute()
    dlSnapToMeshNode.OFFSET = num_attr.createPoint("offset", "ofs")
    num_attr.setStorable(True)
    num_attr.setKeyable(True)

    # offset weight attribute
    num_attr = om.MFnNumericAttribute()
    float_type = om.MFnNumericData.kFloat
    dlSnapToMeshNode.OFFSET_WEIGHT = num_attr.create("offset_weight", "ofs_wi", float_type, 1.0)
    num_attr.setMax(1.0)
    num_attr.setMin(0.0)
    num_attr.setSoftMax(1.0)
    num_attr.setStorable(True)
    num_attr.setKeyable(True)

    # output attributes
    num_attr = om.MFnUnitAttribute()
    x_ot = num_attr.create('outTranslateX', 'out_tX', unit_type)
    y_ot = num_attr.create('outTranslateY', 'out_tY', unit_type)
    z_ot = num_attr.create('outTranslateZ', 'out_tZ', unit_type)

    transform_attr = om.MFnNumericAttribute()
    this_data = transform_attr.create("outTranslate", "out_trans", x_ot, y_ot, z_ot)
    dlSnapToMeshNode.OUT_TRSL = this_data
    transform_attr.setStorable(False)
    transform_attr.setKeyable(False)

    ### Add Attributes To Node

    # mesh input
    dlSnapToMeshNode.addAttribute(dlSnapToMeshNode.INPUT_MESH)

    # matrix input
    #dlSnapToMeshNode.addAttribute(dlSnapToMeshNode.INPUT_MATRIX)
    #dlSnapToMeshNode.addAttribute(dlSnapToMeshNode.INPUT_PARENT_MATRIX)

    # double linear input
    dlSnapToMeshNode.addAttribute(dlSnapToMeshNode.INPUT_POS)
    dlSnapToMeshNode.addAttribute(dlSnapToMeshNode.INPUT_TRSL)
    dlSnapToMeshNode.addAttribute(dlSnapToMeshNode.INPUT_PPOS)
    dlSnapToMeshNode.addAttribute(dlSnapToMeshNode.INPUT_LTRSL)

    # user weight input
    dlSnapToMeshNode.addAttribute(dlSnapToMeshNode.WEIGHT)  # Float attr as weight
    dlSnapToMeshNode.addAttribute(dlSnapToMeshNode.OFFSET)
    dlSnapToMeshNode.addAttribute(dlSnapToMeshNode.OFFSET_WEIGHT)

    # output double linear
    dlSnapToMeshNode.addAttribute(dlSnapToMeshNode.OUT_TRSL)

    # Set update affects
    dlSnapToMeshNode.attributeAffects(dlSnapToMeshNode.INPUT_MESH, dlSnapToMeshNode.OUT_TRSL)
    dlSnapToMeshNode.attributeAffects(dlSnapToMeshNode.INPUT_POS, dlSnapToMeshNode.OUT_TRSL)
    dlSnapToMeshNode.attributeAffects(dlSnapToMeshNode.INPUT_TRSL, dlSnapToMeshNode.OUT_TRSL)
    dlSnapToMeshNode.attributeAffects(dlSnapToMeshNode.INPUT_PPOS, dlSnapToMeshNode.OUT_TRSL)
    dlSnapToMeshNode.attributeAffects(dlSnapToMeshNode.INPUT_LTRSL, dlSnapToMeshNode.OUT_TRSL)

    #dlSnapToMeshNode.attributeAffects(dlSnapToMeshNode.INPUT_MATRIX, dlSnapToMeshNode.OUT_TRSL)
    #dlSnapToMeshNode.attributeAffects(dlSnapToMeshNode.INPUT_PARENT_MATRIX, dlSnapToMeshNode.OUT_TRSL)

    dlSnapToMeshNode.attributeAffects(dlSnapToMeshNode.WEIGHT, dlSnapToMeshNode.OUT_TRSL)
    dlSnapToMeshNode.attributeAffects(dlSnapToMeshNode.OFFSET, dlSnapToMeshNode.OUT_TRSL)
    dlSnapToMeshNode.attributeAffects(dlSnapToMeshNode.OFFSET_WEIGHT, dlSnapToMeshNode.OUT_TRSL)


def _toplugin(mobject):
    return omMPx.MFnPlugin(
        mobject, 'Dennis SH Lai', '0.0.5', 'Any')


def initializePlugin(mobject):
    plugin = _toplugin(mobject)
    plugin.registerNode(nodeName, nodeTypeID, create, init)


def uninitializePlugin(mobject):
    plugin = _toplugin(mobject)
    plugin.deregisterNode(nodeTypeID)


class dlSnapToMeshNode(omMPx.MPxNode):

    INPUT_MATRIX = om.MObject()
    INPUT_PARENT_MATRIX = om.MObject()

    INPUT_MESH = om.MObject()
    INPUT_POS = om.MObject()
    INPUT_TRSL = om.MObject()
    INPUT_PPOS = om.MObject()
    INPUT_LTRSL = om.MObject()
    WEIGHT = om.MObject()
    OFFSET = om.MObject()
    OFFSET_WEIGHT = om.MObject()

    OUT_TRSL = om.MObject()
    OUT_FACE = om.MObject()
    OUT_VERT = om.MObject()

    def __init__(self):
        omMPx.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):

        VERBOSE = False

        if plug == self.OUT_TRSL and self.INPUT_MESH:
            # setup input attributes
            mesh_fn = om.MFnMesh(dataBlock.inputValue(self.INPUT_MESH).asMesh())

            # setup matrix attributes
            #in_trans_matrix = dataBlock.inputValue(self.INPUT_MATRIX).asMatrix()
            #in_parent_t_matrix = dataBlock.inputValue(self.INPUT_PARENT_MATRIX).asMatrix()

            # double linear attributes
            in_pos_data = dataBlock.inputValue(self.INPUT_POS).asDouble3()
            in_ppos_data = dataBlock.inputValue(self.INPUT_PPOS).asDouble3()
            in_t_data = dataBlock.inputValue(self.INPUT_TRSL).asDouble3()
            in_lt_data = dataBlock.inputValue(self.INPUT_LTRSL).asDouble3()

            weight = dataBlock.inputValue(self.WEIGHT).asFloat()
            offset = dataBlock.inputValue(self.OFFSET).asFloat3()
            offset_w = dataBlock.inputValue(self.OFFSET_WEIGHT).asFloat()

            # set output value
            out_trsl = dataBlock.outputValue(self.OUT_TRSL)

            # setup decompose
            # translation is easy
            #in_translate_mat = om.MPoint(in_trans_matrix[3][0], in_trans_matrix[3][1], in_trans_matrix[3][2])
            #in_parent_t_mat = om.MPoint(in_parent_t_matrix[3][0], in_parent_t_matrix[3][1], in_parent_t_matrix[3][2])

            # setup MPoint
            in_pos_p = om.MPoint(in_pos_data[0], in_pos_data[1], in_pos_data[2])
            in_ppos_p = om.MPoint(in_ppos_data[0], in_ppos_data[1], in_ppos_data[2])
            in_t_p = om.MPoint(in_t_data[0], in_t_data[1], in_t_data[2])
            in_lt_p = om.MPoint(in_lt_data[0], in_lt_data[1], in_lt_data[2])

            #in_t_p = in_parent_t_mat
            #in_ppos_p = in_parent_t_mat

            offset_p = om.MPoint(offset[0], offset[1], offset[2])

            out_pos_p = om.MPoint()
            out_norm = om.MVector()

            # New API:    getClosestPointAndNormal()
            # Signature:  getClosestPointAndNormal(point, space=MSpace.kObject)
            # Parameters: point MPoint Point to be compared.
            #             space MSpace constant Coordinate space to use.
            # Returns:    (MPoint, MVector, int)
            # Old API: getClosestPointAndNormal(in_pos, out_pos, out_normal, om.MSpace.kWorld)

            mesh_fn.getClosestPointAndNormal(in_pos_p, out_pos_p, out_norm, om.MSpace.kWorld)

            if out_pos_p and out_norm:

                if VERBOSE:
                    pass
                    #print "Closest Point: (%10.3f, %10.3f, %10.3f)" % (out_pos_p.x, out_pos_p.y, out_pos_p.z)
                    #print "Closest Normal: [%10.3f, %10.3f, %10.3f]" % (out_norm[0], out_norm[1], out_norm[2])

                vector = in_pos_p - out_pos_p

                # normalize the vector to match return normal from getClosestPointAndNormal()
                vector_norm = vector.normal()
                # get dot product between normal and closest normal, if dot < 0 pos is under the surface
                dot = vector_norm * out_norm

                if VERBOSE:
                    dist = out_pos_p.distanceTo(in_pos_p)
                    dist_factored = dot * dist
                    print "Dot Product:%10.3f" % dot
                    print "Distance Factored:%10.3f" % dist_factored

                # weight between original and final
                final = (in_t_p + (vector * dot * weight)) - in_ppos_p

                if dot <= 0:
                    if VERBOSE:
                        print "do DOT"
                    out_trsl.set3Double(final[0]+(offset_p[0]*offset_w),
                                        final[1]+(offset_p[1]*offset_w),
                                        final[2]+(offset_p[2]*offset_w))
                else:
                    if VERBOSE:
                        print "do No DOT"
                    out_trsl.set3Double(in_lt_p[0]+(offset_p[0]*offset_w),
                                        in_lt_p[1]+(offset_p[1]*offset_w),
                                        in_lt_p[2]+(offset_p[2]*offset_w))

            else:
                out_trsl.set3Double(in_lt_p[0]+(offset_p[0]*offset_w),
                                    in_lt_p[1]+(offset_p[1]*offset_w),
                                    in_lt_p[2]+(offset_p[2]*offset_w))

            dataBlock.setClean(plug)


def get_om_node(name):
    """hack way of get OpenMaya node or dag path"""

    sellist = om.MSelectionList()
    sellist.add(name)
    node = om.MObject()
    dag_path = om.MDagPath()
    sellist.getDagPath(0, dag_path, node)

    return dag_path

    # if using new api
    # node = sellist.getDependNode(0)
    # sellist.getDependNode(0, node)


def distance_calc():
    """concept prototyping"""

    in_pos = om.MPoint(*pm.PyNode('locator1').translate.get())
    # in_pos = om.MPoint(1,2,3)
    out_pos = om.MPoint()
    out_normal = om.MVector()

    dagPath = get_om_node('pPlaneShape1')

    meshFn = om.MFnMesh(dagPath)

    meshFn.getClosestPointAndNormal(in_pos, out_pos, out_normal, om.MSpace.kWorld)

    print in_pos.x, in_pos.y, in_pos.z
    print out_pos.x, out_pos.y, out_pos.z
    print out_normal[0], out_normal[1], out_normal[2]

    tempVec = in_pos - out_pos
    tempVec_norm = tempVec.normal()
    print tempVec[0], tempVec[1], tempVec[2]
    print tempVec_norm[0], tempVec_norm[1], tempVec_norm[2]
    dot = tempVec_norm * out_normal
    print dot
    dist = in_pos.distanceTo(out_pos)
    print dist * dot
