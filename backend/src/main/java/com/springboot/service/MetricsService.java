package com.springboot.service;

import com.springboot.model.dto.metrics.DashboardMetrics;

public interface MetricsService {

    DashboardMetrics getDashboardMetrics(String userId, String userRole);
}
