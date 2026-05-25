package com.springboot.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.springboot.common.ErrorCode;
import com.springboot.exception.ThrowUtils;
import com.springboot.mapper.AuditLogMapper;
import com.springboot.mapper.TicketMapper;
import com.springboot.model.dto.ticket.BatchAssignRequest;
import com.springboot.model.dto.ticket.BatchCloseRequest;
import com.springboot.model.dto.ticket.TicketQueryRequest;
import com.springboot.model.entity.AuditLog;
import com.springboot.model.entity.Ticket;
import com.springboot.service.TicketService;
import jakarta.annotation.Resource;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;

import java.util.Date;
import java.util.List;

@Service
public class TicketServiceImpl implements TicketService {

    @Resource
    private TicketMapper ticketMapper;

    @Resource
    private AuditLogMapper auditLogMapper;

    @Override
    public Page<Ticket> listPage(TicketQueryRequest request) {
        long current = request.getCurrent();
        long size = request.getPageSize();
        QueryWrapper<Ticket> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq(StringUtils.isNotBlank(request.getStatus()), "status", request.getStatus());
        queryWrapper.eq(StringUtils.isNotBlank(request.getCategory()), "category", request.getCategory());
        queryWrapper.eq(StringUtils.isNotBlank(request.getPriority()), "priority", request.getPriority());
        queryWrapper.orderByDesc("created_at");
        return ticketMapper.selectPage(new Page<>(current, size), queryWrapper);
    }

    @Override
    public Ticket getById(String ticketId) {
        Ticket ticket = ticketMapper.selectById(ticketId);
        ThrowUtils.throwIf(ticket == null, ErrorCode.NOT_FOUND_ERROR, "工单不存在");
        return ticket;
    }

    @Override
    public Ticket createTicket(Ticket ticket) {
        int result = ticketMapper.insert(ticket);
        ThrowUtils.throwIf(result <= 0, ErrorCode.OPERATION_ERROR, "创建工单失败");
        AuditLog auditLog = new AuditLog();
        auditLog.setAction("create_ticket");
        auditLog.setResourceType("ticket");
        auditLog.setResourceId(ticket.getTicketId());
        auditLog.setTraceId(ticket.getTraceId());
        auditLog.setNewValue(ticket.getSubject());
        auditLogMapper.insert(auditLog);
        return ticket;
    }

    @Override
    public List<Ticket> getMyTodos(String userId) {
        QueryWrapper<Ticket> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("assigned_to", userId);
        queryWrapper.in("status", "open", "in_progress");
        queryWrapper.orderByAsc("sla_deadline");
        return ticketMapper.selectList(queryWrapper);
    }

    @Override
    public int batchAssign(BatchAssignRequest request) {
        int count = 0;
        for (String ticketId : request.getTicketIds()) {
            Ticket ticket = new Ticket();
            ticket.setTicketId(ticketId);
            ticket.setAssignedTo(request.getAssignedTo());
            ticket.setUpdatedAt(new Date());
            count += ticketMapper.updateById(ticket);
        }
        return count;
    }

    @Override
    public int batchClose(BatchCloseRequest request) {
        int count = 0;
        for (String ticketId : request.getTicketIds()) {
            Ticket ticket = new Ticket();
            ticket.setTicketId(ticketId);
            ticket.setStatus("closed");
            ticket.setResolvedAt(new Date());
            ticket.setUpdatedAt(new Date());
            count += ticketMapper.updateById(ticket);
        }
        return count;
    }
}