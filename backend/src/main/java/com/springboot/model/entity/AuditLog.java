package com.springboot.model.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

@TableName(value = "business.audit_logs")
@Data
public class AuditLog implements Serializable {

    @TableId(type = IdType.ASSIGN_UUID)
    private String auditId;

    private String userId;

    private String action;

    private String resourceType;

    private String resourceId;

    private String oldValue;

    private String newValue;

    private String traceId;

    private Date createdAt;

    @TableField(exist = false)
    private static final long serialVersionUID = 1L;
}