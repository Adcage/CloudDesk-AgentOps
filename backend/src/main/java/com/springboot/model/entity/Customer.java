package com.springboot.model.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

@TableName(value = "business.customers")
@Data
public class Customer implements Serializable {

    @TableId(type = IdType.ASSIGN_UUID)
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

    @TableField(exist = false)
    private static final long serialVersionUID = 1L;
}