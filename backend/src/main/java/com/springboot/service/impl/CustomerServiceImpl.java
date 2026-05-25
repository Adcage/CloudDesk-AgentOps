package com.springboot.service.impl;

import com.springboot.common.ErrorCode;
import com.springboot.exception.BusinessException;
import com.springboot.exception.ThrowUtils;
import com.springboot.mapper.ApprovalMapper;
import com.springboot.mapper.CustomerMapper;
import com.springboot.mapper.OrderMapper;
import com.springboot.mapper.TicketMapper;
import com.springboot.model.entity.Customer;
import com.springboot.model.entity.Ticket;
import com.springboot.service.CustomerService;
import jakarta.annotation.Resource;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Service;

@Service
public class CustomerServiceImpl implements CustomerService {

    @Resource
    private CustomerMapper customerMapper;

    @Resource
    private TicketMapper ticketMapper;

    @Resource
    private OrderMapper orderMapper;

    @Resource
    private ApprovalMapper approvalMapper;

    @Override
    public Customer getById(String customerId) {
        Customer customer = customerMapper.selectById(customerId);
        ThrowUtils.throwIf(customer == null, ErrorCode.NOT_FOUND_ERROR, "客户不存在");
        return customer;
    }

    @Override
    public List<Ticket> getTicketsByCustomerId(String customerId) {
        com.baomidou.mybatisplus.core.conditions.query.QueryWrapper<Ticket> queryWrapper =
                new com.baomidou.mybatisplus.core.conditions.query.QueryWrapper<>();
        queryWrapper.eq("customer_id", customerId);
        queryWrapper.orderByDesc("created_at");
        return ticketMapper.selectList(queryWrapper);
    }

    @Override
    public Map<String, Object> getCustomerHistory(String customerId) {
        Customer customer = getById(customerId);
        long orderCount = orderMapper.selectCount(
                new com.baomidou.mybatisplus.core.conditions.query.QueryWrapper<com.springboot.model.entity.Order>()
                        .eq("customer_id", customerId));
        long ticketCount = ticketMapper.selectCount(
                new com.baomidou.mybatisplus.core.conditions.query.QueryWrapper<Ticket>()
                        .eq("customer_id", customerId));
        long approvalCount = approvalMapper.selectCount(
                new com.baomidou.mybatisplus.core.conditions.query.QueryWrapper<com.springboot.model.entity.Approval>()
                        .eq("customer_id", customerId));
        Map<String, Object> history = new HashMap<>();
        history.put("customer", customer);
        history.put("orderCount", orderCount);
        history.put("ticketCount", ticketCount);
        history.put("approvalCount", approvalCount);
        return history;
    }
}