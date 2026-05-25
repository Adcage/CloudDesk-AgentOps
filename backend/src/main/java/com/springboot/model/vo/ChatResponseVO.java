package com.springboot.model.vo;

import com.springboot.model.vo.chat.CustomerContextVO;
import com.springboot.model.vo.chat.OrderContextVO;
import java.io.Serializable;
import java.util.List;
import lombok.Data;

@Data
public class ChatResponseVO implements Serializable {

    private String conversationId;

    private String answer;

    private String selectedAgent;

    private List<String> citations;

    private List<String> toolCalls;

    private Boolean approvalRequired;

    private String approvalId;

    private String traceId;

    private Object citationDetails;

    private CustomerContextVO customerContext;

    private OrderContextVO orderContext;

    private static final long serialVersionUID = 1L;
}
