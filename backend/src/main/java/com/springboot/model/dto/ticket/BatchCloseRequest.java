package com.springboot.model.dto.ticket;

import lombok.Data;
import java.util.List;

@Data
public class BatchCloseRequest {

    private List<String> ticketIds;

    private String closureReason;
}
