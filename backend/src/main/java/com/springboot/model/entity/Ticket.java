package com.springboot.model.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

@TableName(value = "business.tickets")
@Data
public class Ticket implements Serializable {

    @TableId(type = IdType.ASSIGN_UUID)
    private String ticketId;

    private String customerId;

    private String subject;

    private String category;

    private String priority;

    private String status;

    private String agentSummary;

    private String traceId;

    private Date createdAt;

    private Date updatedAt;

    private String orderId;

    private String description;

    private Date slaDeadline;

    private Date firstResponseAt;

    private Date resolvedAt;

    private Integer escalationCount;

    private String assignedTo;

    @TableField(exist = false)
    private static final long serialVersionUID = 1L;
}