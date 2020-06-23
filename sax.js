"use strict"
import fs from 'fs';

import { unit, LayerSet, X3D, head, IS, component, meta, Scene, WorldInfo, NavigationInfo, Background, SpotLight, PointLight, Viewpoint, Group, HAnimHumanoid, HAnimJoint,  HAnimSegment, HAnimSite, Transform, Shape, IndexedLineSet, Coordinate, Color, HAnimDisplacer, Appearance, Material, ImageTexture, TextureTransform, IndexedFaceSet, TextureCoordinate, TimeSensor, OrientationInterpolator, PositionInterpolator, ROUTE, ScalarInterpolator, field, Sphere, ProtoInterface, connect, ProtoBody, ProtoDeclare, Cylinder, fieldValue, ProtoInstance, Box  } from './x3d.js';
import classes from './classes.js';

function zapEmpty(root) {
	if (typeof root === 'boolean' || typeof root === 'string' || typeof root === 'number') {
		return root;
	}
	let ret = {};
	if (Array.isArray(root)) {
		ret = [];
	}
	for (let t in root) {
		let r = t;
		if (t.startsWith("@")) {
			r = t.substr(1);
		} else if (t.startsWith("__")) {
			r = t.substr(2);
		}
		if (classes[r] === 1) { // verify the tag is legal
			let clz = eval(r);  // get the right name (parent name)
			ret[r] = new clz(zapEmpty(root[t])); // instantiate class
			console.log("ZBuilt", r);
		} else {
			ret[r] = root[t];
			console.log("ZRecovery", r, t);
		}
	}
	for (let r in ret) {
		// https://stackoverflow.com/questions/679915/how-do-i-test-for-an-empty-javascript-object
		if (ret["__"+r] === null || ret[r] === null || (Object.keys(ret[r]).length === 0 && ret[r].constructor === Object)) {
			delete ret[r];
		}
	}
	return ret;
}

class JSONParser {
	constructor() {
	}
	parseJSON(json) {
	  	return this.onDocument(json);
	}
	onDocument(doc) {
		let x3d  = this.traverseDown("X3D", doc['X3D'], 1);
		return x3d;
	}
	onArray(elem, array, n) {
		// let attrs = [];
		let nodelist = [];
		for (let i in array) {
			nodelist[i] = this.parseEntity(i, array[i], n+1); // outside
			// nodelist[i] = array[i];
		}
		return nodelist;
	}
	processInstance(instance) {
		return instance;
	}
	traverseDown(k, json, n) {
		let nodelist = null;
		if (k.startsWith("__")) {
			k = k.substr(2);
		}
		let zjson = zapEmpty(json);
		if (classes[k] === 1) { // verify the tag is legal
			let clz = eval(k);  // get the right name (parent name)
			nodelist = new clz(zjson); // instantiate class
			console.log(nodelist, "TD. Build autmated", k, zjson);
		} else {
			console.log(nodelist, "TD. Failed build", zjson);
			nodelist = zjson;
		}
		return nodelist;
	}
	onObject(k, v, n) {
		let nodelist = {};
		for (let [i,d] of Object.entries(v)) {
			nodelist[i] = this.traverseDown(i, d, n+1);
			if (nodelist[i] === null) {
				nodelist[k] = this.onObject(k, v, n+1);
			}
		}
		return nodelist;
	}
	onString(str) {
		if (!typeof number === 'string') {
			throw "NaS";
		} else {
			return str;
		}
	}
	onNumber(num) {
		if (!typeof number === 'number') {
			throw "NaN";
		} else {
			return num;
		}
	}
	onBoolean(val) {
		if (!typeof number === 'boolean') {
			throw "NaB";
		} else {
			return val;
		}
	}
	onNull(value) {
		if (value !== null) {
			throw "NNu";
		} else {
			return null;
		}
	}

	parseEntity(prop, json, n) {
		let nodelist = {};
		let sample = "";
		if (typeof json === 'boolean') {
			sample = this.onBoolean(json);
		} else if (typeof json === 'string') {
			sample = this.onString(json);
		} else if (typeof json === 'number') {
			sample = this.onNumber(json);
		} else if (json === null) {
			sample = this.onNull(json);
		} else if (Array.isArray(json)) {
			nodelist[prop] = this.onArray(prop, json, n+1);
		} else if (typeof json === 'object') {
			nodelist[prop] = this.traverseDown(prop, json, n+1);
			if (nodelist[prop] === null) {
				nodelist[prop] = this.onObject(prop, json, n+1);
			}
		} else {
			console.log("HUH", prop, typeof prop, json, typeof json);
		}
		if (nodelist.keys().length > 0) {
		} else {
			nodelist[prop] = sample;
		}

		return nodelist[prop];
	}

}

var data = fs.readFileSync('Box.json');
var json = JSON.parse(data.toString());

