package com.springboot.model.vo;

import java.io.Serializable;
import java.math.BigDecimal;
import java.util.Date;
import lombok.Data;

@Data
public class OrderVO implements Serializable {

    private String orderId;

    private String customerId;

    private BigDecimal amount;

    private String status;

    private String issueType;

    private Date createdAt;

    private Date updatedAt;

    private static final long serialVersionUID = 1L;
}