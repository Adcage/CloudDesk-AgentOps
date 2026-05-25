package com.springboot.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.springboot.model.dto.ticket.BatchAssignRequest;
import com.springboot.model.dto.ticket.BatchCloseRequest;
import com.springboot.model.dto.ticket.TicketQueryRequest;
import com.springboot.model.entity.Ticket;

import java.util.List;

public interface TicketService {

    Page<Ticket> listPage(TicketQueryRequest request);

    Ticket getById(String ticketId);

    Ticket createTicket(Ticket ticket);

    List<Ticket> getMyTodos(String userId);

    int batchAssign(BatchAssignRequest request);

    int batchClose(BatchCloseRequest request);
}