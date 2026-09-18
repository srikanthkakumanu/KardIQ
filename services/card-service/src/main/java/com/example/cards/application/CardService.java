package com.example.cards.application;

import com.example.cards.api.dto.CardPageResponse;
import com.example.cards.api.dto.CardRequest;
import com.example.cards.api.dto.CardResponse;

import java.util.UUID;

public interface CardService {

    CardPageResponse listCards(int page, int size);

    CardResponse getCard(UUID id);

    CardResponse createCard(CardRequest request);

    CardResponse updateCard(UUID id, CardRequest request);

    void deleteCard(UUID id);
}
