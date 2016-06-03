#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dynamic configuration system for pwndbg, using GDB's built-in Parameter
mechanism.

To create a new pwndbg configuration point, create an instance of
``pwndbg.config.Parameter``.

Parameters should be declared in the module in which they are primarily
used, or in this module for general-purpose parameters.

All pwndbg Parameter types are accessible via property access on this
module, for example:

    >>> pwndbg.config.Parameter('example-value', 7, 'an example')
    >>> int(pwndbg.config.example_value)
    7
"""
import gdb
import sys
import types

TYPES = {
    # The value is an integer. 
    # This is like PARAM_INTEGER, except 0 is interpreted as itself.
    int: gdb.PARAM_ZINTEGER,
 
    # The value is a string. 
    # When the user modifies the string, any escape sequences, 
    # such as ‘\t’, ‘\f’, and octal escapes, are translated into 
    # corresponding characters and encoded into the current host charset.
    str: gdb.PARAM_STRING,

    # The value is a plain boolean. 
    # The Python boolean values, True and False are the only valid values.
    bool: gdb.PARAM_BOOLEAN
}

class Parameter(gdb.Parameter):

    def __init__(self, name, default, docstring):
        self.docstring = docstring.strip()
        self.name = name.replace('-','_')
        self.default = default
        self.set_doc   = 'Set ' + docstring
        self.show_doc  = docstring + ':'
        super(Parameter, self).__init__(name,
                                        gdb.COMMAND_SUPPORT,
                                        TYPES[type(default)])
        self.value = default

        setattr(module, self.name, self)

    def get_set_string(self):
        return 'Set %s to %r' % (self.docstring, self.value)
    def get_show_string(self, svalue):
        return 'Sets %s (currently: %r)' % (self.docstring, self.value)
    def __int__(self):
        return int(self.value)
    def __str__(self):
        return str(self.value)
    def __bool__(self):
        return bool(self.value)

class ConfigModule(types.ModuleType):
    def __init__(self, name, module):
        super(ConfigModule, self).__init__(name)
        self.__dict__.update(module.__dict__)
    Parameter = Parameter


# To prevent garbage collection
tether = sys.modules[__name__]

# Create the module structure
module = ConfigModule(__name__, tether)
sys.modules[__name__] = module