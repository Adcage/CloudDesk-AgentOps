package com.springboot.model.vo;

import java.io.Serializable;
import java.util.Date;
import lombok.Data;

@Data
public class AuditLogVO implements Serializable {

    private String auditId;

    private String userId;

    private String action;

    private String resourceType;

    private String resourceId;

    private String oldValue;

    private String newValue;

    private String traceId;

    private Date createdAt;

    private static final long serialVersionUID = 1L;
}