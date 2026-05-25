package com.springboot.service;

public interface TraceService {

    Object getTraceById(String traceId);

    Object listTraces(int page, int pageSize);
}