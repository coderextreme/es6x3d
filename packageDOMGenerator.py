import xml.etree.ElementTree
import re

# an alone field, no choice table
class alone_field(object):
    def __init__(self, name, type):
        self.attrs = {}
        self.attrs['name'] = name
        self.attrs['type'] = type
        return None
    def get(self, field):
        return self.attrs[field]
    def __getitem__(self, field):
        return self.attrs[field]
    def iter(self, field):
        return []

# class printer
class ClassPrinter(object):
    def __init__(self, node, name, meta = ""):
        self.__choice_table = \
        {
            "initializeOnly": self.initialize,
            "inputOnly": self.setter,
            "inputOutput": self.settergetter,
            "outputOnly": self.getter,
            "toXMLNode": self.toXMLNode,
            "deepExpand": self.deepExpand,
            "fromJSON": self.fromJSON,
            None: self.getter
        }
        self.node = node
        self.name = name
        self.parents = []
        self.metaInfo = meta

        # addinhers = self.node.iter("AdditionalInheritance")
        # for addinher in addinhers:
        #    self.parents.append(addinher.get('baseType'))

        inhers = self.node.iter("Inheritance")
        for inher in inhers:
            self.parents.append(inher.get('baseType'))

        self.printed = False

    # get private variable
    def private(self, fld):
        if fld == "Children":
                fld = "children"
        return "this.__"+fld

    # get field name from self and name
    def getField(self, name):
        start = self.getStart(name)
        name = self.getName(name)
        if name == 'class':
            fld = name + "_"
        elif name == 'global':
            fld = name + "_"
        elif name == 'function':
            fld = name + "_"
        elif name == 'Children':
            fld = "children_"
        else:
            fld = name
        return fld

    # get name minus preop
    def getName(self, name):
        start = self.getStart(name)
        if name == "address":
            pass
        elif re.search(r"_changed$", name):
            name = name
        elif re.search(r"^addSet", name):
            name = name[start+3:start+4].upper() + name[start+4:]
        elif re.search(r"^removeSet", name):
            name = name[start+3:start+4].upper() + name[start+4:]
        elif re.search(r"^getSet", name):
            name = name[start+3:start+4].upper() + name[start+4:]
        elif re.search(r"^add", name):
            name = name[start:start+1].upper() + name[start+1:]
        elif re.search(r"^remove", name):
            name = name[start:start+1].upper() + name[start+1:]
        elif re.search(r"^is", name):
            name = name[start:start+1].upper() + name[start+1:]
        elif re.search(r"^set_", name):
            name = name[start:]
        elif re.search(r"^set", name):
            name = name[start:start+1].lower() + name[start+1:]
        elif re.search(r"^get", name):
            name = name[start:start+1].lower() + name[start+1:]
        return name

    # get funciton name
    def getFunctionName(self, name):
        start = self.getStart(name)
        functionName = name[:start] + self.getName(name)
        return functionName

    # get start of property name
    def getStart(self, name):
        start = 0
        if name == "address":
            start = 0
        elif re.search(r"_changed$", name):
            start = 0
        elif re.search(r"^addSet", name):
            start = 3
        elif re.search(r"^removeSet", name):
            start = 6
        elif re.search(r"^getSet", name):
            start = 3
        elif re.search(r"^add", name):
            start = 3
        elif re.search(r"^remove", name):
            start = 6
        elif re.search(r"^is", name):
            start = 2
        elif re.search(r"^set_", name):
            start = 4
        elif re.search(r"^set", name):
            start = 3
        elif re.search(r"^get", name):
            start = 3
        return start


    # get default value for field
    def getDefault(self, field):
        str = ""
        try:
            if field.get('type').startswith("MF") or field.get('type') == "SFColor" or field.get('type') == "SFVec2f" or field.get('type') == "SFVec3f":
                els = re.split("[, \r\n\t]+", field.get('default'))
                str += '[' + (", ".join(els)) + ']'
            elif field.get('type') == 'SFString':
                str += '"'+field.get('default')+'"'
            elif re.search(r"\s", field.get('default')):
                str += '[' + ", ".join(field.get('default').split()) + ']'
            else:
                if field.get('default') == 'true':
                    field.set('default', 'true')
                if field.get('default') == 'false':
                    field.set('default', 'false')
                if field.get('default') == 'NULL':
                    field.set('default', 'null')
                str += field.get('default')
        except:
                str += "null"
        return str


    def toXMLNode(self, field, name):
        str = ''
        fld = self.getField(name)

        spf = self.private(fld)
        str += "        if ("+spf+" === null) {\n"
        str += "        } else if (typeof "+spf+" !== 'undefined' && typeof "+spf+".toXMLNode === 'function') {\n"
        str += "                str += "+spf+".toXMLNode('"+fld+"');\n"
        str += "        } else if (typeof "+spf+" === 'string') {\n"
        str += "            str += ' "+fld+"=\"'+"+spf+"+'\"';\n"
        str += "        } else if (Array.isArray( "+spf+")) {\n"
        str += "            if (typeof "+spf+"[0].toXMLNode !== 'function') {\n"
        str += "                    str += ' "+fld+"=\"'+"+spf+".join(' ')+'\"';\n"
        str += "            } else {\n"
        str += "                for (let i in "+spf+") {\n"
        str += "                    if (typeof "+spf+"[i].toXMLNode === 'function') {\n"
        str += "                        str += "+spf+"[i].toXMLNode('"+fld+"');\n"
        str += "                    }\n"
        str += "                }\n"
        str += "            }\n"
        str += "        } else {\n"
        str += "            str += ' "+fld+"=\"'+"+spf+"+'\"';\n"
        str += "        }\n"
        return str

    # generate convert to XML
    def deepExpand(self, field, name):
        str = ''
        fld = self.getField(name)

        spf = self.private(fld)
        str += "        if (typeof "+spf+" === 'undefined' || "+spf+" === null) {\n"
        # str += "            obj['"+fld+"'] = null;\n"
        str += "        } else if (typeof "+spf+".deepExpand === 'function') {\n"
        str += "                obj['"+fld+"'] = "+spf+".deepExpand();\n"
        str += "        } else if (typeof "+spf+" === 'string') {\n"
        str += "                obj['"+fld+"'] = "+spf+";\n" 
        str += "        } else if (Array.isArray( "+spf+")) {\n"
        str += "            if (typeof "+spf+"[0].deepExpand !== 'function') {\n"
        str += "                    obj['"+fld+"'] = "+spf+".join(' ');\n"
        str += "            } else {\n"
        str += "                obj['"+fld+"'] = [];\n"
        str += "                for (let i in "+spf+") {\n"
        str += "                    if (typeof "+spf+"[i].deepExpand === 'function') {\n"
        str += "                        obj['"+fld+"'].push("+spf+"[i].deepExpand());\n"
        str += "                    }\n"
        str += "                }\n"
        str += "            }\n"
        str += "        } else {\n"
        str += "            obj['"+fld+"'] = "+spf+";\n"
        str += "        }\n"
        return str

    # generate convert to XML
    def fromJSON(self, field, name):
        str = ''
        fld = self.getField(name)

        spf = self.private(fld)
        str += "        if (Array.isArray(object)) {\n"
        str += "            "+spf+" = new "+field.get('type')+"(object);\n"
        str += "            for (let i in object) {\n"
        str += "                "+spf+".push(object[i]);\n"
        str += "                "+spf+".fromJSON(object[i]);\n"
        str += "            }\n"
        str += "            // console.log(7, "+spf+",'"+fld+"',"+self.name+",'array');\n"
