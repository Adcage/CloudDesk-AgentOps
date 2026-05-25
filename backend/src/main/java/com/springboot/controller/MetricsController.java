package com.springboot.controller;

import com.springboot.common.BaseResponse;
import com.springboot.common.ResultUtils;
import com.springboot.model.dto.metrics.DashboardMetrics;
import com.springboot.service.MetricsService;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/metrics")
@Slf4j
public class MetricsController {

    @Resource
    private MetricsService metricsService;

    @GetMapping("/dashboard")
    public BaseResponse<DashboardMetrics> getDashboardMetrics(
            @RequestParam(required = false) String userId,
            @RequestParam(required = false, defaultValue = "admin") String userRole) {
        DashboardMetrics metrics = metricsService.getDashboardMetrics(userId, userRole);
        return ResultUtils.success(metrics);
    }
}
