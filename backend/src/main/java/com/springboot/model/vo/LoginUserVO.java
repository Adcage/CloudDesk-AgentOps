package com.springboot.model.vo;

import java.io.Serializable;
import java.util.Date;
import lombok.Data;

@Data
public class LoginUserVO implements Serializable {

    private String userId;

    private String username;

    private String userRole;

    private static final long serialVersionUID = 1L;
}