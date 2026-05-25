-- CloudDesk AI Support Agent MVP V1
-- 种子数据（最小测试集）

-- ============================================================
-- 1. business.users — 3 条（support_agent, manager, admin）
-- ============================================================
-- passwords are MD5(SALT + plaintext), SALT='springboot', plaintext='123456'
-- MD5('springboot123456') = a384380c440fb620eb080df5cbfcd0f0
INSERT INTO business.users (user_id, username, password, role) VALUES
    ('U001', 'support_agent', 'a384380c440fb620eb080df5cbfcd0f0', 'support_agent'),
    ('U002', 'manager',       'a384380c440fb620eb080df5cbfcd0f0', 'manager'),
    ('U003', 'admin',         'a384380c440fb620eb080df5cbfcd0f0', 'admin');

-- ============================================================
-- 2. business.customers — 5 条（C001-C005，不同 plan 和 risk_level）
-- ============================================================
INSERT INTO business.customers (customer_id, name, email, plan, status, risk_level) VALUES
    ('C001', 'Acme Corp',          'billing@acme.com',          'enterprise', 'active', 'low'),
    ('C002', 'Beta Solutions',     'support@beta.io',           'business',   'active', 'medium'),
    ('C003', 'Gamma Labs',         'admin@gammalabs.org',       'business',   'active', 'high'),
    ('C004', 'Delta Services',     'contact@deltaservices.com', 'free',       'active', 'low'),
    ('C005', 'Epsilon Tech',       'help@epsilontech.net',      'free',       'suspended', 'high');

-- ============================================================
-- 3. business.orders — 5 条（O1001-O1005，关联客户，含一条 duplicate_charge）
-- ============================================================
INSERT INTO business.orders (order_id, customer_id, amount, status, issue_type) VALUES
    ('O1001', 'C001', 299.99, 'completed',         NULL),
    ('O1002', 'C001', 299.99, 'completed',         'duplicate_charge'),
    ('O1003', 'C002',  49.99, 'completed',         NULL),
    ('O1004', 'C003', 149.00, 'completed',         NULL),
    ('O1005', 'C005',  19.99, 'payment_failed',    'payment_declined');

-- ============================================================
-- 4. business.tickets — 2 条示例工单
-- ============================================================
INSERT INTO business.tickets (ticket_id, customer_id, subject, category, priority, status, agent_summary, trace_id) VALUES
    ('T001', 'C001', '重复扣费问题：订单 O1001 和 O1002 金额相同', 'billing', 'high', 'open',
     '客户反馈两笔相同金额扣款，疑似重复收费，需核实并处理退款', 'TR_20260522_001'),
    ('T002', 'C004', '无法登录账号，提示密码错误', 'account', 'medium', 'open',
     '客户多次尝试登录失败，需协助重置密码', NULL);

-- ============================================================
-- 5. business.approvals — 1 条 pending 示例
-- ============================================================
INSERT INTO business.approvals (approval_id, customer_id, order_id, action, amount, reason, status, requested_by, trace_id) VALUES
    ('A001', 'C001', 'O1002', 'refund', 299.99,
     '订单 O1002 为重复扣费，客户申请全额退款。金额 >= $100，需主管审批。',
     'pending', 'U001', 'TR_20260522_001');
