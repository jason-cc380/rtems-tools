#
# RTEMS GDB Extensions
#
# main

import gdb
import pretty
import rtems

gdb.pretty_printers = []
gdb.pretty_printers.append(pretty.lookup_function)

# Register commands
# rtems and subcommands
rtems.rtems()
rtems.rtems_object()
rtems.rtems_semaphore()
rtems.rtems_task()
rtems.rtems_message_queue()
rtems.rtems_tod()
rtems.rtems_cpu()
rtems.rtems_wdt()
rtems.rtems_wsec()

# Register architecture-specific commands
try:
    import aarch64
    print('  AArch64 support enabled')
except ImportError:
    pass