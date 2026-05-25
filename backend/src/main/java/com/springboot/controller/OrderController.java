package com.springboot.controller;

import com.springboot.common.BaseResponse;
import com.springboot.common.ResultUtils;
import com.springboot.model.entity.Order;
import com.springboot.model.vo.OrderVO;
import com.springboot.service.OrderService;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/orders")
@Slf4j
public class OrderController {

    @Resource
    private OrderService orderService;

    @GetMapping("/{id}")
    public BaseResponse<OrderVO> getOrderById(@PathVariable String id) {
        Order order = orderService.getById(id);
        OrderVO orderVO = new OrderVO();
        BeanUtils.copyProperties(order, orderVO);
        return ResultUtils.success(orderVO);
    }
}