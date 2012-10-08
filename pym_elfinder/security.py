# -*- coding: utf-8 -*-

"""
Security module.

Contains several decorators to limit execution of commands.

Contains file access policy.

Contains name validation policy.
"""

###   class EntryExit(object):
###       def __init__(self, func, *args, **kw):
###           self._func = func
###           print("# Decorator __init__()")
###           print("# Type of func:", type(func))
###           print("# Types of my args:")
###           for a in args:
###               print("#   ", a, type(a))
###           print("# Types of my kw:")
###           for k, v in kw.items():
###               print("   ", k, v, type(v))
###   
###   
###       def __get__(self, instance, owner):
###           def wrapper(*args, **kw):
###               print("+ Function call")
###               print("+ Instance:", str(instance), type(instance))
###               print("+ Owner:", str(owner), type(owner))
###               print("Before", self._func.__name__)
###               print("+ Type of self:", type(self))
###               print("+ Types of my args:")
###               for a in args:
###                   print("+   ", a, type(a))
###               print("+ Types of my kw:")
###               for k, v in kw.items():
###                   print("+   ", k, v, type(v))
###               res = self._func(instance, *args, **kw)
###               print("After", self._func.__name__)
###               return res
###           return wrapper
###   
###   
###    def __call__(self, *args, **kw):
###        print("+ Function call")
###        print("Before", self._func.__name__)
###        print("+ Type of self:", type(self))
###        print("+ Types of my args:")
###        for a in args:
###            print("+   ", a, type(a))
###        print("+ Types of my kw:")
###        for k, v in kw.items():
###            print("+   ", k, v, type(v))
###        res = self._func(*args, **kw)
###        print("After", self._func.__name__)
###        return res

