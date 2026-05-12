# RTEMS Tools Project (http://www.rtems.org/)
# Copyright 2014 Chris Johns (chrisj@rtems.org)
# All rights reserved.
#
# This file is part of the RTEMS Tools package in 'rtems-tools'.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

#
# RTEMS Per CPU Table
#

import gdb

import configuration


def _table(cpu):
    max_cpus = configuration.maximum_processors()
    if cpu >= max_cpus:
        raise IndexError('cpu index out of range (%d)' % (max_cpus))
    try:
        # Try RTEMS 6.x structure
        return gdb.parse_and_eval('_Per_CPU_Information[%d].per_cpu' % (cpu))
    except gdb.error:
        # Try alternative for RTEMS 6.x
        try:
            return gdb.parse_and_eval('_Per_CPU_Information[%d]' % (cpu))
        except gdb.error:
            # Fallback to direct array access
            return gdb.parse_and_eval('_Per_CPU_Information[%d]' % (cpu))


def get(cpu):
    return _table(cpu)


def thread_active(thread):
    for cpu in range(0, configuration.maximum_processors()):
        if thread == _table(cpu)['executing']:
            return cpu
    return -1


def thread_heir(thread):
    for cpu in range(0, configuration.maximum_processors()):
        if thread == _table(cpu)['heir']:
            return cpu
    return -1


def get_current_cpu():
    """Get the current CPU ID for SMP systems."""
    try:
        # Try to get current CPU from Per_CPU_Information
        return gdb.parse_and_eval('_Per_CPU_Get_index()')
    except:
        return 0


def show_all_cpus():
    """Display information about all CPUs in the system."""
    max_cpus = configuration.maximum_processors()
    print("=" * 70)
    print("CPU Information (Total: %d CPUs)" % max_cpus)
    print("=" * 70)
    
    for cpu_id in range(0, max_cpus):
        try:
            per_cpu = _table(cpu_id)
            executing = per_cpu['executing']
            heir = per_cpu['heir']
            
            print("\nCPU %d:" % cpu_id)
            print("  Executing thread: 0x%x" % int(executing))
            print("  Heir thread:      0x%x" % int(heir))
            
            # Try to get more details if threads are available
            if int(executing) != 0:
                try:
                    exec_ctrl = executing.dereference()
                    obj_ctrl = exec_ctrl['Object']
                    obj_id = obj_ctrl['id']
                    print("  Executing ID:     0x%08x" % int(obj_id))
                except:
                    pass
                    
        except Exception as e:
            print("\nCPU %d: Error reading information - %s" % (cpu_id, str(e)))
    
    print("=" * 70)
