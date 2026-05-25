package com.springboot.model.dto.user;

import java.io.Serializable;
import lombok.Data;

@Data
public class UserUpdateMyRequest implements Serializable {

    private String username;

    private static final long serialVersionUID = 1L;
}
