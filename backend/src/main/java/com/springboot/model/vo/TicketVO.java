package com.springboot.model.vo;

import java.io.Serializable;
import java.util.Date;
import lombok.Data;

@Data
public class TicketVO implements Serializable {

    private String ticketId;

    private String customerId;

    private String subject;

    private String category;

    private String priority;

    private String status;

    private String agentSummary;

    private String traceId;

    private Date createdAt;

    private Date updatedAt;

    private static final long serialVersionUID = 1L;
}