#        str += "        } else if (typeof "+spf+" === 'undefined' || "+spf+" === null) {\n"
#        str += "            "+spf+" = new "+field.get('type')+"(object['"+fld+"']);\n"
#        str += "            // console.log(1,JSON.stringify("+spf+"), '"+fld+"',"+self.name+",);\n"
        str += "        } else if ('"+field.get('type')+"' === 'SFNode') {\n"
        str += "            "+spf+" = new "+field.get('type')+"(object['"+fld+"'])\n"
        str += "            // console.log(9, "+spf+",'"+fld+"',"+self.name+",'');\n"
        # str += "            "+spf+".fromJSON(object['"+fld+"']);\n"
        str += "        } else if ('"+field.get('type')+"' === 'MFNode') {\n"
        str += "            "+spf+" = new "+field.get('type')+"(object['-"+fld+"']);\n"
        str += "            // console.log(2, "+spf+",'"+fld+"',"+self.name+",'-');\n"
        str += "            "+spf+".fromJSON(object['-"+fld+"']);\n"
        str += "        } else if ('"+field.get('type')+"' === 'SFNode') {\n"
        str += "            "+spf+" = new "+field.get('type')+"(object['-"+fld+"']);\n"
        str += "            // console.log(3, "+spf+",'"+fld+"',"+self.name+",'-');\n"
        str += "            "+spf+".fromJSON(object['-"+fld+"']);\n"
        str += "        } else if ('"+field.get('type')+"'.startsWith('MF')) {\n"
        str += "            "+spf+" = new "+field.get('type')+"(object['@"+fld+"']);\n"
        str += "            // console.log(4, "+spf+",'"+fld+"',"+self.name+",'@');\n"
        str += "            "+spf+".fromJSON(object['@"+fld+"']);\n"
        str += "        } else if ('"+field.get('type')+"'.startsWith('SF')) {\n"
        str += "            "+spf+" = new "+field.get('type')+"(object['@"+fld+"']);\n"
        str += "            // console.log(5, "+spf+",'"+fld+"',"+self.name+",'@');\n"
        str += "            "+spf+".fromJSON(object['@"+fld+"']);\n"
        str += "        } else if ('"+field.get('type')+"'.startsWith('#')) {\n"
        str += "            "+spf+" = new "+field.get('type')+"(object['#"+fld+"']);\n"
        str += "            // console.log(6, "+spf+",'"+fld+"',"+self.name+",'#');\n"
        str += "            "+spf+".fromJSON(object['#"+fld+"']);\n"
        str += "        } else {\n"
        str += "            "+spf+" = new "+field.get('type')+"(object['"+fld+"'])\n"
        str += "            // console.log(8, "+spf+",'"+fld+"',"+self.name+",'');\n"
        str += "            "+spf+".fromJSON(object['"+fld+"']);\n"
        str += "        }\n"
        return str

    # run choice initialize only
    def initialize(self, field, name):
        str = ""
        fld = self.getField(name)
        str += '        var '+fld+'  = ' + 'jsonobj["__' + fld + '"] || jsonobj["' + fld + '"] || jsonobj["@' + fld + '"] || jsonobj["-' + fld + '"] || jsonobj["#' + fld + '"] || ' + self.getDefault(field) + ";\n"
        # str += '        console.log('+fld+');\n'
        if fld != "accessType":  # hack for now, no check on null accessTypes
            str += self.settervalidate(field, fld)
        str += '        '+self.private(fld)+' = '+fld+';\n'
        return str

    # generate setter function with validation
    def settervalidate(self, field, name):
        fld = self.getField(name)
        str = ""
        rel = { 'minInclusive':" < ",
                 'maxInclusive':" > ",
                 'minExclusive':" <= ",
                 'maxExclusive':" >= "}
        for k,v in rel.items():
            try:
                if field.get('type').startswith("MF") or field.get('type') == "SFColor" or field.get('type') == "SFVec2f" or field.get('type') == "SFVec3f":
                    str += "        if ("+fld+" == null || "+fld+".length <= 0 || Math."+k[0:3] +"("+fld+") " + v + " " + field.get(k) + ") {\n"
                    str += "            return undefined;\n\t}\n"
                else:
                    str += "        if ("+fld+" == null || "+fld+" " + v + " " + field.get(k) + ") {\n"
                    str += "            return undefined;\n\t}\n"
            
            except:
                pass

        try:
            if field.get('additionalEnumerationValuesAllowed') != "true":
                enumerations = field.iter("enumeration")
                efound = 0
                for enum in enumerations:
                    if efound == 0:
                        str += "        if (" + "'"+enum.get('value')+"'" + ' === '+fld+') {\n'
                        efound = 1
                    else:
                        str += "        } else if (" + "'"+enum.get('value')+"'" + ' === '+fld+') {\n'
                if efound == 1:
                    str +=     "        } else {\n"
                    if field.get('use') == 'required':
                        str +=     "            return undefined;\n"
                    str +=     "        }\n"
        except KeyError:
            pass
        return str

    # generate code for setter of field's name
    def setter(self, field, name):
        str = ""
        fld = self.getField(name)

        # this may be cheating, if there's a setter, there must be a property
        # str += '    get '+ fld + '() {\n'
        # str += '        return ' + self.private(fld) + ";\n\t}\n"

        if fld.startswith("SF") or fld.startswith("MF"):
            str += '    set ' + fld +'(value = ' + self.getDefault(field) +  ") {\n"
            str += self.settervalidate(field, "value")
            if fld.startswith("MF"):
                str += '        '+self.private(fld)+' = [value];\n\t}\n'
            else:
                str += '        '+self.private(fld)+' = value;\n\t}\n'

        if not name.startswith("add") and not name.startswith("remove"):
            if name.startswith('set'):
                functionName = self.getFunctionName(name)
            else:
                functionName = self.getFunctionName(name)
            str += '    set ' + functionName +'(' + fld +' = ' + self.getDefault(field) +  ") {\n"
            str += self.settervalidate(field, name)
            if fld.startswith("MF"):
                str += '        '+self.private(fld)+' = ['+fld+"];\n"
            else:
                str += '        '+self.private(fld)+' = '+fld+";\n"
            str += "        return this;\n\t}\n"

        if not name.startswith("set") and not name.startswith("remove"):
            if name.startswith('add'):
                functionName = self.getFunctionName(name)
            else:
                functionName = self.getFunctionName("add"+name)
            str += '    ' + functionName +'(' + fld +' = ' + self.getDefault(field) +  ") {\n"
            str += self.settervalidate(field, name)
            str += "        if ("+self.private(fld)+" == null) {\n"
            str += '            '+self.private(fld)+' =  [];\n'
            str += '        }\n'
            str += '        '+self.private(fld)+'.append('+fld+');\n'
            str += "        return this;\n\t}\n"

        return str


    # code to output getter value of field's name
    def getter(self, field, name):
        str = ""
        fld = self.getField(name)

        if not name.startswith("is"):
            functionName = self.getFunctionName("remove"+name)
            str += '    ' + functionName +'('+fld+") {\n"
            str += '        for( let i = 0; i < '+self.private(fld)+'.length; i++) {\n'
            str += '             if ( '+self.private(fld)+'[i] === '+fld+') {\n'
            str += '                 '+self.private(fld)+'.splice(i, 1);\n'
            str += '             }\n'
            str += '        }\n'
            str += '        return ' + self.private(fld) + ";\n\t}\n"

        if field.get('type') == 'SFBool':
            if name.startswith('is'):
                functionName = self.getFunctionName(name)
            else:
                functionName = self.getFunctionName("is"+name)
            str += '    get '+ functionName + '() {\n'
            str += '        return ' + self.private(fld) + ";\n\t}\n"

        else:
            functionName = self.getFunctionName(name)
            if functionName == 'Children':
                functionName = "children"
            str += '    get '+ functionName + '() {\n'
            str += '        return ' + self.private(fld) + ";\n\t}\n"

            # functionName = self.getFunctionName(name+"_changed")
            # str += '    get '+ functionName + '() {\n'
            # str += '        return ' + self.private(fld) + ";\n\t}\n"

        return str

    # code to output setter and getter
    def settergetter(self, field, name):
        str = ""
        str += self.setter(field, name)
        str += self.getter(field, name)
        return str

    # cleanup field
    def processField(self, field):
        name = field.get('name')
        name = re.sub(r"-", "_", name)
        name = re.sub(r":", "_", name)
        return name


    # get choice table function from access type, field and name
    def setUpField(self, field, accessType):
        name = self.processField(field)
        return self.__choice_table[accessType](field, name)

    # get choice function from access type, field and name
    def setUpAloneField(self, fieldname, fieldtype, accessType):
        field = alone_field(fieldname, fieldtype)
        return self.setUpField(field, accessType)


    # print the class
    def printClass(self):
        str = ""
        if self.printed:
            return str
        for parent in self.parents:
            try:
                str += classes[parent].printClass()
            except:
                pass
        str += 'export'
        #if self.name == "X3D":
        #    str += " default"
        str += ' class ' + self.name + self.metaInfo
        strjoin = ", ".join(self.parents)
        if strjoin != "" and not strjoin.startswith("xs:") and strjoin != "SFString":
            str += " extends "+strjoin
        elif self.name.startswith("SF") or self.name.startswith("MF"):
            str += " extends Array"
        str += " {\n"
        if self.name.startswith("SF") or self.name.startswith("MF"):
            str += "    constructor(jsonobj = null) {\n"
            str += "        super(jsonobj);\n"
            str += "        this.__value = jsonobj;\n"
        elif self.name in [ 'X3D', 'X3DNode', 'X3DBoundedObject', 'X3DFogObject', 'X3DMetadataObject', 'X3DPickableObject', 'X3DProgrammableShaderObject', 'X3DUrlObject', 'component', 'connect', 'EXPORT', 'ExternProtoDeclare', 'field', 'fieldValue', 'head', 'IMPORT', 'IS', 'meta', 'ProtoBody', 'ProtoDeclare', 'ProtoInterface', 'ROUTE', 'Scene', 'unit']:
            str += "    constructor(jsonobj) {\n"
        else:
            str += "    constructor(jsonobj) {\n"
            str += "        super(jsonobj);\n"
            
        # create constructor body
        fields = self.node.iter("field")

        for field in fields:
            str += self.setUpField(field, "initializeOnly")

        if self.name == "Script":
            str += self.setUpAloneField("field", 'MFNode', "initializeOnly")
            str += self.setUpAloneField("IS", 'MFNode', "initializeOnly")
        if self.name == "ComposedShader":
            str += self.setUpAloneField("field", 'MFNode', "initializeOnly")
        if self.name == "field":
            str += self.setUpAloneField("children", 'MFNode', "initializeOnly")
        if self.name == "Scene":
            str += self.setUpAloneField("LayerSet", 'MFNode', "initializeOnly")

        str += "\t}\n"

        # now create other functions
        fields = self.node.iter("field")

        for field in fields:
            if field.get('accessType') != 'initializeOnly':
                str += self.setUpField(field, field.get('accessType'))

        if not re.search(r"^SF", self.name) and not re.search(r"^MF", self.name):
            str += self.setUpAloneField("comments", '#comment', "inputOnly")

        if self.name == "ComposedShader":
            str += self.setUpAloneField("sourceCode", '#cdata', "inputOnly")
        elif self.name == "Script":
            str += self.setUpAloneField("sourceCode", '#cdata', "inputOnly")
        elif self.name == "Collision":
            str += self.setUpAloneField("proxy", 'MFNode', "inputOnly")
        elif self.name == "LayerSet":
            str += self.setUpAloneField("order", 'MFInt32', "inputOnly")

        if self.name == "ComposedShader":
            str += self.setUpAloneField("field", 'MFNode', "inputOutput")
        elif self.name == "Script":
            str += self.setUpAloneField("field", 'MFNode', "inputOutput")
        elif self.name == "field":
            str += self.setUpAloneField("children", 'MFNode', "inputOutput")
        elif self.name == "head":
            str += self.setUpAloneField("meta", 'MFNode', "inputOutput")
        elif self.name == "Scene":
            str += self.setUpAloneField("LayerSet", 'MFNode', "inputOutput")

        if self.name in [ "TouchSensor", "NavigationInfo", "Viewpoint", "OrientationInterpolator", "PositionInterpolator", "DirectionalLight", "Group", "Transform", "Shape", "Material", "Script", "ProtoInstance", "ShaderPart" ]:
            str += self.setUpAloneField("IS", 'MFNode', "inputOutput")


        # stream to XML
        str += "    toXMLNode(attrName) {\n"
        str += "        let str = ''\n"
        if self.name.startswith("SFNode") or self.name.startswith("MFNode"):
            # str += "        str += this.__value;\n"
            str += "        for (let i in this.__value) {\n"
            str += "            if (typeof this.__value[i].toXMLNode === 'function') {\n"
            str += "                str += this.__value[i].toXMLNode(attrName);\n"
            str += "            }\n"
            str += "        }\n"
        elif self.name.startswith("SF") or self.name.startswith("MF"):
            str += "        str += ' '+attrName+'='+'\"'+this.__value+'\"';\n"
        else:
            str += "        str += '<"+self.name+"'\n"

            fields = self.node.iter("field")
            for field in fields:
                if field.get("type") not in ['SFNode', 'MFNode']:
                    str += self.setUpField(field, "toXMLNode")
            str += "        str += '>'\n"

            fields = self.node.iter("field")
            for field in fields:
                if field.get("type") in ['SFNode', 'MFNode']:
                    str += self.setUpField(field, "toXMLNode")
            str += "        str += '</"+self.name+">'\n"
        str += "        return str;\n\t}\n"



        # deep expand
        str += "    deepExpand() {\n"
        if self.name.startswith("SFNode") or self.name.startswith("MFNode"):
            str += "        let obj = [];\n"
            str += "        for (let i in this.__value) {\n"
            str += "            if (typeof this.__value[i].deepExpand === 'function') {\n"
            str += "                obj.push(this.__value[i].deepExpand());\n"
            str += "            }\n"
            str += "        }\n"
        elif self.name.startswith("SF") or self.name.startswith("MF"):
            str += "        let obj = this.__value;\n"
        else:
            str += "        let obj = {};\n"
            fields = self.node.iter("field")
            for field in fields:
                if field.get("type") not in ['SFNode', 'MFNode']:
                    str += self.setUpField(field, "deepExpand")

            fields = self.node.iter("field")
            for field in fields:
                if field.get("type") in ['SFNode', 'MFNode']:
                    str += self.setUpField(field, "deepExpand")
        str +=  "       return new "+self.name+"(obj);\n"
        str +=  "\t}\n";

        # from JSON
        str += "\tfromJSON(object) {\n"
        str += "        this.__value = object;\n";

        fields = self.node.iter("field")
        for field in fields:
            if field.get("type") not in ['SFNode', 'MFNode']:
                str += self.setUpField(field, "fromJSON")

        fields = self.node.iter("field")
        for field in fields:
            if field.get("type") in ['SFNode', 'MFNode']:
                str += self.setUpField(field, "fromJSON")

        str +=  "\treturn this;\n"
        str +=  "\t}\n"
        str +=  "}\n"

        self.printed = True
        return str


