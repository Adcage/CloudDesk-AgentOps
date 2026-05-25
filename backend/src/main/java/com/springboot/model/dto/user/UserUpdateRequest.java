package com.springboot.model.dto.user;

import java.io.Serializable;
import lombok.Data;

@Data
public class UserUpdateRequest implements Serializable {
    private String userId;
    private String username;
    private String userRole;
    private static final long serialVersionUID = 1L;
}
