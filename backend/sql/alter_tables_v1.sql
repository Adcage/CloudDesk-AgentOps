-- CloudDesk 企业化改造 v1：为 tickets 表添加扩展字段
ALTER TABLE business.tickets
    ADD COLUMN IF NOT EXISTS order_id VARCHAR(64),
    ADD COLUMN IF NOT EXISTS description TEXT,
    ADD COLUMN IF NOT EXISTS sla_deadline TIMESTAMP,
    ADD COLUMN IF NOT EXISTS first_response_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS escalation_count INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS assigned_to VARCHAR(64);

-- CloudDesk 企业化改造 v1：为 approvals 表添加扩展字段
ALTER TABLE business.approvals
    ADD COLUMN IF NOT EXISTS order_id VARCHAR(64),
    ADD COLUMN IF NOT EXISTS sla_deadline TIMESTAMP,
    ADD COLUMN IF NOT EXISTS approval_level INTEGER DEFAULT 1,
    ADD COLUMN IF NOT EXISTS risk_score NUMERIC(5,2) DEFAULT 0;