code = "// Do not modify\n"
#code += "import xmldom\n"
#code += "let DOMImplementation = new xmldom.DOMImplementation();\n"
#code += "let docType = DOMImplementation.createDocumentType('X3D', 'ISO//Web3D//DTD X3D 4.0//EN"+' '+"http://www.web3d.org/specifications/x3d-4.0.dtd', null);\n"
#code += "let document = DOMImplementation.createDocument(null, 'X3D', docType);\n"
#code += "document.insertBefore(xmldom.createProcessingInstruction('xml', 'version='1.0' encoding='UTF-8'), docType);\n"

soup = xml.etree.ElementTree.parse(open("c:/x3d-code/www.web3d.org/specifications/X3dUnifiedObjectModel-4.0.xml")).getroot()

classes = {}

ants = soup.iter("AbstractNodeType")
for ant in ants:
    classes[ant.get('name')] = ClassPrinter(ant, ant.get('name'))

aots = soup.iter("AbstractObjectType")
for aot in aots:
    classes[aot.get('name')] = ClassPrinter(aot, aot.get('name'))

cns = soup.iter("ConcreteNode")
for cn in cns:
    classes[cn.get('name')] = ClassPrinter(cn, cn.get('name'), "")

sts = soup.iter("Statement")
for st in sts:
    classes[st.get('name')] = ClassPrinter(st, st.get('name'), "")

fts = soup.iter("FieldType")
for ft in fts:
    classes[ft.get('type')] = ClassPrinter(ft, ft.get('type'), "")

for k,v in classes.items():
    code += v.printClass()

f = open("fromNodeX3d.js", "w")
f.write(code)
f.close()
