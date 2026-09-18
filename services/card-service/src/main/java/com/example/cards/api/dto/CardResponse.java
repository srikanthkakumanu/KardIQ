package com.example.cards.api.dto;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

public record CardResponse(
        UUID id,
        String title,
        String body,
        List<String> tags,
        Instant createdAt,
        Instant updatedAt
) {
}
