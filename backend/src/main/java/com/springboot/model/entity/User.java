package com.springboot.model.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

@TableName(value = "business.users")
@Data
public class User implements Serializable {

    @TableId(type = IdType.ASSIGN_UUID)
    private String userId;

    private String username;

    private String password;

    @TableField("role")
    private String userRole;

    @TableField("created_at")
    private Date createTime;

    @TableField("updated_at")
    private Date updateTime;

    @TableField(exist = false)
    private static final long serialVersionUID = 1L;
}
