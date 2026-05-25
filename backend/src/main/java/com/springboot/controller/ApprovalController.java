package com.springboot.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.springboot.common.BaseResponse;
import com.springboot.common.ErrorCode;
import com.springboot.common.ResultUtils;
import com.springboot.exception.BusinessException;
import com.springboot.model.dto.approval.ApprovalApproveRequest;
import com.springboot.model.dto.approval.ApprovalQueryRequest;
import com.springboot.model.dto.approval.ApprovalRejectRequest;
import com.springboot.model.entity.Approval;
import com.springboot.model.vo.ApprovalVO;
import com.springboot.service.ApprovalService;
import jakarta.annotation.Resource;
import java.util.List;
import java.util.stream.Collectors;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/approvals")
@Slf4j
public class ApprovalController {

    @Resource
    private ApprovalService approvalService;

    @GetMapping
    public BaseResponse<Page<ApprovalVO>> listApprovals(ApprovalQueryRequest request) {
        Page<Approval> approvalPage = approvalService.listPage(request);
        Page<ApprovalVO> voPage = new Page<>(approvalPage.getCurrent(), approvalPage.getSize(), approvalPage.getTotal());
        List<ApprovalVO> voList = approvalPage.getRecords().stream().map(approval -> {
            ApprovalVO vo = new ApprovalVO();
            BeanUtils.copyProperties(approval, vo);
            return vo;
        }).collect(Collectors.toList());
        voPage.setRecords(voList);
        return ResultUtils.success(voPage);
    }

    @PostMapping("/{id}/approve")
    public BaseResponse<ApprovalVO> approve(@PathVariable String id, @RequestBody ApprovalApproveRequest request) {
        if (request == null || request.getReviewedBy() == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR);
        }
        Approval approval = approvalService.approve(id, request.getReviewedBy());
        ApprovalVO vo = new ApprovalVO();
        BeanUtils.copyProperties(approval, vo);
        return ResultUtils.success(vo);
    }

    @PostMapping("/{id}/reject")
    public BaseResponse<ApprovalVO> reject(@PathVariable String id, @RequestBody ApprovalRejectRequest request) {
        if (request == null || request.getReviewedBy() == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR);
        }
        Approval approval = approvalService.reject(id, request.getReviewedBy(), request.getReason());
        ApprovalVO vo = new ApprovalVO();
        BeanUtils.copyProperties(approval, vo);
        return ResultUtils.success(vo);
    }
}