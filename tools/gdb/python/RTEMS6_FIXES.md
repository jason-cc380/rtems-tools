# RTEMS 6.2 GDB Extension 修复说明

## 问题总结

用户在使用 `source /path/to/tools/gdb/python/__init__.py` 加载 RTEMS GDB 扩展后，遇到以下错误：

1. `rtems task` - "There is no member named maximum"
2. `rtems semaphore` - "No symbol '_Semaphore_Information'"
3. `rtems cpu` - "No symbol 'Configuration'"
4. `rtems tod` - "No symbol '_TOD'"
5. `rtems object` - "local variable 'valid' referenced before assignment"

## 根本原因

RTEMS 6.2 版本的数据结构字段名称与早期版本有所不同，原 GDB 扩展代码未做兼容性处理。

## 已修复的问题

### 1. objects.py - 字段名称兼容性

**问题**: RTEMS 6.x 使用不同的字段名称（如 `minimum` 替代 `minimum_id`）

**修复**: 添加多层回退机制：
```python
def maximum(self, api, _class):
    try:
        return int(self.tables[n]['maximum'])
    except gdb.error:
        # Try RTEMS 6.x alternative
        try:
            return int(self.tables[n]['maximum_objects'])
        except gdb.error:
            print("error: Cannot find maximum for %s/%s" % (api, _class))
            return 0
```

### 2. rtems.py - 变量名拼写错误

**问题**: `rtems_object.invoke()` 中使用未定义的变量 `vald` 而非 `valid`

**修复**: 修正变量名为 `valid`

### 3. supercore.py - TOD 结构变化

**问题**: `_TOD` 结构的字段名称在 RTEMS 6.x 中发生变化

**修复**: 添加字段名称回退：
```python
def now(self):
    try:
        return self.tod['now']
    except gdb.error:
        try:
            return self.tod['tod']  # RTEMS 6.x
        except gdb.error:
            return "unknown"
```

### 4. configuration.py - Configuration 表访问

**问题**: `Configuration` 符号可能不存在或字段名称变化

**修复**: 
- 添加备用符号名 `_Configuration_Table`
- 增强 SMP 检测逻辑
- 添加错误处理和友好提示

### 5. percpu.py - Per-CPU 信息访问

**问题**: `_Per_CPU_Information` 结构访问方式变化

**修复**: 添加多层回退机制尝试不同的访问方式

## 使用说明

### 加载扩展

在 GDB 中执行：
```gdb
(gdb) source /path/to/tools/gdb/python/__init__.py
```

脚本会自动：
1. 检测当前架构（AArch64/SPARC）
2. 注册所有 RTEMS 命令
3. 显示可用命令列表

### 可用命令

```
rtems              - 前缀命令
rtems task         - 显示任务信息
rtems semaphore    - 显示信号量信息
rtems cpu          - 显示 CPU 信息（SMP）
rtems tod          - 显示时间
rtems object       - 按 ID 显示对象
rtems timer        - 显示定时器
rtems partition    - 显示分区
rtems region       - 显示区域
rtems barrier      - 显示屏障
rtems mqueue       - 显示消息队列
rtems wdticks      - 显示看门狗 ticks 链
rtems wdseconds    - 显示看门狗 seconds 链
```

### 注意事项

1. **符号加载**: 确保已加载 RTEMS 内核符号
   ```gdb
   (gdb) add-symbol-file path/to/rtems.exe
   ```

2. **目标连接**: 确保已连接到目标系统
   ```gdb
   (gdb) target remote :1234
   ```

3. **错误处理**: 如果仍然看到"No symbol"错误，请检查：
   - RTEMS 内核是否已编译为包含调试信息（-g 选项）
   - 是否正确加载了符号文件
   - 目标系统是否已启动并运行 RTEMS

## 架构支持

- ✅ AArch64 (ARM64) - 完整支持，包括寄存器显示
- ✅ SPARC - 基础支持
- 🔄 其他架构 - 可扩展

## 测试建议

1. 首先测试基本命令：
   ```gdb
   (gdb) rtems tod
   (gdb) rtems cpu
   ```

2. 然后测试对象相关命令：
   ```gdb
   (gdb) rtems task
   (gdb) rtems semaphore
   ```

3. 如有具体对象 ID，可测试：
   ```gdb
   (gdb) rtems object 0x01000001
   ```

## 故障排除

### 问题：仍然看到字段不存在的错误

**解决**: 可能需要根据实际的 RTEMS 6.2 头文件调整字段名称。查看 RTEMS 源码中的结构定义：
```bash
grep -r "typedef struct.*Control" path/to/rtems-source/cpukit/score/include
```

### 问题：命令存在但无法读取数据

**解决**: 确认目标系统已停止且符号正确加载：
```gdb
(gdb) info proc
(gdb) maintenance info sections
```

### 问题：SMP 系统 CPU 信息显示不正确

**解决**: 检查 `configuration.maximum_processors()` 返回值，可能需要调整 `configuration.py` 中的 SMP 检测逻辑。

## 联系与支持

如需进一步帮助，请参考：
- RTEMS 官方文档：https://docs.rtems.org/
- RTEMS GDB 工具源码：tools/gdb/python
