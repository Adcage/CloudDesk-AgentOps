package com.springboot.model.dto.user;

import java.io.Serializable;
import lombok.Data;

@Data
public class UserAddRequest implements Serializable {
    private String username;
    private String userRole;
    private static final long serialVersionUID = 1L;
}
