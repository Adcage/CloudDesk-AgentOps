package com.springboot.common;

import java.io.Serializable;
import lombok.Data;

@Data
public class DeleteRequest implements Serializable {
    private String id;
    private static final long serialVersionUID = 1L;
}