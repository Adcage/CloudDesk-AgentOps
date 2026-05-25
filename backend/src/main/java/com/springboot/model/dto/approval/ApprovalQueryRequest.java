package com.springboot.model.dto.approval;

import com.springboot.common.PageRequest;
import java.io.Serializable;
import lombok.Data;
import lombok.EqualsAndHashCode;

@EqualsAndHashCode(callSuper = true)
@Data
public class ApprovalQueryRequest extends PageRequest implements Serializable {

    private String status;

    private static final long serialVersionUID = 1L;
}