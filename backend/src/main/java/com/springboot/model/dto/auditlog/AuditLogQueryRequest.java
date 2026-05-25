package com.springboot.model.dto.auditlog;

import com.springboot.common.PageRequest;
import java.io.Serializable;
import lombok.Data;
import lombok.EqualsAndHashCode;

@EqualsAndHashCode(callSuper = true)
@Data
public class AuditLogQueryRequest extends PageRequest implements Serializable {

    private static final long serialVersionUID = 1L;
}