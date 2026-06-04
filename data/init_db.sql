-- ============================================================
-- 蔬菜信息管理系统 — 数据库初始化脚本
-- 兼容 SQLite 3 和 MySQL 8.0
-- ============================================================

-- 表1：用户表
CREATE TABLE IF NOT EXISTS sys_user (
    user_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    username        VARCHAR(50)  NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    email           VARCHAR(100) UNIQUE,
    role            VARCHAR(20)  NOT NULL DEFAULT 'user',
    register_time   DATETIME     NOT NULL DEFAULT (datetime('now', 'localtime')),
    last_login_time DATETIME
);

-- 表2：蔬菜信息表
CREATE TABLE IF NOT EXISTS veg_vegetable (
    veg_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    veg_name       VARCHAR(50)  NOT NULL UNIQUE,
    alias          VARCHAR(200),
    category       VARCHAR(30)  NOT NULL,
    season         VARCHAR(30)  NOT NULL,
    nutrition      TEXT,
    purchase_tips  TEXT,
    storage_method TEXT,
    image_path     VARCHAR(255),
    price_ref      DECIMAL(10,2),
    view_count     INTEGER      DEFAULT 0,
    favorite_count INTEGER      DEFAULT 0,
    create_time    DATETIME     NOT NULL DEFAULT (datetime('now', 'localtime')),
    update_time    DATETIME
);

-- 表3：收藏夹表
CREATE TABLE IF NOT EXISTS veg_favorites_list (
    fav_list_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER      NOT NULL,
    list_name   VARCHAR(50)  NOT NULL,
    create_time DATETIME     NOT NULL DEFAULT (datetime('now', 'localtime')),
    update_time DATETIME,
    FOREIGN KEY (user_id) REFERENCES sys_user(user_id)
);

-- 表4：收藏明细表
CREATE TABLE IF NOT EXISTS veg_favorite_item (
    item_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    fav_list_id INTEGER  NOT NULL,
    veg_id      INTEGER  NOT NULL,
    create_time DATETIME NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (fav_list_id) REFERENCES veg_favorites_list(fav_list_id),
    FOREIGN KEY (veg_id) REFERENCES veg_vegetable(veg_id)
);

-- 表5：自定义清单表
CREATE TABLE IF NOT EXISTS veg_custom_list (
    list_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER      NOT NULL,
    list_name   VARCHAR(50)  NOT NULL,
    description VARCHAR(200),
    create_time DATETIME     NOT NULL DEFAULT (datetime('now', 'localtime')),
    update_time DATETIME,
    FOREIGN KEY (user_id) REFERENCES sys_user(user_id)
);

-- 表6：清单明细表
CREATE TABLE IF NOT EXISTS veg_list_item (
    item_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    list_id     INTEGER  NOT NULL,
    veg_id      INTEGER  NOT NULL,
    create_time DATETIME NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (list_id) REFERENCES veg_custom_list(list_id),
    FOREIGN KEY (veg_id) REFERENCES veg_vegetable(veg_id)
);

-- 表7：关联规则表
CREATE TABLE IF NOT EXISTS veg_association_rule (
    rule_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    ante_veg_id INTEGER  NOT NULL,
    post_veg_id INTEGER  NOT NULL,
    support     DOUBLE   NOT NULL,
    confidence  DOUBLE   NOT NULL,
    lift        DOUBLE   NOT NULL,
    create_time DATETIME NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (ante_veg_id) REFERENCES veg_vegetable(veg_id),
    FOREIGN KEY (post_veg_id) REFERENCES veg_vegetable(veg_id)
);

-- 表8：烹饪方法表
CREATE TABLE IF NOT EXISTS veg_cooking_method (
    method_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    veg_id       INTEGER      NOT NULL,
    method_name  VARCHAR(50)  NOT NULL,
    cooking_time VARCHAR(50),
    ingredients  VARCHAR(200),
    create_time  DATETIME     NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (veg_id) REFERENCES veg_vegetable(veg_id) ON DELETE CASCADE
);

-- 表9：浏览历史表
CREATE TABLE IF NOT EXISTS veg_browse_history (
    history_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER  NOT NULL,
    veg_id      INTEGER  NOT NULL,
    browse_time DATETIME NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES sys_user(user_id),
    FOREIGN KEY (veg_id) REFERENCES veg_vegetable(veg_id)
);
