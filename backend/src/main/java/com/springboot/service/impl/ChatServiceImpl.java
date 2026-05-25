package com.springboot.service.impl;

import com.springboot.model.dto.chat.ChatRequest;
import com.springboot.model.entity.AuditLog;
import com.springboot.model.vo.ChatResponseVO;
import com.springboot.model.vo.chat.CustomerContextVO;
import com.springboot.model.vo.chat.OrderContextVO;
import com.springboot.mapper.AuditLogMapper;
import com.springboot.service.AuditLogService;
import com.springboot.service.ChatService;
import jakarta.annotation.Resource;
import java.math.BigDecimal;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class ChatServiceImpl implements ChatService {

    @Resource
    private RestTemplate restTemplate;

    @Resource
    private AuditLogService auditLogService;

    @Value("${agent.service.url}")
    private String agentServiceUrl;

    private static final AtomicInteger traceCounter = new AtomicInteger(0);

    @Override
    public ChatResponseVO chat(ChatRequest request, String userId, String userRole) {
        String traceId = generateTraceId();
        String conversationId = request.getConversationId();
        if (conversationId == null || conversationId.isEmpty()) {
            conversationId = java.util.UUID.randomUUID().toString();
        }

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("trace_id", traceId);
        requestBody.put("conversation_id", conversationId);
        requestBody.put("user_id", userId);
        requestBody.put("user_role", userRole);
        requestBody.put("message", request.getMessage());

        String url = agentServiceUrl + "/agent/chat";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("X-Correlation-ID", traceId);

        HttpEntity<Map<String, Object>> httpEntity = new HttpEntity<>(requestBody, headers);

        ResponseEntity<Map> response = restTemplate.postForEntity(url, httpEntity, Map.class);
        ChatResponseVO chatResponse = convertAgentResponse(response.getBody());
        if (chatResponse != null) {
            chatResponse.setConversationId(conversationId);
        }

        AuditLog auditLog = new AuditLog();
        auditLog.setUserId(userId);
        auditLog.setAction("chat");
        auditLog.setResourceType("chat");
        auditLog.setResourceId(traceId);
        auditLog.setTraceId(traceId);
        if (chatResponse != null) {
            auditLog.setNewValue(chatResponse.getAnswer());
        }
        auditLogService.create(auditLog);

        return chatResponse;
    }

    private String generateTraceId() {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMdd");
        String datePart = sdf.format(new Date());
        int seq = traceCounter.incrementAndGet();
        return String.format("TR_%s_%03d", datePart, seq);
    }

    private ChatResponseVO convertAgentResponse(Map<String, Object> responseBody) {
        if (responseBody == null) {
            return null;
        }
        Object dataObj = responseBody.get("data");
        if (!(dataObj instanceof Map<?, ?> data)) {
            return null;
        }

        ChatResponseVO vo = new ChatResponseVO();
        vo.setConversationId((String) data.get("conversation_id"));
        vo.setAnswer((String) data.get("answer"));
        vo.setSelectedAgent((String) data.get("selected_agent"));
        vo.setApprovalRequired((Boolean) data.get("approval_required"));
        vo.setApprovalId((String) data.get("approval_id"));
        vo.setTraceId((String) data.get("trace_id"));

        Object citations = data.get("citations");
        if (citations instanceof List<?> citationList) {
            vo.setCitations((List<String>) citationList);
        }

        Object toolCalls = data.get("tool_calls");
        if (toolCalls instanceof List<?> toolCallList) {
            vo.setToolCalls((List<String>) toolCallList);
        }

        Object citationDetails = data.get("citation_details");
        vo.setCitationDetails(citationDetails);

        Object customerContext = data.get("customer_context");
        if (customerContext instanceof Map<?, ?> customerData) {
            CustomerContextVO customerVO = new CustomerContextVO();
            customerVO.setCustomerId(asString(customerData.get("customer_id")));
            customerVO.setCustomerName(asString(customerData.get("customer_name")));
            customerVO.setPlan(asString(customerData.get("plan")));
            customerVO.setRiskLevel(asString(customerData.get("risk_level")));
            vo.setCustomerContext(customerVO);
        }

        Object orderContext = data.get("order_context");
        if (orderContext instanceof Map<?, ?> orderData) {
            OrderContextVO orderVO = new OrderContextVO();
            orderVO.setOrderId(asString(orderData.get("order_id")));
            orderVO.setAmount(asBigDecimal(orderData.get("amount")));
            orderVO.setStatus(asString(orderData.get("status")));
            vo.setOrderContext(orderVO);
        }

        return vo;
    }

    private String asString(Object value) {
        return value == null ? "" : String.valueOf(value);
    }

    private BigDecimal asBigDecimal(Object value) {
        if (value == null) {
            return BigDecimal.ZERO;
        }
        try {
            return new BigDecimal(String.valueOf(value));
        } catch (NumberFormatException e) {
            return BigDecimal.ZERO;
        }
    }
}
