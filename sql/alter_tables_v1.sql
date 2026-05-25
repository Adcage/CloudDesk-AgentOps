-- CloudDesk 企业感改造 V1 - 表结构变更
-- 执行前请先备份数据库

-- ============================================================
-- 1. business.tickets 增加 SLA 和处理人字段
-- ============================================================
ALTER TABLE business.tickets 
ADD COLUMN IF NOT EXISTS sla_deadline TIMESTAMP,
ADD COLUMN IF NOT EXISTS first_response_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS escalation_count INT DEFAULT 0,
ADD COLUMN IF NOT EXISTS assigned_to VARCHAR(50);

COMMENT ON COLUMN business.tickets.sla_deadline IS 'SLA 截止时间';
COMMENT ON COLUMN business.tickets.first_response_at IS '首次响应时间';
COMMENT ON COLUMN business.tickets.resolved_at IS '解决时间';
COMMENT ON COLUMN business.tickets.escalation_count IS '升级次数';
COMMENT ON COLUMN business.tickets.assigned_to IS '当前处理人 user_id';

-- 为现有工单补充默认值
UPDATE business.tickets 
SET sla_deadline = created_at + INTERVAL '24 hours'
WHERE sla_deadline IS NULL;

UPDATE business.tickets 
SET assigned_to = 'U001'
WHERE assigned_to IS NULL AND status IN ('in_progress', 'resolved');

-- ============================================================
-- 2. business.approvals 增加审批层级和风险评分
-- ============================================================
ALTER TABLE business.approvals 
ADD COLUMN IF NOT EXISTS sla_deadline TIMESTAMP,
ADD COLUMN IF NOT EXISTS approval_level INT DEFAULT 1,
ADD COLUMN IF NOT EXISTS risk_score DECIMAL(5,2) DEFAULT 0;

COMMENT ON COLUMN business.approvals.sla_deadline IS 'SLA 截止时间';
COMMENT ON COLUMN business.approvals.approval_level IS '审批层级：1=普通 2=主管 3=总监';
COMMENT ON COLUMN business.approvals.risk_score IS '风险评分 0-100';

-- 为现有审批补充默认值
UPDATE business.approvals 
SET sla_deadline = created_at + INTERVAL '48 hours'
WHERE sla_deadline IS NULL;

UPDATE business.approvals 
SET approval_level = CASE 
    WHEN amount >= 1000 THEN 3
    WHEN amount >= 500 THEN 2
    ELSE 1
END
WHERE approval_level = 1;

UPDATE business.approvals 
SET risk_score = CASE 
    WHEN amount >= 1000 THEN 75.0
    WHEN amount >= 500 THEN 50.0
    WHEN amount >= 100 THEN 30.0
    ELSE 10.0
END
WHERE risk_score = 0;

-- ============================================================
-- 3. business.customers 增加最后活跃时间
-- ============================================================
ALTER TABLE business.customers 
ADD COLUMN IF NOT EXISTS last_active_at TIMESTAMP;

COMMENT ON COLUMN business.customers.last_active_at IS '最后活跃时间';

UPDATE business.customers 
SET last_active_at = updated_at
WHERE last_active_at IS NULL;

-- ============================================================
-- 4. 创建索引优化查询性能
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_tickets_assigned_to ON business.tickets(assigned_to);
CREATE INDEX IF NOT EXISTS idx_tickets_sla_deadline ON business.tickets(sla_deadline);
CREATE INDEX IF NOT EXISTS idx_tickets_status_created ON business.tickets(status, created_at);

CREATE INDEX IF NOT EXISTS idx_approvals_status_created ON business.approvals(status, created_at);
CREATE INDEX IF NOT EXISTS idx_approvals_level_status ON business.approvals(approval_level, status);

CREATE INDEX IF NOT EXISTS idx_customers_risk_level ON business.customers(risk_level);
CREATE INDEX IF NOT EXISTS idx_customers_plan_status ON business.customers(plan, status);

-- ============================================================
-- 5. 验证变更结果
-- ============================================================
-- 查看 tickets 表结构
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_schema = 'business' AND table_name = 'tickets'
ORDER BY ordinal_position;

-- 查看 approvals 表结构
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_schema = 'business' AND table_name = 'approvals'
ORDER BY ordinal_position;

-- 统计数据分布
SELECT 
    'tickets' as table_name,
    COUNT(*) as total,
    COUNT(CASE WHEN assigned_to IS NOT NULL THEN 1 END) as has_assigned,
    COUNT(CASE WHEN sla_deadline IS NOT NULL THEN 1 END) as has_sla
FROM business.tickets
UNION ALL
SELECT 
    'approvals' as table_name,
    COUNT(*) as total,
    COUNT(CASE WHEN approval_level > 1 THEN 1 END) as high_level,
    COUNT(CASE WHEN risk_score > 50 THEN 1 END) as high_risk
FROM business.approvals;
