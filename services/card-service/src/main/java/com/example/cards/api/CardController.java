package com.example.cards.api;

import com.example.cards.api.dto.CardPageResponse;
import com.example.cards.api.dto.CardRequest;
import com.example.cards.api.dto.CardResponse;
import com.example.cards.application.CardService;
import io.swagger.v3.oas.annotations.Operation;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.net.URI;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/cards")
public class CardController {

    private final CardService cardService;

    public CardController(CardService cardService) {
        this.cardService = cardService;
    }

    @Operation(summary = "List cards", description = "Returns a page of knowledge cards.")
    @GetMapping
    public CardPageResponse listCards(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        return cardService.listCards(page, size);
    }

    @Operation(summary = "Get a card by id")
    @GetMapping("/{id}")
    public CardResponse getCard(@PathVariable UUID id) {
        return cardService.getCard(id);
    }

    @Operation(summary = "Create a card")
    @PostMapping
    public ResponseEntity<CardResponse> createCard(@Valid @RequestBody CardRequest request) {
        CardResponse created = cardService.createCard(request);
        return ResponseEntity.created(URI.create("/api/v1/cards/" + created.id())).body(created);
    }

    @Operation(summary = "Update a card")
    @PutMapping("/{id}")
    public CardResponse updateCard(@PathVariable UUID id, @Valid @RequestBody CardRequest request) {
        return cardService.updateCard(id, request);
    }

    @Operation(summary = "Delete a card")
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteCard(@PathVariable UUID id) {
        cardService.deleteCard(id);
        return ResponseEntity.noContent().build();
    }
}
