"""
蔬菜信息管理系统 — 应用入口
=============================
基于PySide6 + SQLite3的四层分层架构桌面应用。
启动时自动初始化数据库、导入种子数据、执行关联规则挖掘。
"""

import sys
import os

# 确保当前目录在路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

from utils.db_manager import DBManager
from utils.password_utils import hash_password


def get_data_dir() -> str:
    """获取数据资源目录（SQL脚本、JSON、图片、数据库等）"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def init_database():
    """初始化数据库：建表 + 导入种子数据 + 创建测试账号"""
    data_dir = get_data_dir()

    # 1. 初始化数据库文件（存放在 data/ 目录下）
    db_path = os.path.join(data_dir, 'vegetable_db.db')
    DBManager.initialize(db_type='sqlite', db_path=db_path)
    print("[OK] 数据库连接已建立")

    # 2. 执行建表脚本
    init_sql = os.path.join(data_dir, 'init_db.sql')
    DBManager.init_db(init_sql)
    print("[OK] 数据库表已创建")

    # 2.5 数据库迁移：为旧数据库添加role列
    conn = DBManager.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE sys_user ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user'")
        print("[OK] 数据库迁移：已添加role列")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE veg_vegetable ADD COLUMN image_path VARCHAR(255)")
        print("[OK] 数据库迁移：已添加image_path列")
    except Exception:
        pass
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS veg_browse_history (
                history_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                veg_id      INTEGER NOT NULL,
                browse_time DATETIME NOT NULL DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (user_id) REFERENCES sys_user(user_id),
                FOREIGN KEY (veg_id) REFERENCES veg_vegetable(veg_id)
            )
        """)
        print("[OK] 数据库迁移：已创建浏览历史表")
    except Exception:
        pass
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS veg_cooking_method (
                method_id    INTEGER PRIMARY KEY AUTOINCREMENT,
                veg_id       INTEGER      NOT NULL,
                method_name  VARCHAR(50)  NOT NULL,
                cooking_time VARCHAR(50),
                ingredients  VARCHAR(200),
                create_time  DATETIME     NOT NULL DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (veg_id) REFERENCES veg_vegetable(veg_id) ON DELETE CASCADE
            )
        """)
        print("[OK] 数据库迁移：已创建烹饪方法表")
    except Exception:
        pass

    # 3. 导入种子蔬菜数据
    from dao.vegetable_dao import VegetableDAO
    from dao.user_dao import UserDAO
    from dao.recipe_dao import RecipeDAO

    veg_dao = VegetableDAO()
    if veg_dao.count() == 0:
        seed_sql = os.path.join(data_dir, 'seed_vegetables.sql')
        with open(seed_sql, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        # 按分号分割并执行INSERT语句（处理多行注释头）
        conn = DBManager.get_connection()
        cursor = conn.cursor()
        for part in sql_content.split(';'):
            part = part.strip()
            if 'INSERT' not in part.upper():
                continue
            # 从INSERT关键字开始截取SQL语句
            idx = part.upper().find('INSERT')
            stmt = part[idx:]
            try:
                cursor.execute(stmt)
            except Exception as e:
                print(f"  [WARN] 跳过重复数据: {str(e)[:60]}")
        conn.commit()
        print(f"[OK] 种子蔬菜数据已导入（共{veg_dao.count()}种蔬菜）")
    else:
        print(f"[OK] 蔬菜数据已存在（共{veg_dao.count()}种蔬菜）")

    # 4. 创建/修复测试账号（含角色）
    user_dao = UserDAO()
    conn = DBManager.get_connection()
    cursor = conn.cursor()

    if not user_dao.check_username_exists('test'):
        user_dao.create_user('test', hash_password('Test1234'), 'test@example.com', 'user')
        print("[OK] 测试账号 test / Test1234 已创建（普通用户）")
    else:
        cursor.execute("UPDATE sys_user SET role = 'user' WHERE username = 'test' AND role != 'user'")
        # 迁移旧密码到新密码
        cursor.execute("UPDATE sys_user SET password_hash = ? WHERE username = 'test'",
                       (hash_password('Test1234'),))
        print("[OK] 测试账号 test 密码已更新为 Test1234")

    if not user_dao.check_username_exists('admin'):
        user_dao.create_user('admin', hash_password('Admin1234'), 'admin@example.com', 'admin')
        print("[OK] 管理员账号 admin / Admin1234 已创建（管理员）")
    else:
        cursor.execute("UPDATE sys_user SET role = 'admin' WHERE username = 'admin' AND role != 'admin'")
        cursor.execute("UPDATE sys_user SET password_hash = ? WHERE username = 'admin'",
                       (hash_password('Admin1234'),))
        print("[OK] 管理员账号 admin 密码已更新为 Admin1234")

    conn.commit()

    # 5. 导入烹饪方法种子数据（如果表为空）
    try:
        cursor.execute("SELECT COUNT(*) as cnt FROM veg_cooking_method")
        cooking_count = cursor.fetchone()['cnt']
        if cooking_count == 0:
            seed_sql = os.path.join(data_dir, 'seed_vegetables.sql')
            with open(seed_sql, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            conn = DBManager.get_connection()
            cursor2 = conn.cursor()
            cooking_inserts = 0
            for part in sql_content.split(';'):
                part = part.strip()
                if 'INSERT' not in part.upper():
                    continue
                if 'veg_cooking_method' not in part.lower():
                    continue
                idx = part.upper().find('INSERT')
                stmt = part[idx:]
                try:
                    cursor2.execute(stmt)
                    cooking_inserts += 1
                except Exception as e:
                    print(f"  [WARN] 跳过重复烹饪方法: {str(e)[:60]}")
            conn.commit()
            print(f"[OK] 烹饪方法种子数据已导入（共{cooking_inserts}条）")
        else:
            print(f"[OK] 烹饪方法数据已存在（共{cooking_count}条）")
    except Exception as e:
        print(f"  [WARN] 烹饪方法表初始化: {str(e)[:60]}")

    # 6. 导入菜谱数据（如果尚未导入）
    recipe_dao = RecipeDAO()
    if recipe_dao.get_recipe_count() == 0:
        recipes_json = os.path.join(data_dir, 'recipes.json')
        count = recipe_dao.import_from_json(recipes_json)
        print(f"[OK] 菜谱数据已导入（共{count}条）")
    else:
        print(f"[OK] 菜谱数据已存在（共{recipe_dao.get_recipe_count()}条）")

    return db_path


def run_initial_mining():
    """系统首次运行时执行一次关联规则挖掘"""
    from dao.association_rule_dao import AssociationRuleDAO
    from service.mining_service import MiningService

    rule_dao = AssociationRuleDAO()
    if rule_dao.count() == 0:
        print("[INFO] 首次运行，执行初始关联规则挖掘...")
        mining_service = MiningService()
        count, msg = mining_service.generate_association_rules(
            min_support=0.01,
            min_confidence=0.1,
        )
        print(f"[OK] {msg}")
    else:
        print(f"[OK] 关联规则已存在（共{rule_dao.count()}条）")


def main():
    """应用主入口"""
    print("=" * 60)
    print("  蔬菜百科与推荐系统 - Vegetable Encyclopedia System")
    print("=" * 60)

    # 初始化数据库
    try:
        init_database()
        run_initial_mining()
    except Exception as e:
        print(f"[FATAL] 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 创建Qt应用
    app = QApplication(sys.argv)
    app.setApplicationName("蔬菜百科与推荐系统")

    # 设置应用图标（绘制蔬菜图标）
    from PySide6.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor
    from PySide6.QtCore import Qt, QRectF
    icon_pixmap = QPixmap(64, 64)
    icon_pixmap.fill(QColor(0, 0, 0, 0))  # 透明背景
    painter = QPainter(icon_pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    # 叶片
    painter.setBrush(QBrush(QColor("#4CAF50")))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(QRectF(8, 12, 28, 24))
    painter.drawEllipse(QRectF(28, 8, 28, 24))
    painter.drawEllipse(QRectF(20, 20, 24, 22))
    # 茎
    painter.setBrush(QBrush(QColor("#2E7D32")))
    painter.drawRoundedRect(QRectF(25, 38, 14, 20), 3, 3)
    painter.end()
    app.setWindowIcon(QIcon(icon_pixmap))
    app.setStyle('Fusion')  # 使用Fusion风格，跨平台一致

    # 设置全局浅色调色板，防止黑色背景
    from PySide6.QtGui import QPalette, QColor
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(245, 245, 245))
    palette.setColor(QPalette.WindowText, QColor(33, 33, 33))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(248, 248, 248))
    palette.setColor(QPalette.Text, QColor(33, 33, 33))
    palette.setColor(QPalette.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ButtonText, QColor(33, 33, 33))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Highlight, QColor(46, 125, 50))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 253, 231))
    palette.setColor(QPalette.ToolTipText, QColor(33, 33, 33))
    app.setPalette(palette)

    # 初始化服务层
    from service.user_service import UserService
    from service.search_service import SearchService
    from service.recommendation_service import RecommendationService
    from service.mining_service import MiningService
    from service.vegetable_service import VegetableService
    from service.collection_service import CollectionService
    from dao.user_dao import UserDAO
    from dao.user_dao import UserDAO
    from dao.recipe_dao import RecipeDAO
    from dao.association_rule_dao import AssociationRuleDAO
    from dao.browse_history_dao import BrowseHistoryDAO

    user_service = UserService()
    search_service = SearchService()
    recommendation_service = RecommendationService()
    mining_service = MiningService()
    vegetable_service = VegetableService()
    collection_service = CollectionService()
    recipe_dao = RecipeDAO()
    rule_dao = AssociationRuleDAO()
    user_dao = UserDAO()
    browse_history_dao = BrowseHistoryDAO()

    # 显示登录窗口
    from ui.login_window import LoginWindow
    login_dlg = LoginWindow(user_service)
    login_dlg.exec()

    # X关闭 → 退出应用；跳过 → 访客模式；登录成功 → 已登录
    if not login_dlg.login_success and not login_dlg.skip_mode:
        print("[INFO] 用户关闭登录窗口，退出应用")
        DBManager.close()
        sys.exit(0)

    print("[INFO] 启动主窗口...")

    # 创建并显示主窗口
    from ui.main_window import MainWindow
    main_window = MainWindow(
        search_service=search_service,
        recommendation_service=recommendation_service,
        user_service=user_service,
        collection_service=collection_service,
        vegetable_service=vegetable_service,
        mining_service=mining_service,
        recipe_dao=recipe_dao,
        association_rule_dao=rule_dao,
        user_dao=user_dao,
        browse_history_dao=browse_history_dao,
    )
    main_window.show()

    print("[READY] 应用已启动")

    # 进入事件循环
    exit_code = app.exec()

    # 清理资源
    DBManager.close()
    print("[INFO] 应用已退出")
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
