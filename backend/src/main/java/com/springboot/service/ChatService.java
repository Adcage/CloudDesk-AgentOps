package com.springboot.service;

import com.springboot.model.dto.chat.ChatRequest;
import com.springboot.model.vo.ChatResponseVO;

public interface ChatService {

    ChatResponseVO chat(ChatRequest request, String userId, String userRole);
}