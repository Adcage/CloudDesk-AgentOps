-- CloudDesk AI Support Agent MVP V1
-- PostgreSQL + pgvector 初始化脚本
-- business schema (Java 业务层) + agent schema (Python 智能体层)

-- ============================================================
-- 1. 启用 pgvector 扩展
-- ============================================================
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- 2. business schema
-- ============================================================
CREATE SCHEMA IF NOT EXISTS business;

CREATE TABLE business.users (
    user_id   VARCHAR(50)  PRIMARY KEY,
    username  VARCHAR(100) NOT NULL,
    password  VARCHAR(255) NOT NULL,
    role      VARCHAR(50)  NOT NULL DEFAULT 'support_agent',
    created_at TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE business.customers (
    customer_id VARCHAR(50)  PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(255),
    plan        VARCHAR(50),
    status      VARCHAR(50)  DEFAULT 'active',
    risk_level  VARCHAR(50)  DEFAULT 'low',
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE business.orders (
    order_id    VARCHAR(50)    PRIMARY KEY,
    customer_id VARCHAR(50)    NOT NULL,
    amount      DECIMAL(10, 2) NOT NULL,
    status      VARCHAR(50)    DEFAULT 'completed',
    issue_type  VARCHAR(100),
    created_at  TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP      DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE business.tickets (
    ticket_id    VARCHAR(50)  PRIMARY KEY,
    customer_id  VARCHAR(50)  NOT NULL,
    subject      TEXT         NOT NULL,
    category     VARCHAR(50),
    priority     VARCHAR(50)  DEFAULT 'medium',
    status       VARCHAR(50)  DEFAULT 'open',
    agent_summary TEXT,
    trace_id     VARCHAR(100),
    created_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE business.approvals (
    approval_id  VARCHAR(50)    PRIMARY KEY,
    customer_id  VARCHAR(50),
    order_id     VARCHAR(50),
    action       VARCHAR(50)    NOT NULL,
    amount       DECIMAL(10, 2),
    reason       TEXT,
    status       VARCHAR(50)    DEFAULT 'pending',
    requested_by VARCHAR(50),
    reviewed_by  VARCHAR(50),
    trace_id     VARCHAR(100),
    created_at   TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    reviewed_at  TIMESTAMP,
    updated_at   TIMESTAMP      DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE business.audit_logs (
    audit_id      VARCHAR(50)  PRIMARY KEY,
    user_id       VARCHAR(50),
    action        VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id   VARCHAR(50),
    old_value     TEXT,
    new_value     TEXT,
    trace_id      VARCHAR(100),
    created_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 3. agent schema
-- ============================================================
CREATE SCHEMA IF NOT EXISTS agent;

CREATE TABLE agent.agent_sessions (
    session_id      VARCHAR(50)  PRIMARY KEY,
    conversation_id VARCHAR(50)  NOT NULL,
    user_id         VARCHAR(50),
    current_agent   VARCHAR(50),
    summary         TEXT,
    created_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agent.agent_messages (
    message_id VARCHAR(50)  PRIMARY KEY,
    session_id VARCHAR(50)  NOT NULL,
    role       VARCHAR(50)  NOT NULL,
    content    TEXT         NOT NULL,
    trace_id   VARCHAR(100),
    created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agent.agent_traces (
    trace_id       VARCHAR(100)   PRIMARY KEY,
    session_id     VARCHAR(50),
    user_query     TEXT,
    selected_agent VARCHAR(100),
    intent         VARCHAR(100),
    model_used     VARCHAR(100),
    latency_ms     INTEGER,
    token_usage    INTEGER,
    estimated_cost DECIMAL(10, 6),
    status         VARCHAR(50)    DEFAULT 'running',
    final_answer   TEXT,
    created_at     TIMESTAMP      DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agent.agent_tool_calls (
    tool_call_id VARCHAR(50)  PRIMARY KEY,
    trace_id     VARCHAR(100) NOT NULL,
    agent_name   VARCHAR(100),
    tool_name    VARCHAR(100) NOT NULL,
    tool_input   JSONB,
    tool_output  JSONB,
    status       VARCHAR(50)  DEFAULT 'success',
    latency_ms   INTEGER,
    created_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agent.agent_handoffs (
    handoff_id      VARCHAR(50)  PRIMARY KEY,
    trace_id        VARCHAR(100) NOT NULL,
    from_agent      VARCHAR(100) NOT NULL,
    to_agent        VARCHAR(100) NOT NULL,
    reason          TEXT,
    handoff_payload JSONB,
    created_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agent.agent_memory (
    memory_id    VARCHAR(50)  PRIMARY KEY,
    memory_type  VARCHAR(50)  NOT NULL,
    subject_type VARCHAR(50),
    subject_id   VARCHAR(50),
    content      TEXT         NOT NULL,
    embedding    vector(1024),
    created_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agent.documents (
    document_id  VARCHAR(50)   PRIMARY KEY,
    title        VARCHAR(255)  NOT NULL,
    doc_type     VARCHAR(50)   DEFAULT 'policy',
    source_path  TEXT,
    version      VARCHAR(50)   DEFAULT '1',
    created_at   TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agent.document_chunks (
    chunk_id    VARCHAR(50)  PRIMARY KEY,
    document_id VARCHAR(50)  NOT NULL,
    chunk_text  TEXT         NOT NULL,
    chunk_index INTEGER     NOT NULL,
    embedding   vector(1024),
    metadata    JSONB,
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agent.eval_cases (
    case_id        VARCHAR(50)  PRIMARY KEY,
    question       TEXT         NOT NULL,
    expected_doc   VARCHAR(255),
    expected_tools TEXT,
    expected_action VARCHAR(100),
    risk_level     VARCHAR(50),
    created_at     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agent.eval_results (
    result_id                 VARCHAR(50)    PRIMARY KEY,
    case_id                   VARCHAR(50)    NOT NULL,
    trace_id                  VARCHAR(100),
    retrieval_hit             BOOLEAN,
    tool_call_correct         BOOLEAN,
    approval_routing_correct  BOOLEAN,
    task_success              BOOLEAN,
    latency_ms                INTEGER,
    estimated_cost            DECIMAL(10, 6),
    detail                    JSONB,
    created_at                TIMESTAMP      DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 4. pgvector 索引 (ivfflat)
-- ============================================================
CREATE INDEX idx_document_chunks_embedding ON agent.document_chunks
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX idx_agent_memory_embedding ON agent.agent_memory
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
