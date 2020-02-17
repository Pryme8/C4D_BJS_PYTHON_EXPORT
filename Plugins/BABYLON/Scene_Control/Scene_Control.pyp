import c4d
import os
import sys
import json
import math

from c4d import gui, documents, utils, storage, plugins, bitmaps, Vector
from math import pi

PLUGIN_ID = 1054498
__version__ = "1.0"
__plugin_title__ = "BABYLON Scene Control"
__author__ = "Pryme8"

#=================================
#SCENE CONTROL DECLATRIOS
#=================================
BJS_SCENE_CLEARCOLOR = 1000
BJS_SCENE_CLEARALPHA = 1001
BJS_SCENE_AMBIENTCOLOR = 1002
BJS_SCENE_MAX_LIGHTS = 1003

BJS_EXPORT_SCENE_TEMPLATE = 2000
#---------------------------------

#=================================
#JSON Encoder Class
#=================================
class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)
#---------------------------------
#=================================
#quick converters
#=================================
gScale = 0.2 #200 = 1 unit 
def scale(v):       
    return v*gScale

def getValue(op, v):
    return eval('op[c4d.'+v+']')

def Vec2(v):
    return {'x':v[0],'y':v[1]}

def Vec3(v):
    return {'x':v[0],'y':v[1],'z':v[2]}

def Vec3Rot(v):
    return {'x':v[1],'y':v[0],'z':v[2]}

def sVec3(v):
    return {'x':scale(v[0]),'y':scale(v[1]),'z':scale(v[2])}

def Orientation(axes):
    return ([{'x':1,'y':0,'z':0},{'x':-1,'y':0,'z':0},{'x':0,'y':1,'z':0},{'x':0,'y':-1,'z':0},{'x':0,'y':0,'z':1},{'x':1,'y':0,'z':-1}])[axes]

def LightTypes(t):
    return (["Point", "Spot", "Directional", "Directional"])[t]
#---------------------------------

#=================================
#BASIC TRANSFORMS CLASS
#=================================
class Transforms:
    def __init__(self):        
        self.position = None
        self.rotation = None
        self.scale = None
        
    def reprJSON(self):
        return dict(position=self.position, rotation=self.rotation, scale=self.scale)
    
#--------------------------------- 

