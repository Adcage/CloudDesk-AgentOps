package com.springboot.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.springboot.model.dto.auditlog.AuditLogQueryRequest;
import com.springboot.model.entity.AuditLog;
import com.springboot.mapper.AuditLogMapper;
import com.springboot.service.AuditLogService;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;

@Service
public class AuditLogServiceImpl implements AuditLogService {

    @Resource
    private AuditLogMapper auditLogMapper;

    @Override
    public Page<AuditLog> listPage(AuditLogQueryRequest request) {
        long current = request.getCurrent();
        long size = request.getPageSize();
        QueryWrapper<AuditLog> queryWrapper = new QueryWrapper<>();
        queryWrapper.orderByDesc("created_at");
        return auditLogMapper.selectPage(new Page<>(current, size), queryWrapper);
    }

    @Override
    public AuditLog create(AuditLog auditLog) {
        int result = auditLogMapper.insert(auditLog);
        if (result <= 0) {
            return null;
        }
        return auditLog;
    }
}