package com.springboot.service;

import com.springboot.model.entity.Customer;
import com.springboot.model.entity.Ticket;
import java.util.List;
import java.util.Map;

public interface CustomerService {

    Customer getById(String customerId);

    List<Ticket> getTicketsByCustomerId(String customerId);

    Map<String, Object> getCustomerHistory(String customerId);
}