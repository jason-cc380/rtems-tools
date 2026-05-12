# RTEMS 6.2 AArch64 GDB 调试快速参考

## 加载 GDB 扩展

```bash
$ aarch64-rtems6-gdb your_application.exe
(gdb) source /path/to/tools/gdb/python/__init__.py
```

或者在 `.gdbinit` 中添加自动加载：
```
source /path/to/tools/gdb/python/__init__.py
```

## 核心调试命令

### 查看任务信息
```gdb
# 查看所有任务
(gdb) rtems task

# 查看特定任务（按索引）
(gdb) rtems task 1

# 查看多个任务
(gdb) rtems task 1 2 3
```

### 查看信号量
```gdb
(gdb) rtems semaphore [index]
```

### 查看消息队列
```gdb
(gdb) rtems mqueue [index]
```

### 查看定时器
```gdb
(gdb) rtems timer [index]
```

### 通过 ID 查看对象
```gdb
(gdb) rtems object <object_id>
```

## 多核系统调试 (SMP)

### 查看所有 CPU 状态
```gdb
(gdb) rtems cpu
```

输出示例：
```
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
```

### 查看特定 CPU
```gdb
(gdb) rtems cpu 0
```

## AArch64 架构特性

### 寄存器查看
当使用 `rtems task` 命令时，会自动显示 AArch64 的保存上下文：
- X19-X30（被调用者保存寄存器）
- SP（栈指针）

### 当前帧寄存器
```gdb
# 使用标准 GDB 命令查看当前寄存器
(gdb) info registers

# 或使用 GDB Python API（在脚本中）
import aarch64
regs = aarch64.register()
regs.show()
```

## 系统信息

### 查看时间
```gdb
(gdb) rtems tod
```

### 看门狗链
```gdb
# 看门狗 ticks 链
(gdb) rtems wdticks

# 看门狗 seconds 链
(gdb) rtems wdseconds
```

## 典型调试场景

### 场景 1: 任务卡死调试
```gdb
# 1. 查看所有任务状态
(gdb) rtems task

# 2. 查看特定任务详情
(gdb) rtems task <suspended_task_index>

# 3. 检查任务等待队列
# （在任务输出中查看 Wait info）

# 4. 查看 CPU 状态确认是否死锁
(gdb) rtems cpu
```

### 场景 2: 多核同步问题
```gdb
# 1. 查看所有 CPU 上运行的任务
(gdb) rtems cpu

# 2. 检查每个 CPU 的执行线程和继承线程

# 3. 查看相关信号量
(gdb) rtems semaphore <semaphore_index>

# 4. 检查信号量持有者和等待队列
```

### 场景 3: 内存/堆问题
```gdb
# 1. 查看区域（region）信息
(gdb) rtems regions <index>

# 2. 检查堆使用情况
# （在 region 输出中查看 Memory 部分）
```

## 自动化脚本示例

### GDB 脚本文件 (debug.gdb)
```gdb
# 自动加载 RTEMS 扩展
source /path/to/tools/gdb/python/__init__.py

# 连接目标
target remote localhost:1234

# 加载符号
file your_application.exe

# 自动显示系统状态
rtems cpu
rtems task
```

使用方式：
```bash
$ aarch64-rtems6-gdb -x debug.gdb
```

### Python 调试脚本
```python
# 在 GDB 中执行
import gdb
import sys
sys.path.append('/path/to/tools/gdb/python')

# 获取所有任务信息
gdb.execute('rtems task')

# 获取 CPU 信息
gdb.execute('rtems cpu')
```

## 故障排除

### 问题：命令未找到
**解决**: 确认已正确加载扩展
```gdb
(gdb) source /path/to/tools/gdb/python/__init__.py
```

### 问题：无法读取 CPU 信息
**解决**: 确认 RTEMS 已启用 SMP 支持，并且符号表已正确加载

### 问题：寄存器显示为空
**解决**: 确认目标已停止运行，并且 Context_Control 结构定义正确

## 高级技巧

### 结合标准 GDB 命令
```gdb
# 设置断点
(gdb) break _Thread_Switch

# 当切换发生时查看任务
(gdb) commands
> silent
> rtems cpu
> backtrace
> continue
> end
```

### 条件断点调试
```gdb
# 仅在特定任务切换时中断
(gdb) break _Thread_Switch if executing->Object.id == 0x01000001
```

## 参考资料

- RTEMS 6.2 文档：https://docs.rtems.org/
- GDB 文档：https://sourceware.org/gdb/documentation/
- AArch64 架构手册：ARM Architecture Reference Manual
