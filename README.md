# 3dmodel

一个支持AI驱动的3D模型创建和操作工具。

## 功能特性

- 🤖 AI驱动的3D模型生成
- 💬 **多轮对话式交互界面**
- 🎯 支持多种3D几何体（立方体、圆柱体、半圆柱体、NACA4翼型）
- 🔧 3D模型变换操作（平移、旋转、缩放）
- 🎨 高质量3D渲染和可视化
- ⚡ 强大的布尔运算支持
- 📁 多种3D文件格式导出
- 🔄 **实时模型更新和显示管理**

## 渲染后端

### Trimesh Backend (推荐)
- **文件**: `backend_trimesh.py`
- **优势**:
  - ✅ 完整的布尔运算支持（并集、交集、差集）
  - ✅ 精确的3D几何体表示
  - ✅ 支持多种3D文件格式导出（STL、OBJ、PLY等）
  - ✅ 专业级3D几何处理性能
  - ✅ 网格分析和修复功能
  - ✅ 更好的3D可视化效果
  - ✅ **支持显示窗口管理和关闭**

### Matplotlib Backend (已废弃)
- **文件**: `backend_matplot_deprecated.py`
- **问题**:
  - ❌ 布尔运算支持有限
  - ❌ 3D几何表示不够精确
  - ❌ 性能和可视化质量较低

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### CLI 多轮对话模式（推荐）

使用CLI前端进行多轮对话式模型生成和修正：

```bash
# 方式1：使用独立CLI脚本
python cli.py

# 方式2：使用agent.py的CLI模式
python agent.py cli
```

**CLI功能特性：**
- 🔄 多轮对话支持，可以基于历史对话不断修正模型
- 📝 智能缓存机制，基于对话历史创建缓存
- 🎨 自动关闭上一轮渲染，显示新的模型
- 📊 对话历史查看和管理
- 🧹 清除当前模型和对话历史功能

**CLI命令：**
- `quit` 或 `exit`：退出程序
- `history` 或 `历史`：查看对话历史
- `clear` 或 `清除`：清除当前模型和对话历史，开始新对话

### 基本编程接口

```python
from agent import Agent, gen_tool
from backend_trimesh import BackendTrimesh

# 创建agent和后端
agent = Agent(tools=gen_tool())
backend = BackendTrimesh("trimesh")
agent.set_backend(backend)

# 生成3D模型
user_input = "创建一个立方体和圆柱体"
models, operations = agent.input(user_input)

# 变换和渲染模型
transformed_models = backend.transform(models, operations)
backend.render(transformed_models)

# 多轮对话示例
# 第一轮
models1, ops1 = agent.input("创建一个NACA4翼型")
transformed_models1 = backend.transform(models1, ops1)
backend.render(transformed_models1)

# 关闭当前渲染，准备下一轮
backend.close_display()

# 第二轮 - 基于历史对话修正
models2, ops2 = agent.input("将翼型放大1.5倍", use_conversation_cache=True)
transformed_models2 = backend.transform(models2, ops2)
backend.render(transformed_models2)
```

### 运行示例

查看基本使用示例：
```bash
python examples/basic_trimesh_example.py
```

查看完整演示（需要openai库）：
```bash
python examples/demo_trimesh.py
```

**新增CLI示例使用：**
```bash
# 启动CLI进行多轮对话
python cli.py

# 示例对话流程：
# [第1轮] 请输入您的需求: 创建一个机翼模型，使用3个NACA4翼型
# [第2轮] 请输入您的需求: 将翼型间距增加到20%，并调整翼型弯度
# [第3轮] 请输入您的需求: 给机翼添加一个向上的倾斜角度
```

### 运行测试

运行所有测试：
```bash
python tests/run_tests.py
```

运行特定测试：
```bash
python tests/run_tests.py --test backend_trimesh
```

查看可用测试：
```bash
python tests/run_tests.py --list
```

## 支持的3D模型类型

- **立方体 (Cube)**: 可定制尺寸和方向的长方体
- **圆柱体 (Cylinder)**: 支持椭圆截面的圆柱体
- **半圆柱体 (Half Cylinder)**: 半圆截面的圆柱体

## 支持的操作

- **刚体变换**: 平移、旋转、缩放
- **布尔运算**: 并集、交集、差集（仅Trimesh后端）

## 文件导出

Trimesh后端支持导出到多种3D文件格式：
- STL (适用于3D打印)
- OBJ (通用3D格式)
- PLY (点云格式)
- 等更多格式

## 项目结构

```
├── agent.py                      # 主Agent类
├── backend_trimesh.py            # Trimesh渲染后端
├── backend_matplot_deprecated.py # 已废弃的Matplotlib后端
├── models.py                     # 3D模型定义
├── operations.py                 # 3D操作定义
├── requirements.txt              # 依赖包列表
├── README.md                     # 项目说明
├── tests/                        # 测试目录
│   ├── __init__.py              # 测试包初始化
│   ├── run_tests.py             # 测试运行器
│   └── test_backend_trimesh.py  # Trimesh后端测试
└── examples/                     # 示例目录
    ├── __init__.py              # 示例包初始化
    ├── basic_trimesh_example.py # 基本使用示例
    └── demo_trimesh.py          # 完整功能演示
```

## 更新日志

### v2.0 - Trimesh Backend
- ✨ 新增Trimesh渲染后端
- ✨ 支持完整的布尔运算
- ✨ 新增文件导出功能
- 🗑️ 废弃Matplotlib后端
- 📈 大幅提升3D处理性能和质量