#=================================
#NODE CLASS
#=================================
class Node:
    def __init__(self):
        self.type = 'node'
        self.subType = 'none'
        self.name = 'NewNode'
        self.transforms = Transforms()        
        self.children = []
        self.attributes = {}
        
    def __getitem__(self, arg):
        return str(arg)
    
    def parseObject(self, op):
        type = op.GetTypeName()
        if (
            type == "Cube" or
            type == "Plane" or
            type == "Torus" or
            type == "Sphere"
        ):            
            self.type = "Primitive"
            if type == "Plane":
                self.subType = "Ground"
            else:
                self.subType = type         
        else:    
            self.type = type
            
        self.name = op.GetName()
        
        #setTransforms
        self.transforms.position = Vec3(op.GetAbsPos())  
        self.transforms.rotation = Vec3Rot(op.GetAbsRot())
        self.transforms.scale = Vec3(op.GetAbsScale())
       
        description = op.GetDescription(c4d.DESCFLAGS_DESC_0)
        tags = op.GetTags()
        
        #CAMERAS
        if self.type == "Camera":
            tempTarget = c4d.BaseObject(c4d.Ocube)          
            tempTarget.InsertUnder(op)
            tempTarget.SetRelPos(c4d.Vector(0, 0, 2000))
            mat = tempTarget.GetMg()
            c4d.EventAdd()      
            
            self.attributes['CAMERA_TARGET'] =  Vec3(tempTarget.GetRelPos()*mat)
            
            tempTarget.Remove()
            for tag in tags:
                td = tag.GetDescription(c4d.DESCFLAGS_DESC_0)
                for bc, paramid, groupid in td:                    
                    if (
                        bc[c4d.DESC_IDENT] == "BJS_CAMERA_MAKE_DEFAULT" or
                        bc[c4d.DESC_IDENT] == "BJS_CAMERA_ATTACH_CONTROLS" or
                        bc[c4d.DESC_IDENT] == "BJS_CAMERA_SPEED" or
                        bc[c4d.DESC_IDENT] == "BJS_CAMERA_ANGULAR_SENSIBILITY"
                    ):
                        self.attributes[bc[c4d.DESC_IDENT]] = tag[paramid[0].id]
                        
                    elif bc[c4d.DESC_IDENT] == "BJS_CAMERA_Z_CLIP":
                        self.attributes[bc[c4d.DESC_IDENT]] = Vec2(tag[paramid[0].id])
        #-----------------
        
        #LIGHTS
        elif self.type == "Light":            
            for bc, paramid, groupid in description:
                if bc[c4d.DESC_IDENT] == "LIGHT_COLOR":                    
                    self.attributes[bc[c4d.DESC_IDENT]] = Vec3(getValue(op, bc[c4d.DESC_IDENT]))
                elif bc[c4d.DESC_IDENT] == "LIGHT_TYPE":
                    self.attributes[bc[c4d.DESC_IDENT]] = LightTypes(getValue(op, bc[c4d.DESC_IDENT]))
                elif bc[c4d.DESC_IDENT] == "LIGHT_BRIGHTNESS":
                    self.attributes[bc[c4d.DESC_IDENT]] = getValue(op, bc[c4d.DESC_IDENT])
        
            for tag in op.GetTags():
                td = tag.GetDescription(c4d.DESCFLAGS_DESC_0)
                for bc, paramid, groupid in td:
                     if bc[c4d.DESC_IDENT] == "BJS_LIGHT_SPECULAR":
                          self.attributes[bc[c4d.DESC_IDENT]] = Vec3(getValue(tag, bc[c4d.DESC_IDENT]))
        #-----------------
        
        #PRIMITIVES
        if self.type == "Primitive":
            for bc, paramid, groupid in description:
                if bc[c4d.DESC_IDENT] != None:
                    if (str(bc[c4d.DESC_IDENT]).split("_"))[0] == "PRIM":
                        _d = eval('op[c4d.'+bc[c4d.DESC_IDENT]+']')
                        if isinstance(_d, c4d.Vector):
                            self.attributes[bc[c4d.DESC_IDENT]] = Vec3(_d)
                        else:
                            if bc[c4d.DESC_IDENT] == 'PRIM_AXIS':
                                self.attributes[bc[c4d.DESC_IDENT]] = Orientation(_d)
                            else:  
                                self.attributes[bc[c4d.DESC_IDENT]] = _d
        #----------------- 
        
        #CHECK FOR GLOBAL TAGS
        for tag in tags:
            td = tag.GetDescription(c4d.DESCFLAGS_DESC_0)
            for bc, paramid, groupid in td:                    
                if (
                    bc[c4d.DESC_IDENT] == "BJS_EXPOSE_VARIABLE" or
                    bc[c4d.DESC_IDENT] == "BJS_EXPOSE_GLOBAL" or
                    bc[c4d.DESC_IDENT] == "BJS_VARIABLE_NAME"
                ):
                    self.attributes[bc[c4d.DESC_IDENT]] = tag[paramid[0].id]
        #----------------- 
    
    def reprJSON(self):
        return dict(type=self.type, subType=self.subType, name=self.name, transforms=self.transforms, attributes=self.attributes, children=self.children)
#---------------------------------


#=================================
#Recursion Function
#=================================
def recurse_hierarchy(op, data, parent):
    
    while op:        
        node = Node()
        node.parseObject(op)       
                
        if(op.GetDown()):
            recurse_hierarchy(op.GetDown(), data, node)        
        
        if(parent):
            parent.children.append(node)
        else:
            data.nodes.append(node)
            
        op = op.GetNext()
    return data
