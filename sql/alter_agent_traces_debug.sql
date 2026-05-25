-- CloudDesk Agent Trace 调试字段增强
-- 为 agent_traces 表增加工作流调试数据字段

-- ============================================================
-- 1. agent_traces 增加调试字段
-- ============================================================
ALTER TABLE agent.agent_traces
ADD COLUMN IF NOT EXISTS risk_level VARCHAR(20),
ADD COLUMN IF NOT EXISTS entities JSONB,
ADD COLUMN IF NOT EXISTS approval_required BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS approval_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS handoff_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS citations JSONB,
ADD COLUMN IF NOT EXISTS workflow_steps JSONB;

COMMENT ON COLUMN agent.agent_traces.risk_level IS '风险等级: high/medium/low';
COMMENT ON COLUMN agent.agent_traces.entities IS '意图识别抽取的实体 (customer_id, order_id, amount)';
COMMENT ON COLUMN agent.agent_traces.approval_required IS '是否需要审批';
COMMENT ON COLUMN agent.agent_traces.approval_id IS '审批单ID';
COMMENT ON COLUMN agent.agent_traces.handoff_count IS 'Agent转交次数';
COMMENT ON COLUMN agent.agent_traces.citations IS 'RAG引用来源列表';
COMMENT ON COLUMN agent.agent_traces.workflow_steps IS '工作流步骤记录，每步包含agent/action/detail';

-- ============================================================
-- 2. 为已有数据补充默认值
-- ============================================================
UPDATE agent.agent_traces
SET risk_level = 'low'
WHERE risk_level IS NULL;

UPDATE agent.agent_traces
SET handoff_count = 0
WHERE handoff_count IS NULL;

UPDATE agent.agent_traces
SET approval_required = FALSE
WHERE approval_required IS NULL;

-- ============================================================
-- 3. 创建索引优化调试查询
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_traces_intent ON agent.agent_traces(intent);
CREATE INDEX IF NOT EXISTS idx_traces_risk_level ON agent.agent_traces(risk_level);
CREATE INDEX IF NOT EXISTS idx_traces_approval_required ON agent.agent_traces(approval_required);
CREATE INDEX IF NOT EXISTS idx_traces_status ON agent.agent_traces(status);

-- ============================================================
-- 4. 验证变更结果
-- ============================================================
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_schema = 'agent' AND table_name = 'agent_traces'
ORDER BY ordinal_position;
