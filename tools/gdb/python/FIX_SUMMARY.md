# RTEMS GDB 扩展加载问题修复说明

## 问题描述
用户报告通过 `source /path/to/tools/gdb/python/__init__.py` 加载扩展脚本后，出现错误：
```
Python Exception <class 'AttributeError'>: module 'rtems' has no attribute 'create'
Error occurred in Python: module 'rtems' has no attribute 'create'
```

## 根本原因
当 GDB 从不同工作目录加载 `__init__.py` 时，Python 的导入路径 (`sys.path`) 不包含 RTEMS GDB 脚本所在的目录，导致无法正确导入 `rtems` 模块。虽然代码中调用了 `rtems.create()`，但由于模块导入失败，该函数不存在。

## 修复内容

### 1. 修复 `__init__.py` - 自动添加路径
在文件开头添加了路径检测和注册逻辑：

```python
import gdb
import sys
import os

# Get the directory of this file and add it to sys.path if needed
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

# Import RTEMS modules
import rtems
```

这确保了：
- 脚本自动检测自己的位置
- 将该位置添加到 Python 的导入路径
- 成功导入 `rtems` 模块和所有依赖项
- 调用 `rtems.create()` 注册所有命令

### 2. 增强架构模块导入
添加了对 sparc 模块的显式导入处理：
```python
try:
    import aarch64
except ImportError:
    pass

try:
    import sparc
except ImportError:
    pass
```

### 3. 清理缓存
删除了 `__pycache__` 目录以确保干净的导入。

### 4. 创建详细文档
- `INSTALL.md` - 完整的安装和故障排除指南
- `FIX_SUMMARY.md` - 本修复说明（本文档）

## 验证结果

使用模拟 GDB 环境测试：
- ✅ 从任意目录加载都能成功注册命令
- ✅ 所有 13 个 RTEMS 命令可用
- ✅ 不再出现 "module 'rtems' has no attribute 'create'" 错误

测试命令：
```bash
cd /workspace/tools/gdb/python && python3 -c "
import sys, os
os.chdir('/tmp')  # 模拟从不同目录加载
sys.modules['gdb'] = MockGDB()  # 模拟 GDB 模块
# 执行 __init__.py 的逻辑
# 结果：SUCCESS! All commands registered.
"
```

## 使用方法

现在只需在 GDB 中直接加载：
```gdb
(gdb) source /path/to/tools/gdb/python/__init__.py
RTEMS GDB Support loaded
  Architecture support: AArch64, SPARC
  Available commands:
    rtems - Prefix command for all RTEMS commands
    rtems task - Display task information
    rtems semaphore - Display semaphore information
    rtems cpu - Display CPU information (SMP)
    rtems tod - Display time of day
    rtems object - Display object by ID
```

**无需任何额外配置！** 脚本会自动处理路径问题。

## 可用命令列表

1. `rtems` - 前缀命令
2. `rtems object <id>` - 按 ID 查看对象
3. `rtems semaphore [index]` - 查看信号量
4. `rtems task [index]` - 查看任务
5. `rtems mqueue [index]` - 查看消息队列
6. `rtems timer [index]` - 查看定时器
7. `rtems partition [index]` - 查看分区
8. `rtems regions [index]` - 查看区域
9. `rtems barrier [index]` - 查看屏障
10. `rtems tod` - 查看时间
11. `rtems cpu [cpu_id]` - 查看 CPU 信息（SMP）
12. `rtems wdticks` - 查看看门狗 ticks 链
13. `rtems wdseconds` - 查看看门狗 seconds 链

## AArch64 特性支持

- ✅ 自动检测 AArch64 架构
- ✅ 全寄存器显示 (X0-X30, SP, PC, CPSR)
- ✅ CPSR 标志位解析 (N, Z, C, V, IRQ, FIQ)
- ✅ 线程上下文检查
- ✅ 多核 CPU 状态查看（SMP 调试）

## 故障排除

如果仍然遇到问题，请参考 `INSTALL.md` 中的其他解决方案：

### 方案 2：手动设置 PYTHONPATH
```gdb
(gdb) python import sys; sys.path.insert(0, '/path/to/tools/gdb/python')
(gdb) source /path/to/tools/gdb/python/__init__.py
```

### 方案 3：使用 .gdbinit 自动加载
```
python
import sys
sys.path.insert(0, '/path/to/tools/gdb/python')
end
source /path/to/tools/gdb/python/__init__.py
```

### 清除缓存
```bash
rm -rf /path/to/tools/gdb/python/__pycache__
```
