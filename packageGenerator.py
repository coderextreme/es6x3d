import xml.etree.ElementTree
import re

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

class ClassPrinter(object):
    def __init__(self, node, name, meta = ""):
        self.__choice_table = \
        {
            "initializeOnly": self.initialize,
            "inputOnly": self.setter,
            "inputOutput": self.settergetter,
            "outputOnly": self.getter,
            "toXMLNode": self.toXMLNode,
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

    def private(self, fld):
        if fld == "Children":
                fld = "children"
        return "this.__"+fld

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

    def getFunctionName(self, name):
        start = self.getStart(name)
        functionName = name[:start] + self.getName(name)
        return functionName

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
        str += "            if (typeof "+spf+" !== 'undefined') {\n"
        str += "                str += ' "+fld+"=\"'+"+spf+"+'\"';\n"
        str += "            }\n"
        str += "        } else if (Array.isArray( "+spf+")) {\n"
        str += "            if (typeof "+spf+"[0].toXMLNode !== 'function') {\n"
        str += "                if (typeof "+spf+" !== 'undefined') {\n"
        str += "                    str += ' "+fld+"=\"'+"+spf+".join(' ')+'\"';\n"
        str += "                }\n"
        str += "            } else {\n"
        str += "                for (let i in "+spf+") {\n"
        str += "                    if (typeof "+spf+"[i].toXMLNode === 'function') {\n"
        str += "                        str += "+spf+"[i].toXMLNode('"+fld+"');\n"
        str += "                    }\n"
        str += "                }\n"
        str += "            }\n"
        str += "        } else if (typeof "+spf+" !== 'undefined') {\n"
        str += "            str += ' "+fld+"=\"'+"+spf+"+'\"';\n"
        str += "        }\n"
        return str

    def initialize(self, field, name):
        str = ""
        fld = self.getField(name)
        try:
            # acceptabletypes = field.get("acceptableNodeTypes").split("|")
            if acceptabletypes is None:
                acceptabletypes = [field.get("type")]
        except:
            acceptabletypes = [field.get("type")]
        if acceptabletypes is not None:
            str += "        if ("
            ats = []
            for at in acceptabletypes:
                ats.append('kwargs["' + fld + '"]'  + " instanceof " + at)
            str += (" || ".join(ats))
            str += ") {\n"
        else:
            str += "        if (true) {\n"
        str += '            var xxx'+fld+'  = ' + 'kwargs["' + fld + '"] || ' + self.getDefault(field) + ";\n"
        #  if fld != "accessType":  # hack for now, no check on null accessTypes
        str += self.settervalidate(field, fld)
        str += '            '+self.private(fld)+' = xxx'+fld+';\n'
        str += '        } else if (typeof kwargs["' + fld + '"] !== "undefined") {\n'
        str += '           console.log("'+name+' with value"'+ ', kwargs["' + fld + '"]'+', " should be of acceptable type(s) '+(" ".join(acceptabletypes))+'");\n'
        str += '        }\n'
        return str

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
                    str += "        if (xxx"+fld+" == null || xxx"+fld+".length <= 0 || Math."+k[0:3] +"(xxx"+fld+") " + v + " " + field.get(k) + ") {\n"
                    str += "            return undefined;\n\t}\n"
                else:
                    str += "        if (xxx"+fld+" == null || xxx"+fld+" " + v + " " + field.get(k) + ") {\n"
                    str += "            return undefined;\n\t}\n"
            
            except:
                pass

        try:
            if field.get('additionalEnumerationValuesAllowed') != "true":
                enumerations = field.iter("enumeration")
                efound = 0
                for enum in enumerations:
                    if efound == 0:
                        str += "        if (" + "'"+enum.get('value')+"'" + ' === xxx'+fld+') {\n'
                        efound = 1
                    else:
                        str += "        } else if (" + "'"+enum.get('value')+"'" + ' === xxx'+fld+') {\n'
                if efound == 1:
                    if enum.get('use') == 'required':
                        str +=     "        } else if (" + "'"+enum.get('use')+"'" +" === 'required') {\n"
                        str +=     "            console.error('"+field.get('name')+" required, but does not have legal value (undefined?)');\n"
                        str +=     "            return undefined;\n"
                    str +=     "        }\n"
        except KeyError:
            pass
#        if field.get('type') == 'SFVec2d':
#                    str += "        if (xxx"+fld+" == null || xxx"+fld+".length !== 2 ) {\n"
#                    str += "            return undefined;\n"
#                    str += "        }\n"
#        elif field.get('type') == 'SFVec2f':
#                    str += "        if (xxx"+fld+" == null || xxx"+fld+".length !== 2 ) {\n"
#                    str += "            return undefined;\n"
#                    str += "        }\n"
#        elif field.get('type') == 'SFVec3d':
#                    str += "        if (xxx"+fld+" == null || xxx"+fld+".length !== 3 ) {\n"
#                    str += "            return undefined;\n"
#                    str += "        }\n"
#        elif field.get('type') == 'SFVec3f':
#                    str += "        if (xxx"+fld+" == null || xxx"+fld+".length !== 3 ) {\n"
#                    str += "            return undefined;\n"
#                    str += "        }\n"
#        elif field.get('type') == 'SFColor':
#                    str += "        if (xxx"+fld+" == null || xxx"+fld+".length !== 3 ) {\n"
#                    str += "            return undefined;\n"
#                    str += "        }\n"
#        elif field.get('type') == 'SFRotation':
#                    str += "        if (xxx"+fld+" == null || xxx"+fld+".length !== 4 ) {\n"
#                    str += "            return undefined;\n"
#                    str += "        }\n"
#        elif field.get('type') == 'SFColorRGBA':
#                    str += "        if (xxx"+fld+" == null || xxx"+fld+".length !== 4 ) {\n"
#                    str += "            return undefined;\n"
#                    str += "        }\n"
#        elif field.get('type') == 'MFVec2d':
#                    str += "        if (xxx"+fld+" == null || xxx"+fld+".length % 2 !== 0 ) {\n"
#                    str += "            return undefined;\n"
#                    str += "        }\n"
#        elif field.get('type') == 'MFVec2f':
#                    str += "        if (xxx"+fld+" == null || xxx"+fld+".length % 2 !== 0 ) {\n"
#                    str += "            return undefined;\n"
#                    str += "        }\n"
#        elif field.get('type') == 'MFVec3d':
#                    str += "        if (xxx"+fld+" == null || xxx"+fld+".length % 3 !== 3 ) {\n"
#                    str += "            return undefined;\n"
#                    str += "        }\n"
#        elif field.get('type') == 'MFVec3f':
#                    str += "        if (xxx"+fld+" == null || xxx"+fld+".length % 3 !== 3 ) {\n"
#                    str += "            return undefined;\n"
#                    str += "        }\n"
        return str

    def setter(self, field, name):
        str = ""
        fld = self.getField(name)

        # this may be cheating, if there's a setter, there must be a property
        # str += '    get '+ fld + '() {\n'
        # str += '        return ' + self.private(fld) + ";\n\t}\n"

        if fld.startswith("SF") or fld.startswith("MF"):
            str += '    set ' + fld +'(value = ' + self.getDefault(field) +  ") {\n"
            str += self.settervalidate(field, "value")
            str += '        '+self.private(fld)+' = [value];\n\t}\n'

        if not name.startswith("add") and not name.startswith("remove"):
            if name.startswith('set'):
                functionName = self.getFunctionName(name)
            else:
                functionName = self.getFunctionName(name)
            str += '    set ' + functionName +'(' + fld +' = ' + self.getDefault(field) +  ") {\n"
            str += self.settervalidate(field, name)
            str += '        '+self.private(fld)+' = ['+fld+"];\n"
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

    def settergetter(self, field, name):
        str = ""
        str += self.setter(field, name)
        str += self.getter(field, name)
        return str

    def processField(self, field):
        name = field.get('name')
        name = re.sub(r"-", "_", name)
        name = re.sub(r":", "_", name)
        return name


    def setUpField(self, field, accessType):
        name = self.processField(field)
        return self.__choice_table[accessType](field, name)

    def setUpAloneField(self, fieldname, fieldtype, accessType):
        field = alone_field(fieldname, fieldtype)
        return self.setUpField(field, accessType)



    def printClass(self):
        str = ""
        if self.printed:
            return str
        for parent in self.parents:
            try:
                str += classes[parent].printClass()
            except:
                pass
        str += 'export class ' + self.name + self.metaInfo
        strjoin = ", ".join(self.parents)
        if strjoin != "" and not strjoin.startswith("xs:") and strjoin != "SFString":
            str += " extends "+strjoin
        elif self.name.startswith("MF"):
            str += " extends Array"
        str += " {\n"
        if self.name.startswith("SF"):
            str += "    constructor(value_ = null) {\n"
            str += "        this.__value = value_;\n"
        elif self.name.startswith("MF"):
            str += "    constructor(value_ = null) {\n"
            str += "        super(value_);\n"
            str += "        this.__value = value_;\n"
        else:
            str += "    constructor(kwargs = {}) {\n"
            
        if self.name == "X3D" or self.name == "meta" or self.name == "head":
            pass
        else:
            if strjoin != "" and not strjoin.startswith("xs:") and strjoin != "SFString":
                str += "        super(kwargs);\n"

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
        if self.name.startswith("MF"):
            str += "        for (let i in this.__value) {\n"
            str += "            if (typeof this.__value[i].toXMLNode === 'function') {\n"
            str += "                str += this.__value[i].toXMLNode(attrName);\n"
            str += "            } else {\n"
            str += "                str += this.__value;\n"
            str += "            }\n"
            str += "        }\n"
        elif self.name.startswith("SFNode"):
            str += "            if (typeof this.__value.toXMLNode === 'function') {\n"
            str += "                str += this.__value.toXMLNode(attrName);\n"
            str += "            }\n"
        elif self.name.startswith("SF"):
            str += "        if (typeof this.__value !== 'undefined') {\n"
            str += "            str += ' '+attrName+'='+'\"'+this.__value+'\"';\n"
            str += "        }\n"
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

        str += '}\n\n'
        self.printed = True
        return str
code = "// Do not modify\n"

soup = xml.etree.ElementTree.parse(open("c:/x3d-code/www.web3d.org/specifications/X3dUnifiedObjectModel-4.0.xml")).getroot()

classes = {}

fts = soup.iter("FieldType")
for ft in fts:
    classes[ft.get('type')] = ClassPrinter(ft, ft.get('type'), "")

sts = soup.iter("Statement")
for st in sts:
    classes[st.get('name')] = ClassPrinter(st, st.get('name'), "")

ants = soup.iter("AbstractNodeType")
for ant in ants:
    classes[ant.get('name')] = ClassPrinter(ant, ant.get('name'))

aots = soup.iter("AbstractObjectType")
for aot in aots:
    classes[aot.get('name')] = ClassPrinter(aot, aot.get('name'))

cns = soup.iter("ConcreteNode")
for cn in cns:
    classes[cn.get('name')] = ClassPrinter(cn, cn.get('name'), "")

for k,v in classes.items():
    code += v.printClass()

f = open("x3d.js", "w")
f.write(code)
f.close()
