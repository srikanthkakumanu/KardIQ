package com.example.cards.api.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

import java.util.List;

public record CardRequest(
        @NotBlank @Size(max = 120) String title,
        @NotBlank @Size(max = 4000) String body,
        @Size(max = 8) List<@Size(max = 32) String> tags
) {
}
