package com.springboot.model.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.io.Serializable;
import java.math.BigDecimal;
import java.util.Date;
import lombok.Data;

@TableName(value = "business.approvals")
@Data
public class Approval implements Serializable {

    @TableId(type = IdType.ASSIGN_UUID)
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

    private Date slaDeadline;

    private Integer approvalLevel;

    private BigDecimal riskScore;

    @TableField(exist = false)
    private static final long serialVersionUID = 1L;
}