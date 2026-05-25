package com.springboot.model.dto.approval;

import java.io.Serializable;
import lombok.Data;

@Data
public class ApprovalRejectRequest implements Serializable {

    private String reviewedBy;

    private String reason;

    private static final long serialVersionUID = 1L;
}