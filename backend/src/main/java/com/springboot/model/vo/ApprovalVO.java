package com.springboot.model.vo;

import java.io.Serializable;
import java.math.BigDecimal;
import java.util.Date;
import lombok.Data;

@Data
public class ApprovalVO implements Serializable {

    private String approvalId;

    private String customerId;

    private String orderId;

    private String action;

    private BigDecimal amount;

    private String reason;

    private String status;

    private String requestedBy;

    private String reviewedBy;

    private String traceId;

    private Date createdAt;

    private Date reviewedAt;

    private Date updatedAt;

    private static final long serialVersionUID = 1L;
}