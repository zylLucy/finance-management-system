-- =========================================
-- Smart Ledger 数据库初始化脚本
-- 文件名：initial_schema.sql
-- =========================================

-- 建议先创建数据库
CREATE DATABASE IF NOT EXISTS `smart_ledger`
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE `smart_ledger`;

-- =========================================
-- 1. 用户表
-- =========================================
CREATE TABLE `user` (
    `user_id` INT NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(50) NOT NULL,
    `register_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `password` VARCHAR(255) NOT NULL,   -- 存储密码哈希值
    PRIMARY KEY (`user_id`),
    UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================
-- 2. 账单分类表
-- =========================================
CREATE TABLE `category` (
    `category_id` INT NOT NULL AUTO_INCREMENT,
    `category_name` VARCHAR(50) NOT NULL,
    `type` ENUM('income', 'expense') NOT NULL,
    PRIMARY KEY (`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================
-- 3. 月预算表
-- 采用复合主键：(user_id, year_month)
-- year_month 格式：YYYYMM
-- =========================================
CREATE TABLE `monthly_budget` (
    `user_id` INT NOT NULL,
    `year_month` INT NOT NULL,
    `amount` DECIMAL(10,2) NOT NULL,

    PRIMARY KEY (`user_id`, `year_month`),

    FOREIGN KEY (`user_id`)
        REFERENCES `user`(`user_id`)
        ON DELETE CASCADE,

    CONSTRAINT `chk_year_month`
        CHECK (year_month BETWEEN 200001 AND 210012)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================
-- 4. 账单记录表
-- =========================================
CREATE TABLE `bill_record` (
    `record_id` INT NOT NULL AUTO_INCREMENT,
    `amount` DECIMAL(10,2) NOT NULL,
    `date` DATE NOT NULL,
    `remark` VARCHAR(255) NULL,

    `user_id` INT NOT NULL,
    `category_id` INT NOT NULL,

    PRIMARY KEY (`record_id`),

    FOREIGN KEY (`user_id`)
        REFERENCES `user`(`user_id`)
        ON DELETE CASCADE,

    FOREIGN KEY (`category_id`)
        REFERENCES `category`(`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================
-- 5. AI 财务报告表
-- =========================================
CREATE TABLE `ai_report` (
    `report_id` INT NOT NULL AUTO_INCREMENT,
    `content` TEXT NOT NULL,

    `year_month` INT NOT NULL,
    `user_id` INT NOT NULL,

    PRIMARY KEY (`report_id`),

    FOREIGN KEY (`user_id`)
        REFERENCES `user`(`user_id`)
        ON DELETE CASCADE,

    CONSTRAINT `chk_report_year_month`
        CHECK (year_month BETWEEN 200001 AND 210012)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================
-- 6. 初始化系统基础分类数据
-- =========================================
INSERT INTO `category` (`category_name`, `type`) VALUES
('餐饮', 'expense'),
('购物', 'expense'),
('娱乐', 'expense'),
('交通', 'expense'),
('学习', 'expense'),

('工资', 'income'),
('奖学金', 'income'),
('生活费', 'income'),
('兼职收入', 'income');