import c4d
import os
import sys
from c4d import gui, plugins, bitmaps, Vector

PLUGIN_ID = 1054494
__version__ = "1.0"
__plugin_title__ = "BABYLON Camera Tag"
__author__ = "Pryme8"

BJS_CAMERA_MAKE_DEFAULT = 10001
BJS_CAMERA_ATTACH_CONTROLS = 10002
BJS_CAMERA_SPEED = 10003
BJS_CAMERA_ANGULAR_SENSIBILITY = 10004
BJS_CAMERA_Z_CLIP = 10005

class BJS_Camera_Tag(plugins.TagData):
    pass #code
    
    def Init(self, node):
        tag = node
        data = tag.GetDataInstance()
        
        data.SetBool(BJS_CAMERA_MAKE_DEFAULT, False)
        data.SetBool(BJS_CAMERA_ATTACH_CONTROLS, False)
        data.SetReal(BJS_CAMERA_SPEED, 100)
        data.SetReal(BJS_CAMERA_ANGULAR_SENSIBILITY, 800)
        data.SetVector(BJS_CAMERA_Z_CLIP, Vector(1, 10000, 0))
        
        return True
    
    def Execute(self, tag, doc, op, bt, priority, flags):
        data = tag.GetDataInstance()
        
        default = data.GetBool(BJS_CAMERA_MAKE_DEFAULT)
        attachControls = data.GetBool(BJS_CAMERA_ATTACH_CONTROLS)
        speed = data.GetReal(BJS_CAMERA_SPEED)
        angular = data.GetReal(BJS_CAMERA_ANGULAR_SENSIBILITY)
        zClip = data.GetVector(BJS_CAMERA_Z_CLIP)
        
        return c4d.EXECUTIONRESULT_OK

if __name__ == "__main__":
    bmp = bitmaps.BaseBitmap()
    dir, file = os.path.split(__file__)
    bitmapfile = os.path.join(dir, "res", "icon.png")
    
    result = bmp.InitWith(bitmapfile)
    
    if not result:
        print "Error loading Icon!"
    
    okyn = plugins.RegisterTagPlugin(id=PLUGIN_ID, str="BJS Camera Tag", info=c4d.TAG_VISIBLE|c4d.TAG_EXPRESSION, g=BJS_Camera_Tag, description="BJS_Camera_Tag", icon=bmp)
    print "BJS_Camera_Tag Initialized", okyn