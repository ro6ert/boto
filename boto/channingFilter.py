from boto.resultset import ResultSet
import boto.handler
import xml.sax
#import xml.etree.ElementTree as ET
import elementtree.ElementTree as ET

def channingFilter(body,params,markers,parent):
    rs = ResultSet(markers)
    h = boto.handler.XmlHandler(rs,parent)
    filteredBody = filterBody(body,params)
    xml.sax.parseString(filteredBody,h)
    return rs

def filterBody(body,params):
    """See http://stackoverflow.com/questions/9700803/how-to-find-element-in-kml-tree-containing"""
    root = ET.XML(body)
    parentdict = createParentDict(root)
    #print parentdict
    #prefix = "http://ec2.amazonaws.com/doc/2012-12-01/"
    prefix = "http://ec2.amazonaws.com/doc/2011-01-01/"
    ET.register_namespace("euca",prefix)
    boto.log.debug( "channingFilter.py filterBody root: "+str(root))
    itemsToRemove = []
    parameters = processParameters(params)
    for item in root.findall('.//{'+prefix+'}item'):
        boto.log.debug( "ChanningFilter.py params: "+str(parameters))
        boto.log.debug( "ChanningFilter.py itemtag: "+ str(item.tag))
        boto.log.debug( "ChanningFilter.py text : " + str(item.text))
        keepItem = True
        for param in parameters:
            element = item.find("{"+prefix+"}"+param)
            boto.log.debug( "ChanningFilter.py element: " + str(element))
            if element is not None and element.text in parameters[param]:
                pass
            else:
                keepItem = False
        if not keepItem:
            itemsToRemove.append(item)
        
    for item in itemsToRemove:
         parentdict[item].remove(item)
    boto.log.debug( "channingFilter.py finalversionofstring: "+ET.tostring(root).replace("euca:",""))
    #return body
    return ET.tostring(root).replace("euca:","")

def createParentDict(element):
    return parentDict(element,{})

def parentDict(element,parentdict):
    for child in element:
        parentdict[child] = element
        parentdict = parentDict(child,parentdict)
    return parentdict

def toCamel(string):
    stringList = string.split("-")
    returnstring = stringList[0]
    for st in stringList[1:]:
        returnstring+=st[0].upper()
        returnstring+=st[1:]
    return returnstring

def processParameters(params):
    returnDict = {}
    for i in range(1,10):
        prospectiveName = "Filter."+str(i)+".Name"
        if prospectiveName in params:
            possibleValues = []
            for j in range(1,10):
                prospectiveValue = "Filter."+str(i)+".Value."+str(j) 
                if prospectiveValue in params:
                    possibleValues.append(params[prospectiveValue])
            returnDict[toCamel(params[prospectiveName])] = possibleValues 
    return returnDict
