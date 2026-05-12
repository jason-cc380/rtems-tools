# RTEMS GDB

GDB extensions to help accelerating RTEMS debugging.

**Supported Versions:** RTEMS 6.2+  
**Supported Architectures:** AArch64, SPARC

## Usage
 - Clone the git repo
 - Fire up gdb and use source command

```
$ aarch64-rtems6-gdb

GNU gdb (GDB) 13.x
Copyright (C) 2023 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.  Type "show copying"
and "show warranty" for details.
This GDB was configured as "--host=x86_64-linux-gnu --target=aarch64-rtems6".
For bug reporting instructions, please see:
<http://www.gnu.org/software/gdb/bugs/>.
(gdb) source path/to/clone/__init__.py
RTEMS GDB Support loaded
  Architecture support: AArch64, SPARC
  Available commands:
    rtems - Prefix command for all RTEMS commands
    rtems task - Display task information
    rtems semaphore - Display semaphore information
    rtems cpu - Display CPU information (SMP)
    rtems tod - Display time of day
    rtems object - Display object by ID
(gdb)
```

## Commands Implemented

### Core Commands
 - `rtems object <id>` : Prints RTEMS objects by ID
 - `rtems semaphore [index]` : Display semaphore(s) by index(es)
 - `rtems task [index]` : Display task(s) by index(es)
 - `rtems mqueue [index]` : Display message queue(s) by index(es)
 - `rtems timer [index]` : Display timer(s) by index(es)
 - `rtems partition [index]` : Display partition(s) by index(es)
 - `rtems regions [index]` : Display region(s) by index(es)
 - `rtems barrier [index]` : Display barrier(s) by index(es)

### System Commands
 - `rtems tod` : Display time of day
 - `rtems cpu [cpu_id]` : Display CPU information for SMP systems
   - Without arguments: shows all CPUs
   - With cpu_id: shows specific CPU information
 - `rtems wdticks` : Display watchdog ticks chain
 - `rtems wdseconds` : Display watchdog seconds chain

### Architecture-Specific Features

#### AArch64 Support
The AArch64 architecture module provides:
- Register display for all 31 general-purpose registers (X0-X30)
- Special register display (SP, PC, CPSR)
- CPSR flag interpretation (N, Z, C, V flags and Exception Level)
- Thread context inspection for saved callee-saved registers
- Auto-detection of AArch64 target architecture

Example usage:
```
(gdb) rtems task 1
         Id: 0x01000001 (@ 0x40001234)
       Name: Init
 Active CPU: 0
      State: ready
    Current: 1
       Real: 1
    Preempt: True
   T Budget: 0
       Time: 00:00:00.123456
  Resources: 0

Saved Context (callee-saved registers):
======================================================================
   x19: 0x0000000040001000
   x20: 0x0000000000000001
   ...
   x30: 0x0000000040002abc
     SP: 0x0000000040005000
```

## Multi-Core Debugging (SMP)

For RTEMS 6.2 on multi-core AArch64 systems, the following features are available:

### CPU Information
```
(gdb) rtems cpu
======================================================================
CPU Information (Total: 4 CPUs)
======================================================================

CPU 0:
  Executing thread: 0x40001234
  Heir thread:      0x40001234
  Executing ID:     0x01000001

CPU 1:
  Executing thread: 0x40002345
  Heir thread:      0x40002345
  Executing ID:     0x01000002
...
```

### Per-CPU Task Inspection
```
(gdb) rtems cpu 0
CPU 0 Information:
  Executing thread: 0x40001234
  Heir thread:      0x40001234
```

## Developer documentation
We have a document to get started with [pretty printer development](https://github.com/dbalan/rtems-gdb/wiki/Writing-a-pretty-printer).

## Integration Notes for RTEMS 6.2 AArch64

1. **Architecture Detection**: The GDB extension automatically detects the AArch64 architecture and enables appropriate register handling.

2. **Context Control**: The `aarch64.context` class handles parsing of `Context_Control` structures which contain callee-saved registers (X19-X30) and stack pointer for thread context switching.

3. **SMP Support**: Enhanced per-CPU data structures support multi-core debugging with CPU-specific thread information.

4. **Pretty Printers**: Register pretty printers are automatically applied when inspecting thread contexts.

