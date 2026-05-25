package com.springboot.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.springboot.common.BaseResponse;
import com.springboot.common.ResultUtils;
import com.springboot.model.dto.ticket.BatchAssignRequest;
import com.springboot.model.dto.ticket.BatchCloseRequest;
import com.springboot.model.dto.ticket.TicketQueryRequest;
import com.springboot.model.entity.Ticket;
import com.springboot.model.vo.TicketVO;
import com.springboot.service.TicketService;
import jakarta.annotation.Resource;
import java.util.List;
import java.util.stream.Collectors;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/tickets")
@Slf4j
public class TicketController {

    @Resource
    private TicketService ticketService;

    @GetMapping
    public BaseResponse<Page<TicketVO>> listTickets(TicketQueryRequest request) {
        Page<Ticket> ticketPage = ticketService.listPage(request);
        Page<TicketVO> voPage = new Page<>(ticketPage.getCurrent(), ticketPage.getSize(), ticketPage.getTotal());
        List<TicketVO> voList = ticketPage.getRecords().stream().map(ticket -> {
            TicketVO vo = new TicketVO();
            BeanUtils.copyProperties(ticket, vo);
            return vo;
        }).collect(Collectors.toList());
        voPage.setRecords(voList);
        return ResultUtils.success(voPage);
    }

    @GetMapping("/{id}")
    public BaseResponse<TicketVO> getTicketById(@PathVariable String id) {
        Ticket ticket = ticketService.getById(id);
        TicketVO vo = new TicketVO();
        BeanUtils.copyProperties(ticket, vo);
        return ResultUtils.success(vo);
    }

    @GetMapping("/my-todos")
    public BaseResponse<List<TicketVO>> getMyTodos(@RequestParam String userId) {
        List<Ticket> tickets = ticketService.getMyTodos(userId);
        List<TicketVO> voList = tickets.stream().map(ticket -> {
            TicketVO vo = new TicketVO();
            BeanUtils.copyProperties(ticket, vo);
            return vo;
        }).collect(Collectors.toList());
        return ResultUtils.success(voList);
    }

    @PostMapping("/batch/assign")
    public BaseResponse<Integer> batchAssign(@RequestBody BatchAssignRequest request) {
        int count = ticketService.batchAssign(request);
        return ResultUtils.success(count);
    }

    @PostMapping("/batch/close")
    public BaseResponse<Integer> batchClose(@RequestBody BatchCloseRequest request) {
        int count = ticketService.batchClose(request);
        return ResultUtils.success(count);
    }
}