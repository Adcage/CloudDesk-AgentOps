package com.springboot.model.vo.chat;

import java.io.Serializable;
import java.math.BigDecimal;
import lombok.Data;

@Data
public class OrderContextVO implements Serializable {

    private String orderId;

    private BigDecimal amount;

    private String status;

    private static final long serialVersionUID = 1L;
}
