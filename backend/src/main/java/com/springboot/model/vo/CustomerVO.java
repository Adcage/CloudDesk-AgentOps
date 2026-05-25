package com.springboot.model.vo;

import java.io.Serializable;
import java.util.Date;
import lombok.Data;

@Data
public class CustomerVO implements Serializable {

    private String customerId;

    private String name;

    private String email;

    private String plan;

    private String status;

    private String riskLevel;

    private Date createdAt;

    private Date updatedAt;

    private String contactName;

    private String phone;

    private Date lastActiveAt;

    private static final long serialVersionUID = 1L;
}