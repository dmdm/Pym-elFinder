Some Notes
##########

Access Control
==============

Access control governs several aspects:

* Files/directories
* Mime types
* Commands
* Names

Settings for access control are given for each volume, so it must be implemented
in each driver, not in the finder.

Files/Directories
-----------------

Permissions: read, write, hidden, locked

* Permissions set directly on the object, e.g. read/write permission by the local
  file system

* ACL: A regular expression is applied to object's path and if it matches, the noted
  permissions are attached to the object

Commands
--------

Specific commands can be disabled: ``opts['disabled_cmds'] = [ ... ]``.

Names
-----

Checks that a given object name conforms to specific rules, e.g. contains only 
appropriate characters etc.





Misc
====

https://github.com/devopsni/django-bigmouth
