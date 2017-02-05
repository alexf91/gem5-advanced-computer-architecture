
from m5.params import *
from m5.SimObject import SimObject

class HelloObject(SimObject):

    type = 'HelloObject'
    cxx_header = "hpca_tutorial/hello_object.hh"
