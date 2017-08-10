import sys, os, json, arcpy, urllib2, urllib
from arcpy import env

def main():
    try:
        #############################
        ### Set config items
        #############################
        #ags env params
        env.overwriteOutput = True
        env.workspace = r"F:\arcgisresources\GeocodeAndIdentity\prod_data.gdb"
        if env.scratchWorkspace is None:
			env.scratchWorkspace = r"F:\arcgisresources\GeocodeAndIdentity\scratch"
        else:
			pass
        #the polygon feature class' to perform Identity on
        dacFeatures = "ca_dacs_Project"
        #the feature class to use as a template for a spatial reference for the geocoding WGS84 X,Y location values
        spatialRefFC = 'wgs84_spatial_ref'
        #the feature class to use as a template for attributes for the output point feature
        geocodeResultsFC = 'geocode_results2'
        #the feature class that holds the Identity results
        identityResultsFCName="geocode_results_dac_info_A.shp"
        identityResultsFC= os.path.join(env.scratchWorkspace,identityResultsFCName)

        #############################
        ### Get and set inpur parameters
        #############################
        arcpy.AddMessage("gpService: Starting process.")

        arcpy.AddMessage("gpService: Setting X")
        #Get Location X
        inX = arcpy.GetParameterAsText(0)
        if inX == '#' or not inX:
            #inX = "-123.123456"  #FOR TESTING
            #in Prod format appropiate error output and end process
            sys.exit("X coordinate is null")

        arcpy.AddMessage("gpService: Setting Y")
        #Get Location Y
        inY = arcpy.GetParameterAsText(1)
        if inY == '#' or not inY:
            #inY = "41.123456"  #FOR TESTING
            #in Prod format appropiate error output and end process
            sys.exit("Y coordinate is null")

        #############################
        ### start main proccess
        #############################


        arcpy.AddMessage("gpService: Creating point")

        #create a point geometry object from coords.
        newPoint = arcpy.Point(float(inX),float(inY))


        arcpy.AddMessage("gpService: Creating temp feature classes")
        #create temporary in-momory feature class for storing the point geom and attributes (using geocode_results fc as template). this will be turned into a feature set and used in the Identify operation
        spatialRef = arcpy.Describe(spatialRefFC).spatialReference
        pointfc = arcpy.CreateFeatureclass_management("in_memory", "tempfc", "POINT", geocodeResultsFC, "SAME_AS_TEMPLATE","SAME_AS_TEMPLATE",spatialRef)
        pointfc = arcpy.CreateFeatureclass_management("in_memory", "tempfc", "POINT", geocodeResultsFC, "SAME_AS_TEMPLATE","SAME_AS_TEMPLATE",spatialRef)
        feat = incur.newRow()
        feat.shape = newPoint
        incur.insertRow(feat)
        del incur

        arcpy.AddMessage("gpService: Create feature set")
        #create a feature set for use in the Identity process
        featSet = arcpy.FeatureSet()
        featSet.load(pointfc)

        arcpy.AddMessage("gpService: Make temp files")
        #make temp files
        arcpy.AddMessage("gpService: Make tempResultsFC1")
        tempResultsFC1 = arcpy.CreateFeatureclass_management(env.scratchWorkspace, "tempResultsFC1", "POINT", "#", "#","#",spatialRef)

        arcpy.AddMessage("gpService: Do the identify")
        #do Identity
        arcpy.Identity_analysis(featSet, dacFeatures, tempResultsFC1)

        # create output table views and get attributes
        arcpy.AddMessage("gpService: Create DAC output table view")
        #UTILITY
        outTableView1 = "result_table1"
        arcpy.MakeTableView_management(tempResultsFC1, outTableView1)
        rows = arcpy.SearchCursor(outTableView1, "", "", "dac")
        for row in rows:
            #print row.Score
            #score = row.Score
            print row.dac
            dac = row.dac
        del row, rows, outTableView1, tempResultsFC1

        arcpy.AddMessage("gpService: Delete temp files")
        arcpy.Delete_management(os.path.join(env.scratchWorkspace,"tempResultsFC1.shp"))

        arcpy.AddMessage("gpService: Compile results for output")
        msgResult = "Success"
        msgInfo = "Location Overlay Successful"
        outputString = "{'error':'%s','errMessage':'%s','success':'%s','successMessage':'%s','dac':'%s'}" % (False,'',True,msgInfo,dac)
        arcpy.AddMessage(outputString)
        arcpy.SetParameterAsText(2, outputString)
        arcpy.AddMessage("gpService: Finished process successfully")
    except SystemExit as e:
        #format and send system exit output here
        val, tb = sys.exc_info()[1:]
        print "Error: Line %s - %s" % (tb.tb_lineno, val)
        msgInfo = "%s" % (val)
        print msgInfo
        outputString = "{'error':'%s','errMessage':'%s','success':'%s','successMessage':%s,'dac':'%s'}" % (True,msgInfo,False,'')
        arcpy.SetParameterAsText(2, outputString)
        tb = None
        arcpy.AddMessage("gpService: Finished process with errors")
        arcpy.AddMessage("gpService: SystemExit handler")
        arcpy.AddMessage(msgInfo)
        arcpy.AddMessage("Line %s - %s" % (tb.tb_lineno, val))
    except Exception:
        #format and send unhandled exception output here
        val, tb = sys.exc_info()[1:]
        print "Error: Line %s - %s" % (tb.tb_lineno, val)
        msgInfo = "System error"
        print msgInfo
        outputString = "{'error':'%s','errMessage':'%s','success':%s,'successMessage':%s,'dac':'%s'}" % (True,msgInfo,False,'')
        arcpy.SetParameterAsText(2, outputString)
        tb = None
        arcpy.AddMessage("gpService: Finished process with errors")
        arcpy.AddMessage("gpService: Unhandled Exception")

if __name__ == "__main__":
	main()

