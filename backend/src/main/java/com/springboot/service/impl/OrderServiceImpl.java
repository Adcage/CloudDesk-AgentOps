package com.springboot.service.impl;

import com.springboot.common.ErrorCode;
import com.springboot.exception.ThrowUtils;
import com.springboot.mapper.OrderMapper;
import com.springboot.model.entity.Order;
import com.springboot.service.OrderService;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;

@Service
public class OrderServiceImpl implements OrderService {

    @Resource
    private OrderMapper orderMapper;

    @Override
    public Order getById(String orderId) {
        Order order = orderMapper.selectById(orderId);
        ThrowUtils.throwIf(order == null, ErrorCode.NOT_FOUND_ERROR, "订单不存在");
        return order;
    }
}