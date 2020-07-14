"use strict"

import fs from 'fs'

import { meta, head, Scene, X3D,  Transform, Group, Material, Shape, Box, Appearance } from './x3d.js';
import { MFNode, SFColor, SFVec3f, SFString, SFNode, SFRotation } from './x3d.js';


let x3d = new X3D({
	version: new SFString("4.0"),
	profile: new SFString("Immersive"),
	head : new SFNode(new head({
		meta : new MFNode([
			new meta({
				name : new SFString("John W"),
				content : new SFString("Carlson, I")
			}),
			new meta({
				name : new SFString("John A"),
				content : new SFString("Carlson, II")
			}),
			new meta({
				name : new SFString("John R"),
				content : new SFString("Carlson, III")
			})
		])
	})),
	Scene : new SFNode(new Scene({
		children : new MFNode([
			new Shape({
				appearance : new SFNode(new Appearance({
					material : new SFNode(new Material({
						diffuseColor : new SFColor([1, 0, 0])
					}))
				})),
				geometry : new SFNode(new Box({}))
			}),
			new Transform({
				translation : new SFVec3f([1, 2, 3]),
				scale: new SFVec3f([4, 5, 6]),
				rotation: new SFRotation([7, 8, 9, 3.14])
			})
		])
	}))
});

// console.log(JSON.stringify(x3d, null, 2));
console.log(x3d.toXMLNode());
