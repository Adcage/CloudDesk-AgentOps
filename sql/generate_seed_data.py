#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CloudDesk 企业级种子数据生成器
生成符合真实分布的中文业务数据
"""

import random
import datetime
from typing import List, Tuple
import hashlib
import sys
import io

# 设置 UTF-8 输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============================================================
# 配置参数
# ============================================================
NUM_CUSTOMERS = 100
NUM_ORDERS = 500
NUM_TICKETS = 300
NUM_APPROVALS = 150

START_DATE = datetime.datetime.now() - datetime.timedelta(days=90)
END_DATE = datetime.datetime.now()

# ============================================================
# 真实中文数据模板
# ============================================================

COMPANY_PREFIXES = [
    "北京", "上海", "深圳", "广州", "杭州", "成都", "武汉", "西安", "南京", "苏州",
    "天津", "重庆", "青岛", "大连", "厦门", "长沙", "郑州", "济南", "福州", "合肥"
]

COMPANY_TYPES = [
    "科技有限公司", "网络科技公司", "信息技术公司", "电子商务公司", "软件开发公司",
    "数据服务公司", "智能科技公司", "云计算公司", "互联网公司", "咨询服务公司"
]

COMPANY_NAMES = [
    "创新", "智联", "云端", "数智", "飞扬", "腾跃", "星辰", "海纳", "鼎盛", "卓越",
    "华美", "锦绣", "博雅", "恒通", "瑞达", "金石", "天成", "盛世", "宏图", "远航"
]

CONTACT_SURNAMES = ["张", "王", "李", "刘", "陈", "杨", "黄", "赵", "吴", "周", "徐", "孙", "马", "朱", "胡", "郭", "何", "高", "林", "罗"]
CONTACT_NAMES = ["伟", "芳", "娜", "敏", "静", "丽", "强", "磊", "军", "洋", "勇", "艳", "杰", "娟", "涛", "明", "超", "秀英", "霞", "平"]

TICKET_SUBJECTS = [
    "订单 {order_id} 支付失败，请协助处理",
    "重复扣费问题，订单号 {order_id}",
    "账户余额异常，无法完成支付",
    "发票开具申请 - 订单 {order_id}",
    "订单 {order_id} 退款进度查询",
    "系统登录异常，提示账号被锁定",
    "API 调用频繁超时，影响业务",
    "数据同步延迟，订单状态未更新",
    "账单金额与实际不符，需核对",
    "服务到期续费问题咨询",
    "权限申请 - 需要开通高级功能",
    "订单 {order_id} 物流信息未更新",
    "批量导入数据失败，报错信息不明确",
    "对账单下载功能异常",
    "客户信息修改申请",
]

TICKET_DESCRIPTIONS = [
    "客户反馈在支付环节点击确认后页面无响应，已尝试更换浏览器和网络环境，问题依旧。请技术团队排查支付网关日志。",
    "客户账户在 {time} 被重复扣款两次，金额分别为 ¥{amount1} 和 ¥{amount2}，订单号相同。客户要求立即退还多扣款项并给出解释。",
    "客户报告账户余额显示为负数，但近期无大额消费记录。怀疑系统计算错误，需财务和技术联合核查。",
    "企业客户要求开具增值税专用发票，抬头：{company}，税号：91110000{tax_code}，订单金额 ¥{amount}。",
    "客户于 {days} 天前提交退款申请，至今未到账。多次催促无果，情绪激动，威胁投诉至消费者协会。",
    "客户反馈使用正确账号密码登录时提示'账号已被锁定，请联系管理员'，但未收到任何安全警告邮件。",
    "业务高峰期（每日 10:00-11:00）API 响应时间超过 5 秒，导致订单创建失败率上升至 15%，严重影响客户体验。",
    "订单在上游系统已标记为'已发货'，但下游 CRM 系统仍显示'待处理'，数据同步延迟超过 2 小时。",
    "客户对账时发现本月账单总额比实际消费高出 ¥{diff}，要求提供详细消费明细和差异说明。",
    "客户服务套餐将于 {days} 天后到期，咨询续费折扣政策及是否支持按月付费。",
    "客户申请开通'批量导出'和'自定义报表'功能，需主管审批后开通权限。",
    "客户反馈订单已签收 3 天，但系统物流信息仍停留在'运输中'状态，要求更新。",
    "使用批量导入功能上传 Excel 文件后提示'第 47 行数据格式错误'，但未说明具体哪个字段有问题，客户无法定位。",
    "客户尝试下载本月对账单时页面报错'文件生成失败'，已尝试多次均无法成功。",
    "客户公司法人变更，需更新合同主体信息及发票抬头，要求提供变更流程和所需材料。",
]

APPROVAL_REASONS = [
    "客户投诉订单 {order_id} 商品质量问题，要求全额退款",
    "系统故障导致重复扣费，客户要求退还多扣金额 ¥{amount}",
    "客户取消订单 {order_id}，申请退款 ¥{amount}（已扣除手续费）",
    "VIP 客户申请特殊折扣，订单金额 ¥{amount}，申请优惠 15%",
    "客户账户异常冻结，申请解冻并补偿损失 ¥{amount}",
    "合同提前终止，客户要求按比例退还剩余服务费 ¥{amount}",
    "客户升级服务套餐，申请补差价优惠 ¥{amount}",
    "批量采购订单，客户申请企业折扣，总金额 ¥{amount}",
]

# ============================================================
# 工具函数
# ============================================================

def random_date(start: datetime.datetime, end: datetime.datetime) -> datetime.datetime:
    """生成随机时间，工作日概率更高"""
    delta = end - start
    random_days = random.random() * delta.days
    random_seconds = random.random() * 86400
    
    result = start + datetime.timedelta(days=random_days, seconds=random_seconds)
    
    # 工作日权重更高
    if result.weekday() >= 5:  # 周末
        if random.random() < 0.6:  # 60% 概率重新生成
            return random_date(start, end)
    
    # 工作时间权重更高 (9:00-18:00)
    if result.hour < 9 or result.hour >= 18:
        if random.random() < 0.7:  # 70% 概率调整到工作时间
            result = result.replace(hour=random.randint(9, 17))
    
    return result

def generate_customer_id(index: int) -> str:
    return f"C{index:05d}"

def generate_order_id(index: int) -> str:
    return f"O{index:06d}"

def generate_ticket_id(index: int) -> str:
    return f"T{index:06d}"

def generate_approval_id(index: int) -> str:
    return f"A{index:06d}"

def generate_company_name() -> str:
    prefix = random.choice(COMPANY_PREFIXES)
    name = random.choice(COMPANY_NAMES)
    type_ = random.choice(COMPANY_TYPES)
    return f"{prefix}{name}{type_}"

def generate_contact_name() -> str:
    return random.choice(CONTACT_SURNAMES) + random.choice(CONTACT_NAMES)

def generate_email(name: str, company: str) -> str:
    # 简化公司名作为域名
    domain = company.replace("有限公司", "").replace("公司", "")[:6]
    pinyin_map = {"北京": "bj", "上海": "sh", "深圳": "sz", "广州": "gz", "杭州": "hz"}
    for cn, py in pinyin_map.items():
        domain = domain.replace(cn, py)
    return f"{name.lower()}@{domain}.com"

def generate_phone() -> str:
    return f"1{random.choice([3,5,7,8,9])}{random.randint(100000000, 999999999)}"

# ============================================================
# 数据生成函数
# ============================================================

def generate_customers() -> List[Tuple]:
    """生成客户数据"""
    customers = []
    risk_distribution = [0.7, 0.25, 0.05]  # low: 70%, medium: 25%, high: 5%
    plan_distribution = [0.6, 0.3, 0.1]  # basic: 60%, pro: 30%, enterprise: 10%
    
    for i in range(1, NUM_CUSTOMERS + 1):
        customer_id = generate_customer_id(i)
        company = generate_company_name()
        contact = generate_contact_name()
        email = generate_email(contact, company)
        phone = generate_phone()
        
        risk_level = random.choices(['low', 'medium', 'high'], weights=risk_distribution)[0]
        plan = random.choices(['basic', 'pro', 'enterprise'], weights=plan_distribution)[0]
        status = random.choices(['active', 'inactive'], weights=[0.9, 0.1])[0]
        
        created_at = random_date(START_DATE, END_DATE - datetime.timedelta(days=30))
        last_active = random_date(created_at, END_DATE)
        
        customers.append((
            customer_id, company, contact, email, phone,
            risk_level, plan, status,
            created_at.strftime('%Y-%m-%d %H:%M:%S'),
            last_active.strftime('%Y-%m-%d %H:%M:%S'),
            last_active.strftime('%Y-%m-%d %H:%M:%S')
        ))
    
    return customers

def generate_orders(customers: List[Tuple]) -> List[Tuple]:
    """生成订单数据"""
    orders = []
    
    for i in range(1, NUM_ORDERS + 1):
        order_id = generate_order_id(i)
        customer = random.choice(customers)
        customer_id = customer[0]
        
        # 金额分布：大部分小额，少量大额
        if random.random() < 0.7:
            amount = round(random.uniform(100, 1000), 2)
        elif random.random() < 0.9:
            amount = round(random.uniform(1000, 5000), 2)
        else:
            amount = round(random.uniform(5000, 20000), 2)
        
        status_weights = [0.1, 0.15, 0.6, 0.1, 0.05]
        status = random.choices(['pending', 'processing', 'completed', 'cancelled', 'refunded'], 
                               weights=status_weights)[0]
        
        created_at = random_date(START_DATE, END_DATE)
        
        orders.append((
            order_id, customer_id, amount, status,
            created_at.strftime('%Y-%m-%d %H:%M:%S'),
            created_at.strftime('%Y-%m-%d %H:%M:%S')
        ))
    
    return orders

def generate_tickets(customers: List[Tuple], orders: List[Tuple]) -> List[Tuple]:
    """生成工单数据"""
    tickets = []
    users = ['U001', 'U002', 'U003']  # support_agent, manager, admin
    
    for i in range(1, NUM_TICKETS + 1):
        ticket_id = generate_ticket_id(i)
        customer = random.choice(customers)
        customer_id = customer[0]
        
        # 60% 工单关联订单
        order_id = random.choice(orders)[0] if random.random() < 0.6 else None
        
        subject_template = random.choice(TICKET_SUBJECTS)
        subject = subject_template.format(order_id=order_id or "N/A")
        
        description_template = random.choice(TICKET_DESCRIPTIONS)
        description = description_template.format(
            time=f"{random.randint(1, 30)}日{random.randint(9, 17)}时",
            amount1=round(random.uniform(100, 1000), 2),
            amount2=round(random.uniform(100, 1000), 2),
            company=customer[1],
            tax_code=f"{random.randint(10000000, 99999999)}",
            amount=round(random.uniform(500, 5000), 2),
            days=random.randint(3, 15),
            diff=round(random.uniform(50, 500), 2)
        )
        
        category = random.choice(['billing', 'technical', 'account', 'general'])
        priority = random.choices(['low', 'medium', 'high', 'urgent'], 
                                 weights=[0.4, 0.35, 0.2, 0.05])[0]
        
        status_weights = [0.3, 0.25, 0.35, 0.1]
        status = random.choices(['open', 'in_progress', 'resolved', 'closed'], 
                               weights=status_weights)[0]
        
        created_at = random_date(START_DATE, END_DATE)
        
        # SLA 根据优先级设置
        sla_hours = {'low': 48, 'medium': 24, 'high': 8, 'urgent': 4}
        sla_deadline = created_at + datetime.timedelta(hours=sla_hours[priority])
        
        # 已处理的工单设置响应和解决时间
        first_response = None
        resolved_at = None
        assigned_to = None
        escalation_count = 0
        
        if status in ['in_progress', 'resolved', 'closed']:
            assigned_to = random.choice(users)
            first_response = created_at + datetime.timedelta(hours=random.uniform(0.5, 4))
            
            if status in ['resolved', 'closed']:
                resolved_at = first_response + datetime.timedelta(hours=random.uniform(1, 24))
                
                # 10% 概率升级过
                if random.random() < 0.1:
                    escalation_count = random.randint(1, 2)
        
        agent_summary = f"客户{customer[2]}反馈{category}问题，优先级{priority}。" if status != 'open' else None
        
        tickets.append((
            ticket_id, customer_id, order_id, subject, description,
            category, priority, status, agent_summary,
            created_at.strftime('%Y-%m-%d %H:%M:%S'),
            created_at.strftime('%Y-%m-%d %H:%M:%S'),
            sla_deadline.strftime('%Y-%m-%d %H:%M:%S'),
            first_response.strftime('%Y-%m-%d %H:%M:%S') if first_response else None,
            resolved_at.strftime('%Y-%m-%d %H:%M:%S') if resolved_at else None,
            escalation_count,
            assigned_to
        ))
    
    return tickets

def generate_approvals(customers: List[Tuple], orders: List[Tuple]) -> List[Tuple]:
    """生成审批数据"""
    approvals = []
    
    for i in range(1, NUM_APPROVALS + 1):
        approval_id = generate_approval_id(i)
        customer = random.choice(customers)
        customer_id = customer[0]
        order = random.choice(orders)
        order_id = order[0]
        
        # 金额分布
        if random.random() < 0.6:
            amount = round(random.uniform(50, 500), 2)
            approval_level = 1
            risk_score = round(random.uniform(10, 30), 2)
        elif random.random() < 0.9:
            amount = round(random.uniform(500, 2000), 2)
            approval_level = 2
            risk_score = round(random.uniform(30, 60), 2)
        else:
            amount = round(random.uniform(2000, 10000), 2)
            approval_level = 3
            risk_score = round(random.uniform(60, 95), 2)
        
        reason_template = random.choice(APPROVAL_REASONS)
        reason = reason_template.format(order_id=order_id, amount=amount)
        
        status_weights = [0.3, 0.5, 0.15, 0.05]
        status = random.choices(['pending', 'approved', 'rejected', 'cancelled'], 
                               weights=status_weights)[0]
        
        created_at = random_date(START_DATE, END_DATE)
        sla_deadline = created_at + datetime.timedelta(hours=48)
        
        approvals.append((
            approval_id, customer_id, order_id, amount, reason,
            status,
            created_at.strftime('%Y-%m-%d %H:%M:%S'),
            created_at.strftime('%Y-%m-%d %H:%M:%S'),
            sla_deadline.strftime('%Y-%m-%d %H:%M:%S'),
            approval_level,
            risk_score
        ))
    
    return approvals

# ============================================================
# SQL 生成
# ============================================================

def generate_sql():
    """生成完整的 SQL 插入语句"""
    
    print("-- ============================================================")
    print("-- CloudDesk 企业级种子数据")
    print(f"-- 生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"-- 数据规模: {NUM_CUSTOMERS} 客户 + {NUM_ORDERS} 订单 + {NUM_TICKETS} 工单 + {NUM_APPROVALS} 审批")
    print("-- ============================================================\n")
    
    print("-- 清空现有数据")
    print("TRUNCATE TABLE business.approvals CASCADE;")
    print("TRUNCATE TABLE business.tickets CASCADE;")
    print("TRUNCATE TABLE business.orders CASCADE;")
    print("TRUNCATE TABLE business.customers CASCADE;\n")
    
    # 生成数据
    customers = generate_customers()
    orders = generate_orders(customers)
    tickets = generate_tickets(customers, orders)
    approvals = generate_approvals(customers, orders)
    
    # 客户数据
    print("-- ============================================================")
    print(f"-- 插入 {len(customers)} 条客户数据")
    print("-- ============================================================")
    print("INSERT INTO business.customers (customer_id, name, contact_name, email, phone, risk_level, plan, status, created_at, updated_at, last_active_at) VALUES")
    for i, c in enumerate(customers):
        comma = "," if i < len(customers) - 1 else ";"
        print(f"('{c[0]}', '{c[1]}', '{c[2]}', '{c[3]}', '{c[4]}', '{c[5]}', '{c[6]}', '{c[7]}', '{c[8]}', '{c[9]}', '{c[10]}'){comma}")
    print()
    
    # 订单数据
    print("-- ============================================================")
    print(f"-- 插入 {len(orders)} 条订单数据")
    print("-- ============================================================")
    print("INSERT INTO business.orders (order_id, customer_id, amount, status, created_at, updated_at) VALUES")
    for i, o in enumerate(orders):
        comma = "," if i < len(orders) - 1 else ";"
        print(f"('{o[0]}', '{o[1]}', {o[2]}, '{o[3]}', '{o[4]}', '{o[5]}'){comma}")
    print()
    
    # 工单数据
    print("-- ============================================================")
    print(f"-- 插入 {len(tickets)} 条工单数据")
    print("-- ============================================================")
    print("INSERT INTO business.tickets (ticket_id, customer_id, order_id, subject, description, category, priority, status, agent_summary, created_at, updated_at, sla_deadline, first_response_at, resolved_at, escalation_count, assigned_to) VALUES")
    for i, t in enumerate(tickets):
        comma = "," if i < len(tickets) - 1 else ";"
        order_id = f"'{t[2]}'" if t[2] else "NULL"
        agent_summary = f"'{t[8]}'" if t[8] else "NULL"
        first_response = f"'{t[12]}'" if t[12] else "NULL"
        resolved_at = f"'{t[13]}'" if t[13] else "NULL"
        assigned_to = f"'{t[15]}'" if t[15] else "NULL"
        
        # 转义单引号
        subject = t[3].replace("'", "''")
        description = t[4].replace("'", "''")
        
        print(f"('{t[0]}', '{t[1]}', {order_id}, '{subject}', '{description}', '{t[5]}', '{t[6]}', '{t[7]}', {agent_summary}, '{t[9]}', '{t[10]}', '{t[11]}', {first_response}, {resolved_at}, {t[14]}, {assigned_to}){comma}")
    print()
    
    # 审批数据
    print("-- ============================================================")
    print(f"-- 插入 {len(approvals)} 条审批数据")
    print("-- ============================================================")
    print("INSERT INTO business.approvals (approval_id, customer_id, order_id, amount, reason, status, created_at, updated_at, sla_deadline, approval_level, risk_score) VALUES")
    for i, a in enumerate(approvals):
        comma = "," if i < len(approvals) - 1 else ";"
        reason = a[4].replace("'", "''")
        print(f"('{a[0]}', '{a[1]}', '{a[2]}', {a[3]}, '{reason}', '{a[5]}', '{a[6]}', '{a[7]}', '{a[8]}', {a[9]}, {a[10]}){comma}")
    print()
    
    # 统计信息
    print("-- ============================================================")
    print("-- 数据统计")
    print("-- ============================================================")
    print("SELECT 'customers' as table_name, COUNT(*) as count FROM business.customers")
    print("UNION ALL SELECT 'orders', COUNT(*) FROM business.orders")
    print("UNION ALL SELECT 'tickets', COUNT(*) FROM business.tickets")
    print("UNION ALL SELECT 'approvals', COUNT(*) FROM business.approvals;")

if __name__ == "__main__":
    generate_sql()
