# 3dmodel

一个支持AI驱动的3D模型创建和操作工具。

## 功能特性

- 🤖 AI驱动的3D模型生成
- 🎯 支持多种3D几何体（立方体、圆柱体、半圆柱体）
- 🔧 3D模型变换操作（平移、旋转、缩放）
- 🎨 高质量3D渲染和可视化
- ⚡ 强大的布尔运算支持
- 📁 多种3D文件格式导出

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

### 基本使用

```python
from agent import Agent, gen_tool
from backend_trimesh import BackendTrimesh

# 创建agent
agent = Agent(tools=gen_tool())

# 生成3D模型
user_input = "创建一个立方体和圆柱体"
models, operations = agent.input(user_input)

# 使用Trimesh后端渲染
backend = BackendTrimesh("trimesh")
transformed_models = backend.transform(models, operations)
backend.render(transformed_models)
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