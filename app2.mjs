"use strict"

import { X3D } from './x3d.mjs';
import { head, meta, Scene, Transform, Group, Material, Shape, Box, Appearance } from './x3d.mjs';
import { MFNode, SFColor, SFVec3f, SFRotation } from './x3d.mjs';

var x3d = new X3D({
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
							})
						}),
						geometry : new Box({})
					})
				])
			})
		])
	}),
	"xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance",
	"xsi:nonamespaceschemalocation":"http://www.web3d.org/specifications/x3d-3.3.xsd" ,
	width:"940px",
	height:"940px",
	showLog : true
})

console.log(x3d.toXMLNode());
export default x3d;
