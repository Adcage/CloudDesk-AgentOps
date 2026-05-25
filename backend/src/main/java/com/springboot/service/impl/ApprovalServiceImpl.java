package com.springboot.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.springboot.common.ErrorCode;
import com.springboot.exception.BusinessException;
import com.springboot.exception.ThrowUtils;
import com.springboot.mapper.ApprovalMapper;
import com.springboot.mapper.AuditLogMapper;
import com.springboot.model.dto.approval.ApprovalQueryRequest;
import com.springboot.model.entity.Approval;
import com.springboot.model.entity.AuditLog;
import com.springboot.service.ApprovalService;
import jakarta.annotation.Resource;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;

@Service
public class ApprovalServiceImpl implements ApprovalService {

    @Resource
    private ApprovalMapper approvalMapper;

    @Resource
    private AuditLogMapper auditLogMapper;

    @Override
    public Page<Approval> listPage(ApprovalQueryRequest request) {
        long current = request.getCurrent();
        long size = request.getPageSize();
        QueryWrapper<Approval> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq(StringUtils.isNotBlank(request.getStatus()), "status", request.getStatus());
        queryWrapper.orderByDesc("created_at");
        return approvalMapper.selectPage(new Page<>(current, size), queryWrapper);
    }

    @Override
    public Approval createApproval(Approval approval) {
        approval.setStatus("pending");
        int result = approvalMapper.insert(approval);
        ThrowUtils.throwIf(result <= 0, ErrorCode.OPERATION_ERROR, "创建审批失败");
        AuditLog auditLog = new AuditLog();
        auditLog.setAction("create_approval");
        auditLog.setResourceType("approval");
        auditLog.setResourceId(approval.getApprovalId());
        auditLog.setTraceId(approval.getTraceId());
        auditLog.setNewValue(approval.getAction());
        auditLogMapper.insert(auditLog);
        return approval;
    }

    @Override
    public Approval approve(String approvalId, String reviewedBy) {
        Approval approval = approvalMapper.selectById(approvalId);
        ThrowUtils.throwIf(approval == null, ErrorCode.NOT_FOUND_ERROR, "审批不存在");
        if (!"pending".equals(approval.getStatus())) {
            throw new BusinessException(ErrorCode.OPERATION_ERROR, "只有待审批状态的审批才能通过");
        }
        approval.setStatus("approved");
        approval.setReviewedBy(reviewedBy);
        approval.setReviewedAt(new java.util.Date());
        int result = approvalMapper.updateById(approval);
        ThrowUtils.throwIf(result <= 0, ErrorCode.OPERATION_ERROR, "审批通过失败");
        AuditLog auditLog = new AuditLog();
        auditLog.setAction("approve");
        auditLog.setResourceType("approval");
        auditLog.setResourceId(approvalId);
        auditLog.setOldValue("pending");
        auditLog.setNewValue("approved");
        auditLogMapper.insert(auditLog);
        return approval;
    }

    @Override
    public Approval reject(String approvalId, String reviewedBy, String reason) {
        Approval approval = approvalMapper.selectById(approvalId);
        ThrowUtils.throwIf(approval == null, ErrorCode.NOT_FOUND_ERROR, "审批不存在");
        if (!"pending".equals(approval.getStatus())) {
            throw new BusinessException(ErrorCode.OPERATION_ERROR, "只有待审批状态的审批才能驳回");
        }
        approval.setStatus("rejected");
        approval.setReviewedBy(reviewedBy);
        approval.setReviewedAt(new java.util.Date());
        approval.setReason(reason);
        int result = approvalMapper.updateById(approval);
        ThrowUtils.throwIf(result <= 0, ErrorCode.OPERATION_ERROR, "审批驳回失败");
        AuditLog auditLog = new AuditLog();
        auditLog.setAction("reject");
        auditLog.setResourceType("approval");
        auditLog.setResourceId(approvalId);
        auditLog.setOldValue("pending");
        auditLog.setNewValue("rejected");
        auditLogMapper.insert(auditLog);
        return approval;
    }
}