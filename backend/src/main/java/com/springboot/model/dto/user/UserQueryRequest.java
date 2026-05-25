package com.springboot.model.dto.user;

import com.springboot.common.PageRequest;
import java.io.Serializable;
import lombok.Data;
import lombok.EqualsAndHashCode;

@EqualsAndHashCode(callSuper = true)
@Data
public class UserQueryRequest extends PageRequest implements Serializable {
    private String userId;
    private String username;
    private String userRole;
    private static final long serialVersionUID = 1L;
}
