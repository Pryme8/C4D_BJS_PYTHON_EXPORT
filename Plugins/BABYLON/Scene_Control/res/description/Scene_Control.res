CONTAINER Scene_Control
{
	NAME Scene_Control;
	INCLUDE Obase;

	GROUP ID_OBJECTPROPERTIES
	{   
        GROUP
        {
            LAYOUTGROUP; COLUMNS 2;

            GROUP
            {
                COLOR       BJS_SCENE_CLEARCOLOR        { PARENTCOLLAPSE; }
                REAL        BJS_SCENE_CLEARALPHA        { MIN 0; MAX 1; STEP 0.01; }
            }

            GROUP
            {
                COLOR       BJS_SCENE_AMBIENTCOLOR      { PARENTCOLLAPSE; }
            }             
        }
        SEPARATOR { LINE; }
        GROUP
        {
            LONG        BJS_SCENE_MAX_LIGHTS        { MIN 1; }
        }
        SEPARATOR { LINE; }
        GROUP
        {
            BUTTON BJS_EXPORT_SCENE_TEMPLATE { }
        }       
	}
}