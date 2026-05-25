package com.springboot.service;

import com.springboot.model.entity.Order;

public interface OrderService {

    Order getById(String orderId);
}