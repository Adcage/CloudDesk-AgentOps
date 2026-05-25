package com.springboot.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.springboot.model.dto.approval.ApprovalQueryRequest;
import com.springboot.model.entity.Approval;

public interface ApprovalService {

    Page<Approval> listPage(ApprovalQueryRequest request);

    Approval createApproval(Approval approval);

    Approval approve(String approvalId, String reviewedBy);

    Approval reject(String approvalId, String reviewedBy, String reason);
}