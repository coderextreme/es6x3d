#  ECMAScript 6 library for X3D

Python programmers welcome!

packageGenerator.py generates ECMAscript package.

Run it like:
```
python packageGenerator.py
```

That python processs creates x3d.js and x3d.js is the ECMAScript 6 module

One sample app below.

Run it like:
```
node app.js

```
Currently XML generation is under test.  Contributions welcome.

Do not modify x3d.js
===============================================================================
Current implementation:

ES 6 class hierachy for X3D (not necessarily SAI).

setters/getters/add/remove
	Note:  This uses standard set and get for each attribute
	
toXMLNode
