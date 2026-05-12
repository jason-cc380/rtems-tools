#
# RTEMS GDB Extensions
# AArch64 architecture specific abstractions for RTEMS 6.2
#

import gdb


class register:
    """AArch64 Registers for RTEMS 6.2"""

    def __init__(self, reg_frame=None):
        """
        Initialize with optional register frame from GDB.
        If reg_frame is None, registers will be fetched from current frame.
        """
        self.reg_frame = reg_frame
        self.regs = {}
        self._load_registers()

    def _load_registers(self):
        """Load all AArch64 general purpose and special registers."""
        # General purpose registers X0-X30
        for i in range(0, 31):
            reg_name = 'x%d' % i
            try:
                if self.reg_frame:
                    self.regs[reg_name] = self.reg_frame.read_register(reg_name)
                else:
                    self.regs[reg_name] = gdb.parse_and_eval('$' + reg_name)
            except:
                self.regs[reg_name] = None

        # Stack pointer
        try:
            if self.reg_frame:
                self.regs['sp'] = self.reg_frame.read_register('sp')
            else:
                self.regs['sp'] = gdb.parse_and_eval('$sp')
        except:
            self.regs['sp'] = None

        # Program counter
        try:
            if self.reg_frame:
                self.regs['pc'] = self.reg_frame.read_register('pc')
            else:
                self.regs['pc'] = gdb.parse_and_eval('$pc')
        except:
            self.regs['pc'] = None

        # Current Program Status Register
        try:
            if self.reg_frame:
                self.regs['cpsr'] = self.reg_frame.read_register('cpsr')
            else:
                self.regs['cpsr'] = gdb.parse_and_eval('$cpsr')
        except:
            self.regs['cpsr'] = None

        # Frame pointer (X29) and Link register (X30)
        self.regs['fp'] = self.regs.get('x29')
        self.regs['lr'] = self.regs.get('x30')

    def get(self, reg_name):
        """Get register value by name."""
        return self.regs.get(reg_name)

    def get_all(self):
        """Get all registers as dictionary."""
        return self.regs

    def show(self, show_all=False):
        """Display register values."""
        print("AArch64 Registers:")
        print("=" * 70)
        
        # Show general purpose registers
        print("\nGeneral Purpose Registers:")
        for i in range(0, 31):
            reg_name = 'x%d' % i
            val = self.regs.get(reg_name)
            if val is not None:
                print("  %4s: 0x%016x" % (reg_name, int(val)))
        
        # Show special registers
        print("\nSpecial Registers:")
        special_regs = ['sp', 'pc', 'cpsr', 'fp', 'lr']
        for reg_name in special_regs:
            val = self.regs.get(reg_name)
            if val is not None:
                print("  %4s: 0x%016x" % (reg_name, int(val)))
        
        # Show CPSR flags if available
        cpsr = self.regs.get('cpsr')
        if cpsr is not None:
            self._show_cpsr_flags(int(cpsr))

    def _show_cpsr_flags(self, cpsr):
        """Display CPSR flag bits."""
        flags = {
            'N': (cpsr >> 31) & 1,
            'Z': (cpsr >> 30) & 1,
            'C': (cpsr >> 29) & 1,
            'V': (cpsr >> 28) & 1,
        }
        print("\nCPSR Flags: N=%d Z=%d C=%d V=%d" % (
            flags['N'], flags['Z'], flags['C'], flags['V']))
        
        # Exception level
        el = (cpsr >> 2) & 3
        print("Exception Level: EL%d" % el)

    def to_string(self):
        """Return register dump as string."""
        lines = []
        lines.append("AArch64 Register Dump:")
        lines.append("=" * 70)
        
        # Format registers in groups of 4 per line
        for i in range(0, 31, 4):
            line = ""
            for j in range(4):
                reg_idx = i + j
                if reg_idx < 31:
                    reg_name = 'x%d' % reg_idx
                    val = self.regs.get(reg_name)
                    if val is not None:
                        line += "%4s: 0x%016x  " % (reg_name, int(val))
            lines.append(line)
        
        # Special registers
        lines.append("")
        lines.append("SP: 0x%016x  PC: 0x%016x  CPSR: 0x%016x" % (
            int(self.regs.get('sp', 0)),
            int(self.regs.get('pc', 0)),
            int(self.regs.get('cpsr', 0))))
        
        return '\n'.join(lines)


class context:
    """AArch64 Thread Context for RTEMS 6.2"""

    def __init__(self, context_ctrl):
        """
        Initialize with Thread_Control's Registers field.
        context_ctrl should be a gdb.Value of type Context_Control.
        """
        self.context = context_ctrl
        self.regs = {}
        self._parse_context()

    def _parse_context(self):
        """Parse the Context_Control structure."""
        try:
            # In RTEMS 6.2, Context_Control for AArch64 contains:
            # - General purpose registers x19-x30 (callee-saved)
            # - Stack pointer
            # Note: The exact structure may vary based on RTEMS configuration
            
            # Try to access register fields
            for i in range(19, 31):
                reg_name = 'x%d' % i
                try:
                    self.regs[reg_name] = int(self.context[reg_name])
                except:
                    # Try alternative field names
                    try:
                        self.regs[reg_name] = int(self.context['r%d' % i])
                    except:
                        self.regs[reg_name] = None
            
            # Stack pointer
            try:
                self.regs['sp'] = int(self.context['sp'])
            except:
                self.regs['sp'] = None
                
        except Exception as e:
            print("Warning: Could not parse context: %s" % str(e))

    def show(self):
        """Display saved context registers."""
        print("\nSaved Context (callee-saved registers):")
        print("=" * 70)
        
        for i in range(19, 31):
            reg_name = 'x%d' % i
            val = self.regs.get(reg_name)
            if val is not None:
                print("  %4s: 0x%016x" % (reg_name, val))
        
        sp = self.regs.get('sp')
        if sp is not None:
            print("  SP: 0x%016x" % sp)

    def get_sp(self):
        """Get stack pointer from context."""
        return self.regs.get('sp')

    def get_register(self, reg_name):
        """Get specific register from context."""
        return self.regs.get(reg_name)


def get_current_arch():
    """Get current architecture name from GDB."""
    frame = gdb.selected_frame()
    arch = frame.architecture()
    return arch.name()


def is_aarch64():
    """Check if current architecture is AArch64."""
    arch = get_current_arch()
    return 'aarch64' in arch.lower()


def create():
    """Create and return an AArch64 register object."""
    return register()