#---------------------------------

#=================================
#PARSED DATA CLASS
#=================================
class parsedScene:
    def __init__(self, op):
        self.nodes = []
        self.attributes = {}        
        description = op.GetDescription(c4d.DESCFLAGS_DESC_0)
        
        for bc, paramid, groupid in description:
            if bc[c4d.DESC_IDENT] != None:
                 if (
                    bc[c4d.DESC_IDENT] == "BJS_SCENE_CLEARCOLOR" or
                    bc[c4d.DESC_IDENT] == "BJS_SCENE_AMBIENTCOLOR" 
                 ):
                    self.attributes[bc[c4d.DESC_IDENT]] = Vec3(getValue(op, bc[c4d.DESC_IDENT]))
                 elif (
                    bc[c4d.DESC_IDENT] == "BJS_SCENE_CLEARALPHA" or
                    bc[c4d.DESC_IDENT] == "BJS_SCENE_MAX_LIGHTS" 
                 ):
                    self.attributes[bc[c4d.DESC_IDENT]] = getValue(op, bc[c4d.DESC_IDENT])
    
    def __getitem__(self, arg):
        return str(arg)
    
    def reprJSON(self):
        return dict( 
            nodes=self.nodes,
            attributes=self.attributes
            )
    
#---------------------------------

#=================================
#Parsing Function
#=================================
def startParse(op):
    data = parsedScene(op)
    data = recurse_hierarchy(op.GetDown(), data, False)    
    return data
#---------------------------------

#=================================
#SCENE CONTROL CLASS
#=================================
class Scene_Control(plugins.ObjectData):
    def __init__(self):
        return None

    def Init(self, node):
        #Scene Defaults
        #self.InitAttr(node, vector, BJS_SCENE_CLEARCOLOR)
        #self.InitAttr(node, float, BJS_SCENE_CLEARALPHA)        
        
        node[BJS_SCENE_CLEARCOLOR] = Vector(0.2, 0.2, 0.6)
        node[BJS_SCENE_CLEARALPHA] = 1.0        
        node[BJS_SCENE_AMBIENTCOLOR] = Vector(1.0, 1.0, 1.0)
        
        node[BJS_SCENE_MAX_LIGHTS] = 8

        return True
        
    def Execute(self, node, doc, bt, priority, flags):     
        return c4d.EXECUTIONRESULT_OK

    def Message(self, node, type, data):
        if type ==  c4d.MSG_DESCRIPTION_COMMAND:
            if data['id'][0].id == BJS_EXPORT_SCENE_TEMPLATE:
                self.Export(node)            
        return True

    def Export(self, node):        
            data = json.dumps((startParse(node)).reprJSON(), sort_keys=True, indent=4, separators=(',', ': '), cls=ComplexEncoder)
            #print data
            filePath = storage.LoadDialog(title="Save as Keeyah Template", flags=c4d.FILESELECT_SAVE, force_suffix="json")
            if filePath is None:
                return
            #open file
            f = open(filePath,"w")
            f.write(data)
            f.close()        
            c4d.CopyStringToClipboard("KEEEYAH!")
            gui.MessageDialog(".json file exported")

if __name__ == "__main__":
    bmp = bitmaps.BaseBitmap()
    dir, file = os.path.split(__file__)
    bitmapfile = os.path.join(dir, "res", "Icon.tif")
    
    result = bmp.InitWith(bitmapfile)
    
    if not result:
        print "Error loading Icon!"
    
    okyn = plugins.RegisterObjectPlugin( 
        id=PLUGIN_ID,
        str="Scene_Control",
        info=c4d.OBJECT_GENERATOR,
        g=Scene_Control,
        description="Scene_Control",
        icon=bmp
    )
    
    print "BJS_Scene_Control Initialized", okyn
#---------------------------------