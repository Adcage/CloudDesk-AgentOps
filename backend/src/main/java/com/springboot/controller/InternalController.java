package com.springboot.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.springboot.common.BaseResponse;
import com.springboot.common.ErrorCode;
import com.springboot.common.ResultUtils;
import com.springboot.exception.BusinessException;
import com.springboot.model.dto.auditlog.AuditLogQueryRequest;
import com.springboot.model.entity.Approval;
import com.springboot.model.entity.AuditLog;
import com.springboot.model.entity.Customer;
import com.springboot.model.entity.Order;
import com.springboot.model.entity.Ticket;
import com.springboot.model.vo.AuditLogVO;
import com.springboot.model.vo.CustomerVO;
import com.springboot.model.vo.OrderVO;
import com.springboot.model.vo.TicketVO;
import com.springboot.service.AuditLogService;
import com.springboot.service.ApprovalService;
import com.springboot.service.CustomerService;
import com.springboot.service.OrderService;
import com.springboot.service.TicketService;
import jakarta.annotation.Resource;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/internal")
@Slf4j
public class InternalController {

    @Value("${agent.service.token:clouddesk-internal-token}")
    private String internalToken;

    @Resource
    private CustomerService customerService;

    @Resource
    private OrderService orderService;

    @Resource
    private TicketService ticketService;

    @Resource
    private ApprovalService approvalService;

    @Resource
    private AuditLogService auditLogService;

    private void validateToken(String token) {
        if (StringUtils.isBlank(token) || !internalToken.equals(token)) {
            throw new BusinessException(ErrorCode.FORBIDDEN_ERROR, "内部接口认证失败");
        }
    }

    @GetMapping("/customers/{id}")
    public BaseResponse<CustomerVO> getCustomerById(
            @PathVariable String id,
            @RequestHeader("X-Internal-Token") String token) {
        validateToken(token);
        Customer customer = customerService.getById(id);
        CustomerVO vo = new CustomerVO();
        BeanUtils.copyProperties(customer, vo);
        return ResultUtils.success(vo);
    }

    @GetMapping("/customers/{id}/history")
    public BaseResponse<Map<String, Object>> getCustomerHistory(
            @PathVariable String id,
            @RequestHeader("X-Internal-Token") String token) {
        validateToken(token);
        Map<String, Object> history = customerService.getCustomerHistory(id);
        return ResultUtils.success(history);
    }

    @GetMapping("/orders/{id}")
    public BaseResponse<OrderVO> getOrderById(
            @PathVariable String id,
            @RequestHeader("X-Internal-Token") String token) {
        validateToken(token);
        Order order = orderService.getById(id);
        OrderVO vo = new OrderVO();
        BeanUtils.copyProperties(order, vo);
        return ResultUtils.success(vo);
    }

    @GetMapping("/tickets/customer/{id}")
    public BaseResponse<List<TicketVO>> getTicketsByCustomerId(
            @PathVariable String id,
            @RequestHeader("X-Internal-Token") String token) {
        validateToken(token);
        List<Ticket> tickets = customerService.getTicketsByCustomerId(id);
        List<TicketVO> voList = tickets.stream().map(ticket -> {
            TicketVO vo = new TicketVO();
            BeanUtils.copyProperties(ticket, vo);
            return vo;
        }).collect(Collectors.toList());
        return ResultUtils.success(voList);
    }

    @PostMapping("/tickets")
    public BaseResponse<TicketVO> createTicket(
            @RequestBody Ticket ticket,
            @RequestHeader("X-Internal-Token") String token) {
        validateToken(token);
        Ticket created = ticketService.createTicket(ticket);
        TicketVO vo = new TicketVO();
        BeanUtils.copyProperties(created, vo);
        return ResultUtils.success(vo);
    }

    @PostMapping("/approvals")
    public BaseResponse<Approval> createApproval(
            @RequestBody Approval approval,
            @RequestHeader("X-Internal-Token") String token) {
        validateToken(token);
        Approval created = approvalService.createApproval(approval);
        return ResultUtils.success(created);
    }

    @PostMapping("/audit-logs")
    public BaseResponse<AuditLog> createAuditLog(
            @RequestBody AuditLog auditLog,
            @RequestHeader("X-Internal-Token") String token) {
        validateToken(token);
        AuditLog created = auditLogService.create(auditLog);
        return ResultUtils.success(created);
    }
}