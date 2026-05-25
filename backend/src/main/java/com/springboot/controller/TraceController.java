package com.springboot.controller;

import com.springboot.common.BaseResponse;
import com.springboot.common.ResultUtils;
import com.springboot.service.TraceService;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/traces")
@Slf4j
public class TraceController {

    @Resource
    private TraceService traceService;

    @GetMapping
    public BaseResponse<Object> listTraces(
            @RequestParam(defaultValue = "1") int current,
            @RequestParam(defaultValue = "10") int pageSize) {
        Object traces = traceService.listTraces(current, pageSize);
        return ResultUtils.success(traces);
    }

    @GetMapping("/{id}")
    public BaseResponse<Object> getTraceById(@PathVariable String id) {
        Object trace = traceService.getTraceById(id);
        return ResultUtils.success(trace);
    }
}