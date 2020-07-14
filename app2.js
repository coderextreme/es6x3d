"use strict"

import { X3D, head, meta, Scene, Transform, Group, Material, Shape, Box, Appearance,
MFNode, SFBool, SFNode, SFString, SFColor, SFVec3f, SFRotation } from './x3d.js';

let x3d = new X3D({
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
			new Group({
				children : new MFNode([
					new Shape({
						appearance : new SFNode(new Appearance({
							material : new SFNode(new Material({
							}))
						})),
						geometry : new SFNode(new Box({}))
					})
				])
			})
		])
	})),
	"xmlns:xsi":new SFString("http://www.w3.org/2001/XMLSchema-instance"),
	"xsi:nonamespaceschemalocation":new SFString("http://www.web3d.org/specifications/x3d-3.3.xsd"),
	width:new SFString("940px"),
	height:new SFString("940px"),
	showLog:new SFBool( true)
})

console.log(x3d.toXMLNode());
export default x3d;
