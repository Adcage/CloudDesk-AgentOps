package com.springboot.controller;

import com.springboot.common.BaseResponse;
import com.springboot.common.ResultUtils;
import com.springboot.model.entity.Customer;
import com.springboot.model.vo.CustomerVO;
import com.springboot.service.CustomerService;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/customers")
@Slf4j
public class CustomerController {

    @Resource
    private CustomerService customerService;

    @GetMapping("/{id}")
    public BaseResponse<CustomerVO> getCustomerById(@PathVariable String id) {
        Customer customer = customerService.getById(id);
        CustomerVO customerVO = new CustomerVO();
        BeanUtils.copyProperties(customer, customerVO);
        return ResultUtils.success(customerVO);
    }
}