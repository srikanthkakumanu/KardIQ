package com.example.cards.api.dto;

import java.time.Instant;

/**
 * Standard error shape shared across every KardIQ HTTP service.
 */
public record ApiError(
        String code,
        String message,
        String requestId,
        Instant timestamp
) {
}
