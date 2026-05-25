package com.springboot.model.vo.chat;

import java.io.Serializable;
import lombok.Data;

@Data
public class CustomerContextVO implements Serializable {

    private String customerId;

    private String customerName;

    private String plan;

    private String riskLevel;

    private static final long serialVersionUID = 1L;
}
