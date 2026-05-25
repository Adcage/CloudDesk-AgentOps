package com.springboot.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.springboot.common.BaseResponse;
import com.springboot.common.ResultUtils;
import com.springboot.model.dto.chat.ChatRequest;
import com.springboot.model.entity.User;
import com.springboot.model.vo.ChatResponseVO;
import com.springboot.service.ChatService;
import com.springboot.service.UserService;
import jakarta.annotation.Resource;
import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

@RestController
@RequestMapping("/chat")
@Slf4j
public class ChatController {

    @Resource
    private ChatService chatService;

    @Resource
    private UserService userService;

    private final ObjectMapper objectMapper = new ObjectMapper();
    private final ExecutorService streamExecutor = Executors.newCachedThreadPool();

    @PostMapping
    public BaseResponse<ChatResponseVO> chat(@RequestBody ChatRequest request, HttpServletRequest httpRequest) {
        User loginUser = userService.getLoginUser(httpRequest);
        ChatResponseVO response = chatService.chat(request, loginUser.getUserId(), loginUser.getUserRole());
        return ResultUtils.success(response);
    }

    @PostMapping("/stream")
    public SseEmitter chatStream(@RequestBody ChatRequest request, HttpServletRequest httpRequest) {
        User loginUser = userService.getLoginUser(httpRequest);
        SseEmitter emitter = new SseEmitter(0L);

        streamExecutor.execute(() -> {
            try {
                ChatResponseVO response = chatService.chat(request, loginUser.getUserId(), loginUser.getUserRole());
                if (response == null) {
                    sendEvent(emitter, "chunk", "{\"type\":\"chunk\",\"content\":\"未获取到有效回复\"}");
                    sendDoneEvent(emitter, null, null);
                    emitter.complete();
                    return;
                }

                String answer = response.getAnswer() != null ? response.getAnswer() : "";
                for (int i = 0; i < answer.length(); i++) {
                    String chunk = answer.substring(i, Math.min(i + 3, answer.length()));
                    sendEvent(emitter, "chunk", objectMapper.writeValueAsString(Map.of("type", "chunk", "content", chunk)));
                    i += 2;
                    Thread.sleep(20);
                }

                Map<String, Object> doneData = new HashMap<>();
                doneData.put("type", "done");
                doneData.put("answer", answer);
                doneData.put("conversationId", response.getConversationId());
                doneData.put("traceId", response.getTraceId());
                doneData.put("selectedAgent", response.getSelectedAgent());
                doneData.put("citations", response.getCitations());
                doneData.put("toolCalls", response.getToolCalls());
                doneData.put("approvalRequired", response.getApprovalRequired());
                doneData.put("approvalId", response.getApprovalId());
                doneData.put("citationDetails", response.getCitationDetails());
                if (response.getCustomerContext() != null) {
                    Map<String, Object> customer = new HashMap<>();
                    customer.put("customer_id", response.getCustomerContext().getCustomerId());
                    customer.put("customer_name", response.getCustomerContext().getCustomerName());
                    customer.put("plan", response.getCustomerContext().getPlan());
                    customer.put("risk_level", response.getCustomerContext().getRiskLevel());
                    doneData.put("customerContext", customer);
                }
                if (response.getOrderContext() != null) {
                    Map<String, Object> order = new HashMap<>();
                    order.put("order_id", response.getOrderContext().getOrderId());
                    order.put("amount", response.getOrderContext().getAmount());
                    order.put("status", response.getOrderContext().getStatus());
                    doneData.put("orderContext", order);
                }
                sendEvent(emitter, "done", objectMapper.writeValueAsString(doneData));
                emitter.complete();
            } catch (Exception e) {
                log.error("SSE stream error", e);
                try {
                    sendEvent(emitter, "error", "{\"type\":\"error\",\"message\":\"流式响应异常\"}");
                } catch (Exception ignored) {}
                emitter.completeWithError(e);
            }
        });

        return emitter;
    }

    private void sendEvent(SseEmitter emitter, String eventName, String data) {
        try {
            emitter.send(SseEmitter.event().name(eventName).data(data, MediaType.APPLICATION_JSON));
        } catch (Exception e) {
            log.warn("Failed to send SSE event: {}", e.getMessage());
        }
    }

    private void sendDoneEvent(SseEmitter emitter, String conversationId, String traceId) {
        Map<String, Object> done = new HashMap<>();
        done.put("type", "done");
        if (conversationId != null) done.put("conversationId", conversationId);
        if (traceId != null) done.put("traceId", traceId);
        try {
            sendEvent(emitter, "done", objectMapper.writeValueAsString(done));
        } catch (Exception e) {
            log.warn("Failed to send done event: {}", e.getMessage());
        }
    }
}