-- =====================================================
-- CloudDesk V3: 数据库权限隔离
-- Java 使用 java_app_user（仅访问 business schema）
-- Python 使用 python_agent_user（仅访问 agent schema）
-- =====================================================

REVOKE CREATE ON SCHEMA public FROM PUBLIC;

-- 创建应用角色
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'java_app_user') THEN
        CREATE ROLE java_app_user WITH LOGIN PASSWORD 'clouddesk_java_2026' INHERIT;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'python_agent_user') THEN
        CREATE ROLE python_agent_user WITH LOGIN PASSWORD 'clouddesk_python_2026' INHERIT;
    END IF;
END $$;

-- Java 用户：business schema 完整权限，agent schema 只读
GRANT USAGE ON SCHEMA business TO java_app_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA business TO java_app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA business GRANT ALL ON TABLES TO java_app_user;

GRANT USAGE ON SCHEMA agent TO java_app_user;
GRANT SELECT ON ALL TABLES IN SCHEMA agent TO java_app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA agent GRANT SELECT ON TABLES TO java_app_user;

-- Python 用户：agent schema 完整权限
GRANT USAGE ON SCHEMA agent TO python_agent_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA agent TO python_agent_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA agent GRANT ALL ON TABLES TO python_agent_user;

-- 确保新表自动获得权限
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA business
    GRANT ALL ON TABLES TO java_app_user;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA agent
    GRANT ALL ON TABLES TO python_agent_user;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA agent
    GRANT SELECT ON TABLES TO java_app_user;
