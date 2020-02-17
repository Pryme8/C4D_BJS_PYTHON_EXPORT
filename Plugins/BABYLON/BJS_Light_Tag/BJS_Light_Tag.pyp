import c4d
import os
import sys
from c4d import gui, plugins, bitmaps, Vector

PLUGIN_ID = 1054495
__version__ = "1.0"
__plugin_title__ = "BABYLON Light Tag"

BJS_LIGHT_SPECULAR = 1000

class BJS_Light_Tag(plugins.TagData):
    pass #code
    
    def Init(self, node):
        tag = node
        data = tag.GetDataInstance()
        
        data.SetVector(BJS_LIGHT_SPECULAR, Vector(1,1,1))
        
        return True
    
    def Execute(self, tag, doc, op, bt, priority, flags):
        data = tag.GetDataInstance()
        
        specular = data.GetVector(BJS_LIGHT_SPECULAR)
        
        return c4d.EXECUTIONRESULT_OK

if __name__ == "__main__":
    bmp = bitmaps.BaseBitmap()
    dir, file = os.path.split(__file__)
    bitmapfile = os.path.join(dir, "res", "Icon.tif")
    
    result = bmp.InitWith(bitmapfile)
    
    if not result:
        print "Error loading Icon!"
    
    okyn = plugins.RegisterTagPlugin(id=PLUGIN_ID, str="BJS Light Tag", info=c4d.TAG_VISIBLE|c4d.TAG_EXPRESSION, g=BJS_Light_Tag, description="BJS_Light_Tag", icon=bmp)
    print "BJS_Light_Tag Initialized", okyn