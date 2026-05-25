package com.springboot.config;

import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

@Component
@Slf4j
public class DatabaseMigration {

    private final DataSource dataSource;

    public DatabaseMigration(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @PostConstruct
    public void runMigrations() {
        try (Connection conn = dataSource.getConnection()) {
            ensureTicketColumns(conn);
            ensureApprovalColumns(conn);
            ensureCustomerColumns(conn);
            log.info("Database migration check completed");
        } catch (Exception e) {
            log.warn("Database migration skipped: {}", e.getMessage());
        }
    }

    private void ensureTicketColumns(Connection conn) {
        List<String> missing = new ArrayList<>();
        missing.addAll(checkMissing(conn, "business", "tickets",
                "order_id", "VARCHAR(64)"));
        missing.addAll(checkMissing(conn, "business", "tickets",
                "description", "TEXT"));
        missing.addAll(checkMissing(conn, "business", "tickets",
                "sla_deadline", "TIMESTAMP"));
        missing.addAll(checkMissing(conn, "business", "tickets",
                "first_response_at", "TIMESTAMP"));
        missing.addAll(checkMissing(conn, "business", "tickets",
                "resolved_at", "TIMESTAMP"));
        missing.addAll(checkMissing(conn, "business", "tickets",
                "escalation_count", "INTEGER DEFAULT 0"));
        missing.addAll(checkMissing(conn, "business", "tickets",
                "assigned_to", "VARCHAR(64)"));

        for (String sql : missing) {
            execute(conn, sql);
        }
        if (!missing.isEmpty()) {
            log.info("Added {} missing columns to business.tickets", missing.size());
        }
    }

    private void ensureApprovalColumns(Connection conn) {
        List<String> missing = new ArrayList<>();
        missing.addAll(checkMissing(conn, "business", "approvals",
                "order_id", "VARCHAR(64)"));
        missing.addAll(checkMissing(conn, "business", "approvals",
                "sla_deadline", "TIMESTAMP"));
        missing.addAll(checkMissing(conn, "business", "approvals",
                "approval_level", "INTEGER DEFAULT 1"));
        missing.addAll(checkMissing(conn, "business", "approvals",
                "risk_score", "NUMERIC(5,2) DEFAULT 0"));

        for (String sql : missing) {
            execute(conn, sql);
        }
        if (!missing.isEmpty()) {
            log.info("Added {} missing columns to business.approvals", missing.size());
        }
    }

    private void ensureCustomerColumns(Connection conn) {
        List<String> missing = new ArrayList<>();
        missing.addAll(checkMissing(conn, "business", "customers",
                "contact_name", "VARCHAR(100)"));
        missing.addAll(checkMissing(conn, "business", "customers",
                "phone", "VARCHAR(20)"));
        missing.addAll(checkMissing(conn, "business", "customers",
                "last_active_at", "TIMESTAMP"));

        for (String sql : missing) {
            execute(conn, sql);
        }
        if (!missing.isEmpty()) {
            log.info("Added {} missing columns to business.customers", missing.size());
        }
    }

    private List<String> checkMissing(Connection conn, String schema, String table, String column, String columnDef) {
        List<String> results = new ArrayList<>();
        String sql = String.format(
                "SELECT 1 FROM information_schema.columns WHERE table_schema='%s' AND table_name='%s' AND column_name='%s'",
                schema, table, column);
        try (Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            if (!rs.next()) {
                results.add(String.format("ALTER TABLE %s.%s ADD COLUMN %s %s", schema, table, column, columnDef));
            }
        } catch (Exception e) {
            log.warn("Failed to check column {}.{}: {}", table, column, e.getMessage());
        }
        return results;
    }

    private void execute(Connection conn, String sql) {
        try (Statement stmt = conn.createStatement()) {
            stmt.execute(sql);
            log.info("Executed: {}", sql);
        } catch (Exception e) {
            log.warn("Failed to execute: {} - {}", sql, e.getMessage());
        }
    }
}
