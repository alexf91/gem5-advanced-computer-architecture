import m5
from m5.objects import *

root = Root()
root.full_system = False

root.hello_jason = HelloObject()

m5.instantiate()

print "Beginnning to run the simulation"

exit_event = m5.simulate()

print "Exiting at tick %d because %s" % (m5.curTick(), exit_event.getCause())
