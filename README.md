# 🥬 蔬菜百科与推荐系统

面向普通消费者的蔬菜百科桌面应用，支持百科查询、浏览榜单、智能推荐、收藏管理。

## 快速开始

```bash
pip install -r requirements.txt
python main.py
```

首次运行自动建库、导入58种蔬菜和118条菜谱，并执行关联规则挖掘。

## 测试账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 普通用户 | `test` | `Test1234` |
| 管理员 | `admin` | `Admin1234` |

## 主要功能

- **百科查询** — 分类浏览、模糊搜索、热门榜单、性价比排行、蔬菜详情（营养/选购/储存/烹饪推荐）
- **智能推荐** — 时令蔬菜（按月自动匹配）、关联推荐（Apriori算法，最多5条）
- **用户中心** — 注册/登录（bcrypt加密）、多收藏夹、自定义清单、浏览历史、访客模式
- **后台管理** — 蔬菜CRUD、菜谱导入、关联规则挖掘、用户管理、系统重置

## 项目结构

```
code/
├── main.py               # 入口
├── entity/                # 实体层 — 7个 @dataclass 数据类
├── dao/                   # 数据访问层 — BaseDAO + 8个子类
├── service/               # 业务逻辑层 — 6个服务类
├── ui/                    # 表示层 — 7个 PySide6 窗口
├── utils/                 # 工具层 — DBManager(单例)/bcrypt/图片
├── data/                  # SQL脚本、种子数据、菜谱JSON、蔬菜图片
├── tests/                 # 测试 — 184个用例、6个测试文件
└── docs/                  # 设计文档、PlantUML图、可视化图
```

## 技术栈

Python · PySide6 · SQLite3 · pandas · mlxtend (Apriori) · bcrypt

## 运行测试

```bash
pytest tests/ -v
```
