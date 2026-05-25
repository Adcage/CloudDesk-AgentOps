-- =====================================================
-- CloudDesk V3: Hybrid Retrieval 数据库变更
-- 为 agent.document_chunks 添加 tsvector 全文检索支持
-- =====================================================

-- 1. 新增 tsvector 列
ALTER TABLE agent.document_chunks
    ADD COLUMN IF NOT EXISTS text_search tsvector;

-- 2. 创建 GIN 索引加速全文检索
CREATE INDEX IF NOT EXISTS idx_chunks_text_search
    ON agent.document_chunks USING GIN (text_search);

-- 3. 创建触发器函数：写入/更新时自动更新 tsvector
CREATE OR REPLACE FUNCTION agent.update_text_search()
RETURNS trigger AS $$
BEGIN
    NEW.text_search := to_tsvector('simple', COALESCE(NEW.chunk_text, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 4. 创建触发器
DROP TRIGGER IF EXISTS trg_update_text_search ON agent.document_chunks;
CREATE TRIGGER trg_update_text_search
    BEFORE INSERT OR UPDATE ON agent.document_chunks
    FOR EACH ROW
    EXECUTE FUNCTION agent.update_text_search();

-- 5. 回填现有数据
UPDATE agent.document_chunks
SET text_search = to_tsvector('simple', COALESCE(chunk_text, ''));
