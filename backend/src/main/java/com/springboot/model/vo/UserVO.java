package com.springboot.model.vo;

import java.io.Serializable;
import java.util.Date;
import lombok.Data;

@Data
public class UserVO implements Serializable {

    private String userId;

    private String username;

    private String userRole;

    private Date createTime;

    private static final long serialVersionUID = 1L;
}