package com.example.cards.api.dto;

import java.util.List;

public record CardPageResponse(
        List<CardResponse> items,
        int page,
        int size,
        long totalElements
) {
}
