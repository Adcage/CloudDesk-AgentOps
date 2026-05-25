package com.springboot.model.dto.ticket;

import lombok.Data;
import java.util.List;

@Data
public class BatchAssignRequest {

    private List<String> ticketIds;

    private String assignedTo;
}
