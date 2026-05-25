package com.springboot.model.dto.ticket;

import com.springboot.common.PageRequest;
import java.io.Serializable;
import lombok.Data;
import lombok.EqualsAndHashCode;

@EqualsAndHashCode(callSuper = true)
@Data
public class TicketQueryRequest extends PageRequest implements Serializable {

    private String status;

    private String category;

    private String priority;

    private static final long serialVersionUID = 1L;
}