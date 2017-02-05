#ifndef __HPCA_TUTORIAL_HELLO_OBJECT_HH__
#define __HPCA_TUTORIAL_HELLO_OBJECT_HH__

#include "params/HelloObject.hh"
#include "sim/sim_object.hh"

class HelloObject : public SimObject
{
  public:
    HelloObject(HelloObjectParams *params);
};

#endif