var parser = new JSONParser();
var parsed = parser.parseJSON(zapEmpty(json));
console.log(JSON.stringify(json));
console.log(JSON.stringify(parsed));
console.log(parsed.toXMLNode());

	/*
let parser = new xml.SaxParser(function(cb) {
  cb.onStartDocument(function() {
  });
  cb.onEndDocument(function() {
  });
  cb.onStartElementNS(function(elem, attrs, prefix, uri, namespaces) {
  });
  cb.onEndElementNS(function(elem, prefix, uri) {
  });
  cb.onCharacters(function(chars) {
    if (chars.trim()) {
    	console.log(chars.trim());
    }
  });
  cb.onCdata(function(cdata) {
    console.log("<CDATA>" + cdata + "</CDATA>");
  });
  cb.onComment(function(msg) {
    console.log("<COMMENT>" + msg + "</COMMENT>");
  });
  cb.onWarning(function(msg) {
    console.log("<WARNING>" + msg + "</WARNING>");
  });
  cb.onError(function(msg) {
    console.log("<ERROR>" + JSON.stringify(msg) + "</ERROR>");
  });
});
 
//example read from chunks
parser.parseString(`
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE X3D PUBLIC "ISO//Web3D//DTD X3D 3.3//EN" "http://www.web3d.org/specifications/x3d-3.3.dtd">
<X3D  profile="Immersive" version="3.3" >
      <head>
        <meta name='title' content='Box.x3d'/>
        <meta name='creator' content='John Carlson'/>
        <meta name='generator' content='manual'/>
        <meta name='identifier' content='https://coderextreme.net/X3DJSONLD/box.x3d'/>
        <meta name='description' content='3 boxes'/>      
      </head>
    <Scene>
        <NavigationInfo type="&quot;EXAMINE&quot;"></NavigationInfo>
        <Viewpoint description="Cubes on Fire" position="0 0 12"></Viewpoint>
        <ProtoDeclare name="anyShape">
            <ProtoInterface>
                <field name="xtranslation" accessType="inputOutput" type="SFVec3f" value="0 0 0"></field>
                <field name="myShape" accessType="inputOutput" type="MFNode">
                    <Shape>
                        <Sphere containerField="geometry"></Sphere>
                        <Appearance containerField="appearance">
                            <Material containerField="material" diffuseColor="1 1 1"></Material>
                        </Appearance>
                    </Shape>
                </field>
            </ProtoInterface>
            <ProtoBody>
                <Transform>
                    <IS>
                        <connect nodeField="translation" protoField="xtranslation"></connect>
                        <connect nodeField="children" protoField="myShape"></connect>
                    </IS>
                </Transform>
            </ProtoBody>
        </ProtoDeclare>
        <ProtoDeclare name="three">
            <ProtoInterface>
                <field name="ytranslation" accessType="inputOutput" type="SFVec3f" value="0 0 0"></field>
                <field name="myShape" accessType="inputOutput" type="MFNode">
                    <Shape>
                        <Cylinder containerField="geometry"></Cylinder>
                        <Appearance containerField="appearance">
                            <Material containerField="material" diffuseColor="1 1 1"></Material>
                        </Appearance>
                    </Shape>
                </field>
            </ProtoInterface>
            <ProtoBody>
                <Transform>
                    <IS>
                        <connect nodeField="translation" protoField="ytranslation"></connect>
                    </IS>
                    <ProtoInstance name="anyShape">
                        <fieldValue name="xtranslation" value="0 0 0"></fieldValue>
                        <IS>
                            <connect nodeField="myShape" protoField="myShape"></connect>
                        </IS>
                    </ProtoInstance>
                    <ProtoInstance name="anyShape">
                        <fieldValue name="xtranslation" value="2 0 0"></fieldValue>
                        <IS>
                            <connect nodeField="myShape" protoField="myShape"></connect>
                        </IS>
                    </ProtoInstance>
                    <ProtoInstance name="anyShape">
                        <fieldValue name="xtranslation" value="-2 0 0"></fieldValue>
                        <IS>
                            <connect nodeField="myShape" protoField="myShape"></connect>
                        </IS>
                    </ProtoInstance>
                </Transform>
            </ProtoBody>
        </ProtoDeclare>
        <ProtoInstance name="three" DEF="threepi">
            <fieldValue name="ytranslation" value="0 0 0"></fieldValue>
            <fieldValue name="myShape">
                <Shape DEF="box">
                    <Box containerField="geometry" size="1 1 1"></Box>
                    <Appearance containerField="appearance">
                        <Material containerField="material" diffuseColor="0 1 0"></Material>
                    </Appearance>
                </Shape>
            </fieldValue>
        </ProtoInstance>
	<Transform translation="0 2 0">
		<Shape USE="box"/>
	</Transform>
    </Scene>
</X3D>
`);
*/
