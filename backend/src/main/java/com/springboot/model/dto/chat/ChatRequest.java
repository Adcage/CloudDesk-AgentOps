package com.springboot.model.dto.chat;

import java.io.Serializable;
import lombok.Data;

@Data
public class ChatRequest implements Serializable {

    private String conversationId;

    private String message;

    private static final long serialVersionUID = 1L;
}