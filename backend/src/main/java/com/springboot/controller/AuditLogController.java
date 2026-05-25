package com.springboot.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.springboot.common.BaseResponse;
import com.springboot.common.ResultUtils;
import com.springboot.model.dto.auditlog.AuditLogQueryRequest;
import com.springboot.model.entity.AuditLog;
import com.springboot.model.vo.AuditLogVO;
import com.springboot.service.AuditLogService;
import jakarta.annotation.Resource;
import java.util.List;
import java.util.stream.Collectors;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/audit-logs")
@Slf4j
public class AuditLogController {

    @Resource
    private AuditLogService auditLogService;

    @GetMapping
    public BaseResponse<Page<AuditLogVO>> listAuditLogs(AuditLogQueryRequest request) {
        Page<AuditLog> auditLogPage = auditLogService.listPage(request);
        Page<AuditLogVO> voPage = new Page<>(auditLogPage.getCurrent(), auditLogPage.getSize(), auditLogPage.getTotal());
        List<AuditLogVO> voList = auditLogPage.getRecords().stream().map(auditLog -> {
            AuditLogVO vo = new AuditLogVO();
            BeanUtils.copyProperties(auditLog, vo);
            return vo;
        }).collect(Collectors.toList());
        voPage.setRecords(voList);
        return ResultUtils.success(voPage);
    }
}