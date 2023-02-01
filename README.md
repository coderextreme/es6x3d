#  ECMAScript 6 library for X3D

Python programmers welcome!

packageGenerator.py generates ECMAscript package.

Run it like:
```
python packageGenerator.py
```

That python processs creates x3d.mjs and x3d.mjs is the ECMAScript 6 module

One sample app below.

Run it like:
```
node examples/app.js

```
Currently XML generation is under test.  Contributions welcome.

To run a full build an test, run

```
ant
```

This requires ant, python3, npm.cmd, and node (or nodejs)

Do not modify x3d.js
===============================================================================
Current implementation:

ES 6 class hierachy for X3D (not necessarily SAI).

setters/getters/add/remove
	Note:  This uses standard set and get for each attribute
	
toXMLNode
