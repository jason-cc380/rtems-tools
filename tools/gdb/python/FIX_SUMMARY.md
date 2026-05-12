# RTEMS GDB 扩展加载问题修复说明

## 问题描述
用户报告通过 `source /path/to/tools/gdb/python/__init__.py` 加载扩展脚本后，GDB 中没有显示 rtems 相关指令。

## 根本原因
`__init__.py` 文件中缺少对 `rtems.create()` 函数的调用，导致虽然模块被导入，但所有 GDB 命令没有被实际注册到 GDB 中。

## 修复内容

### 1. 修复 `__init__.py`
在 `__init__.py` 文件末尾添加了：
- 调用 `rtems.create()` 来初始化并注册所有 RTEMS GDB 命令
- 详细的命令列表输出，帮助用户了解可用的命令

### 2. 修复 `rtems.py` 的 `create()` 函数
更新了 `create()` 函数返回值，确保所有已定义的命令类都被实例化：
- `rtems_timer()` - 定时器命令
- `rtems_partition()` - 分区命令  
- `rtems_region()` - 区域命令
- `rtems_barrier()` - 屏障命令
- `rtems_cpu()` - CPU 信息命令（SMP 调试）

### 3. 更新文档
- 更新 `README.md` 中的示例输出，显示完整的命令列表
- 保留 `QUICKSTART_AARCH64.md` 中文快速参考指南

### 4. 添加测试脚本
创建 `test_extension.py` 用于验证扩展加载是否正确。

## 验证结果
运行测试脚本确认：
```
✓ Created 13 commands
✓ All 13 commands created successfully!
✓ aarch64 module imported successfully
```

## 使用方法
在 GDB 中加载扩展：
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

## AArch64 特性
- 自动检测 AArch64 架构
- 支持寄存器显示（X0-X30, SP, PC, CPSR）
- CPSR 标志位解析
- 线程上下文检查
- 多核 CPU 状态查看
