package com.springboot.model.dto.approval;

import java.io.Serializable;
import lombok.Data;

@Data
public class ApprovalApproveRequest implements Serializable {

    private String reviewedBy;

    private static final long serialVersionUID = 1L;
}