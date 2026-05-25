package com.springboot.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.springboot.model.dto.auditlog.AuditLogQueryRequest;
import com.springboot.model.entity.AuditLog;

public interface AuditLogService {

    Page<AuditLog> listPage(AuditLogQueryRequest request);

    AuditLog create(AuditLog auditLog);
}