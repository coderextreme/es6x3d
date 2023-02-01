"use strict"

import * as fs from 'fs';

import { X3D } from '../fromNodeX3d.js';
import { head, meta, Scene, Transform, Group, Material, Shape, Box, Appearance } from '../fromNodeX3d.js';
import { MFNode, SFString, SFColor, SFVec3f, SFRotation } from '../fromNodeX3d.js';

var x3d = new X3D({
	version : "4.0",
	profile: "Immersive",
	head : new head({
		meta : [
			new meta({
				name : "John W",
				content : "Carlson, I"
			}),
			new meta({
				name : "John A",
				content : "Carlson, II"
			}),
			new meta({
				name : "John R",
				content : "Carlson, III"
			})
		]
	}),
	Scene : new Scene({
		children : new MFNode([
			new Group({
				children : new MFNode([
					new Shape({
						appearance : new Appearance({
							material : new Material({
								diffuseColor : new SFColor([1, 0, 0])
							})
						}),
						geometry : new Box({})
					})
				])
			}),
			new Transform({
				translation : new SFVec3f([1, 2, 3]),
				scale: new SFVec3f([4, 5, 6]),
				rotation: new SFRotation([7, 8, 9, 3.14])
			})
		])
	})
});

console.log("Converted to XML", x3d.toXMLNode());
// console.log("Expanded", x3d.deepExpand().toXMLNode());

var data = fs.readFileSync('examples/Box.json');
var json = JSON.parse(data.toString());
var x = new X3D(json);
x.fromJSON(json["X3D"]);
console.log("Output XML from JSON", x.toXMLNode())
