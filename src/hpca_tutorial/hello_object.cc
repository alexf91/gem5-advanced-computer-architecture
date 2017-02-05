#include "hpca_tutorial/hello_object.hh"

#include "debug/Hello.hh"

HelloObject::HelloObject(HelloObjectParams *params) : SimObject(params)
{
    DPRINTF(Hello, "hello world from sim objecti %d\n", 10);
}

HelloObject *
HelloObjectParams::create()
{
    return new HelloObject(this);
}
