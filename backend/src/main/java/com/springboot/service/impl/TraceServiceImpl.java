package com.springboot.service.impl;

import com.springboot.service.TraceService;
import jakarta.annotation.Resource;
import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class TraceServiceImpl implements TraceService {

    @Resource
    private RestTemplate restTemplate;

    @Value("${agent.service.url}")
    private String agentServiceUrl;

    @Override
    public Object getTraceById(String traceId) {
        String url = agentServiceUrl + "/agent/traces/" + traceId;
        ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);
        return extractData(response.getBody());
    }

    @Override
    public Object listTraces(int page, int pageSize) {
        String url = agentServiceUrl + "/agent/traces?page=" + page + "&page_size=" + pageSize;
        ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);
        return extractData(response.getBody());
    }

    @SuppressWarnings("unchecked")
    private Object extractData(Map<String, Object> responseBody) {
        if (responseBody == null) {
            return null;
        }
        Object dataObj = responseBody.get("data");
        if (dataObj instanceof Map) {
            return dataObj;
        }
        return responseBody;
    }
}