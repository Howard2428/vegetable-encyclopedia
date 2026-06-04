# 🥬 蔬菜百科与推荐系统

面向普通消费者的垂直领域蔬菜百科与智能推荐桌面应用。

## 技术栈

| 层级 | 技术 |
|------|------|
| UI框架 | PySide6（桌面GUI） |
| 业务逻辑 | 纯Python，四层分层架构 |
| 数据库 | SQLite 3（默认）/ MySQL 8.0 |
| 数据挖掘 | pandas + mlxtend（Apriori关联规则） |
| 密码加密 | bcrypt |

## 项目结构

```
code/
├── entity/                    # 实体层 — 纯数据类
│   ├── vegetable.py           # 蔬菜实体
│   ├── user.py                # 用户实体
│   ├── favorites_list.py      # 收藏夹实体
│   ├── custom_list.py         # 自定义清单实体
│   ├── association_rule.py    # 关联规则实体
│   ├── recipe.py              # 菜谱实体
│   └── cooking_method.py      # 烹饪方法实体
├── dao/                       # 数据访问层
│   ├── base_dao.py            # 基础DAO
│   ├── vegetable_dao.py       # 蔬菜CRUD+搜索+排行
│   ├── user_dao.py            # 用户注册/登录/管理
│   ├── favorites_dao.py       # 收藏夹操作
│   ├── custom_list_dao.py     # 自定义清单操作
│   ├── association_rule_dao.py# 关联规则读写
│   ├── recipe_dao.py          # 菜谱数据存取
│   ├── browse_history_dao.py  # 浏览历史
│   └── cooking_method_dao.py  # 烹饪方法CRUD
├── service/                   # 业务逻辑层
│   ├── user_service.py        # 用户认证+管理
│   ├── search_service.py      # 搜索+筛选+排行
│   ├── recommendation_service.py # 时令推荐+关联推荐
│   ├── mining_service.py      # Apriori关联规则挖掘
│   ├── vegetable_service.py   # 蔬菜信息管理
│   └── collection_service.py  # 收藏+清单管理
├── ui/                        # 表示层（PySide6）
│   ├── main_window.py         # 主窗口
│   ├── vegetable_detail_window.py  # 蔬菜详情
│   ├── login_window.py        # 登录窗口
│   ├── register_window.py     # 注册窗口
│   ├── user_center_window.py  # 个人中心
│   ├── admin_window.py        # 后台管理
│   ├── mining_progress_dialog.py   # 挖掘进度
│   └── styles.py              # 全局样式
├── utils/                     # 工具层
│   ├── db_manager.py          # 数据库连接管理（单例）
│   ├── password_utils.py      # bcrypt密码加密
│   └── image_utils.py         # 图片加载
├── data/                      # 数据文件
│   ├── init_db.sql            # 建表脚本（9张表）
│   ├── seed_vegetables.sql    # 58种蔬菜初始数据
│   ├── recipes.json           # 118条菜谱数据
│   └── images/                # 蔬菜图片
├── main.py                    # 应用入口
├── requirements.txt           # Python依赖
└── README.md                  # 本文件
```

## 环境配置

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行
```bash
python main.py
```

首次运行自动：建库 → 导入58种蔬菜 → 导入118条菜谱 → Apriori挖掘 → 创建测试账号。

## 测试账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 普通用户 | test | Test1234 |
| 管理员 | admin | Admin1234 |

## 功能清单

### 已实现（Must Have + Should Have + 部分Could Have）

| 功能 | 状态 |
|------|------|
| 蔬菜分类浏览（6大品类） | ✅ |
| 蔬菜详情（营养、选购、储存、烹饪推荐、价格） | ✅ |
| 模糊搜索（名称+别名，不区分大小写） | ✅ |
| 热门榜单Top10（浏览+收藏排序） | ✅ |
| 用户注册/登录（bcrypt加密） | ✅ |
| 多收藏夹管理（增删查） | ✅ |
| 自定义清单管理（上限50种） | ✅ |
| 智能推荐（Apriori关联规则，最多5条） | ✅ |
| 时令推荐（按系统月份自动匹配） | ✅ |
| 后台管理（蔬菜CRUD、菜谱导入、规则挖掘） | ✅ |
| 浏览量/收藏量统计 | ✅ |
| 浏览历史（最近20条） | ✅ |
| 图片展示（自动按名称匹配） | ✅ |
| 用户管理（查看、重置密码） | ✅ |
| 系统重置（清统计、清规则、清用户） | ✅ |
| 密码强度检测（弱密码提醒修改） | ✅ |
| 详情页内跳转（非新开窗口） | ✅ |
| 密码显示/隐藏切换 | ✅ |

## 强制业务规则

| 规则 | 实现 |
|------|------|
| BR-01 搜索模糊匹配名称+别名 | LIKE不区分大小写，四级相关度排序 |
| BR-02 时令蔬菜按月匹配 | datetime.now().month → 季节映射 |
| BR-03 关联推荐≤5条，按置信度降序 | LIMIT 5, ORDER BY confidence DESC |
| BR-04 收藏/清单需登录 | 所有操作前检查is_logged_in |
| BR-05 清单不重名+上限50 | check_name_duplicate + count_items |
| BR-06 浏览/收藏实时更新 | increment_view_count/favorite_count |
| BR-07 挖掘先清空旧规则 | clear_all → batch_insert |
| BR-08 密码加密存储 | bcrypt hash，禁止明文 |
