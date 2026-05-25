package com.springboot.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.springboot.mapper.ApprovalMapper;
import com.springboot.mapper.TicketMapper;
import com.springboot.model.dto.metrics.DashboardMetrics;
import com.springboot.model.entity.Approval;
import com.springboot.model.entity.Ticket;
import com.springboot.service.MetricsService;
import org.springframework.stereotype.Service;

import jakarta.annotation.Resource;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.Date;
import java.util.List;

@Service
public class MetricsServiceImpl implements MetricsService {

    @Resource
    private TicketMapper ticketMapper;

    @Resource
    private ApprovalMapper approvalMapper;

    private QueryWrapper<Ticket> baseTicketQuery(String userId, String userRole) {
        QueryWrapper<Ticket> qw = new QueryWrapper<>();
        if ("support_agent".equals(userRole)) {
            qw.eq("assigned_to", userId);
        }
        return qw;
    }

    private QueryWrapper<Approval> baseApprovalQuery() {
        return new QueryWrapper<>();
    }

    @Override
    public DashboardMetrics getDashboardMetrics(String userId, String userRole) {
        DashboardMetrics metrics = new DashboardMetrics();

        metrics.setTotalTickets(ticketMapper.selectCount(baseTicketQuery(userId, userRole)));

        QueryWrapper<Ticket> openQw = baseTicketQuery(userId, userRole);
        openQw.in("status", "open", "in_progress");
        metrics.setOpenTickets(ticketMapper.selectCount(openQw));

        QueryWrapper<Ticket> overdueQw = baseTicketQuery(userId, userRole);
        overdueQw.lt("sla_deadline", new Date());
        overdueQw.in("status", "open", "in_progress");
        metrics.setOverdueTickets(ticketMapper.selectCount(overdueQw));

        metrics.setTotalApprovals(approvalMapper.selectCount(baseApprovalQuery()));

        QueryWrapper<Approval> pendingQw = baseApprovalQuery();
        pendingQw.eq("status", "pending");
        metrics.setPendingApprovals(approvalMapper.selectCount(pendingQw));

        QueryWrapper<Approval> highRiskQw = baseApprovalQuery();
        highRiskQw.ge("risk_score", 60);
        highRiskQw.eq("status", "pending");
        metrics.setHighRiskApprovals(approvalMapper.selectCount(highRiskQw));

        List<Ticket> allTickets = ticketMapper.selectList(baseTicketQuery(userId, userRole));
        long slaCompliantCount = allTickets.stream()
                .filter(t -> t.getResolvedAt() != null && t.getSlaDeadline() != null)
                .filter(t -> t.getResolvedAt().before(t.getSlaDeadline()))
                .count();
        long totalResolved = allTickets.stream()
                .filter(t -> t.getResolvedAt() != null && t.getSlaDeadline() != null)
                .count();
        if (totalResolved > 0) {
            metrics.setSlaComplianceRate(
                    BigDecimal.valueOf(slaCompliantCount * 100.0 / totalResolved)
                            .setScale(2, RoundingMode.HALF_UP)
            );
        } else {
            metrics.setSlaComplianceRate(BigDecimal.ZERO);
        }

        long totalResponseTime = allTickets.stream()
                .filter(t -> t.getFirstResponseAt() != null && t.getCreatedAt() != null)
                .mapToLong(t -> t.getFirstResponseAt().getTime() - t.getCreatedAt().getTime())
                .sum();
        long responseCount = allTickets.stream()
                .filter(t -> t.getFirstResponseAt() != null && t.getCreatedAt() != null)
                .count();
        if (responseCount > 0) {
            double avgHours = (totalResponseTime / (double) responseCount) / (1000.0 * 60 * 60);
            metrics.setAvgResponseTimeHours(
                    BigDecimal.valueOf(avgHours).setScale(2, RoundingMode.HALF_UP)
            );
        } else {
            metrics.setAvgResponseTimeHours(BigDecimal.ZERO);
        }

        long escalatedCount = allTickets.stream()
                .filter(t -> t.getEscalationCount() != null && t.getEscalationCount() > 0)
                .count();
        if (metrics.getTotalTickets() > 0) {
            metrics.setTicketEscalationRate(
                    BigDecimal.valueOf(escalatedCount * 100.0 / metrics.getTotalTickets())
                            .setScale(2, RoundingMode.HALF_UP)
            );
        } else {
            metrics.setTicketEscalationRate(BigDecimal.ZERO);
        }

        List<Approval> allApprovals = approvalMapper.selectList(baseApprovalQuery());
        long approvedCount = allApprovals.stream()
                .filter(a -> "approved".equals(a.getStatus()))
                .count();
        long processedCount = allApprovals.stream()
                .filter(a -> !"pending".equals(a.getStatus()))
                .count();
        if (processedCount > 0) {
            metrics.setApprovalApprovalRate(
                    BigDecimal.valueOf(approvedCount * 100.0 / processedCount)
                            .setScale(2, RoundingMode.HALF_UP)
            );
        } else {
            metrics.setApprovalApprovalRate(BigDecimal.ZERO);
        }

        Date todayStart = Date.from(LocalDate.now().atStartOfDay(ZoneId.systemDefault()).toInstant());
        Date todayEnd = Date.from(LocalDate.now().plusDays(1).atStartOfDay(ZoneId.systemDefault()).toInstant());

        QueryWrapper<Ticket> todayNewQw = baseTicketQuery(userId, userRole);
        todayNewQw.ge("created_at", todayStart);
        todayNewQw.lt("created_at", todayEnd);
        metrics.setTodayNewTickets(ticketMapper.selectCount(todayNewQw));

        QueryWrapper<Ticket> todayResolvedQw = baseTicketQuery(userId, userRole);
        todayResolvedQw.ge("resolved_at", todayStart);
        todayResolvedQw.lt("resolved_at", todayEnd);
        metrics.setTodayResolvedTickets(ticketMapper.selectCount(todayResolvedQw));

        QueryWrapper<Approval> todayNewApprovalQw = baseApprovalQuery();
        todayNewApprovalQw.ge("created_at", todayStart);
        todayNewApprovalQw.lt("created_at", todayEnd);
        metrics.setTodayNewApprovals(approvalMapper.selectCount(todayNewApprovalQw));

        QueryWrapper<Approval> todayProcessedQw = baseApprovalQuery();
        todayProcessedQw.ge("reviewed_at", todayStart);
        todayProcessedQw.lt("reviewed_at", todayEnd);
        metrics.setTodayProcessedApprovals(approvalMapper.selectCount(todayProcessedQw));

        return metrics;
    }
}
