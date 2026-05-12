# RTEMS GDB Extension Installation Guide

## Problem: "module 'rtems' has no attribute 'create'"

This error occurs when GDB cannot properly find and import the `rtems` module. The issue is typically caused by Python's import path not including the directory where the RTEMS GDB scripts are located.

## Solution

### Option 1: Use the updated __init__.py (Recommended)

The `__init__.py` file has been updated to automatically add its directory to Python's import path. Simply source it in GDB:

```gdb
(gdb) source /path/to/tools/gdb/python/__init__.py
```

The script will now:
1. Automatically detect its location
2. Add that location to `sys.path`
3. Import the `rtems` module correctly
4. Register all RTEMS commands

### Option 2: Manually set PYTHONPATH in GDB

Before sourcing the init file, set the PYTHONPATH environment variable:

```gdb
(gdb) python import sys; sys.path.insert(0, '/path/to/tools/gdb/python')
(gdb) source /path/to/tools/gdb/python/__init__.py
```

Or set it in your shell before starting GDB:

```bash
export PYTHONPATH=/path/to/tools/gdb/python:$PYTHONPATH
gdb
(gdb) source /path/to/tools/gdb/python/__init__.py
```

### Option 3: Use .gdbinit for automatic loading

Add the following to your `~/.gdbinit` file:

```
python
import sys
sys.path.insert(0, '/path/to/tools/gdb/python')
end

source /path/to/tools/gdb/python/__init__.py
```

## Verification

After loading, verify the commands are available:

```gdb
(gdb) help rtems
Prefix command for RTEMS.

(gdb) info commands rtems
All commands matching pattern "rtems":
  rtems
  rtems barrier
  rtems cpu
  rtems mqueue
  rtems object
  rtems partition
  rtems regions
  rtems semaphore
  rtems task
  rtems timer
  rtems tod
  rtems wdticks
  rtems wdseconds
```

## Available Commands

- `rtems task [index]` - Display task information
- `rtems semaphore [index]` - Display semaphore information
- `rtems mqueue [index]` - Display message queue information
- `rtems timer [index]` - Display timer information
- `rtems partition [index]` - Display partition information
- `rtems region [index]` - Display region information
- `rtems barrier [index]` - Display barrier information
- `rtems tod` - Display time of day
- `rtems cpu [cpu_id]` - Display CPU information (SMP systems)
- `rtems object <id>` - Display object by ID
- `rtems wdticks` - Display watchdog ticks chain
- `rtems wdseconds` - Display watchdog seconds chain

## Architecture Support

The extension automatically detects and supports:
- AArch64 (ARM64)
- SPARC
- Additional architectures can be added by creating architecture-specific modules

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'gdb'"

This is expected when running outside of GDB. The scripts must be loaded within GDB's Python interpreter.

### Error: "ImportError: No module named 'rtems'"

The Python path does not include the directory containing the RTEMS scripts. Use one of the solutions above.

### Commands not appearing after source

1. Check for error messages during the source command
2. Verify the `rtems.create()` function is being called
3. Ensure all dependencies (objects.py, threads.py, etc.) are in the same directory
4. Clear Python cache: `rm -rf __pycache__`
