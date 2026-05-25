package com.springboot.model.dto.metrics;

import lombok.Data;
import java.math.BigDecimal;

@Data
public class DashboardMetrics {

    private Long totalTickets;

    private Long openTickets;

    private Long overdueTickets;

    private Long totalApprovals;

    private Long pendingApprovals;

    private Long highRiskApprovals;

    private BigDecimal slaComplianceRate;

    private BigDecimal avgResponseTimeHours;

    private BigDecimal ticketEscalationRate;

    private BigDecimal approvalApprovalRate;

    private Long todayNewTickets;

    private Long todayResolvedTickets;

    private Long todayNewApprovals;

    private Long todayProcessedApprovals;
}
