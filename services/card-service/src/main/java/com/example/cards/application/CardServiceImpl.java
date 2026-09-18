package com.example.cards.application;

import com.example.cards.api.dto.CardPageResponse;
import com.example.cards.api.dto.CardRequest;
import com.example.cards.api.dto.CardResponse;
import com.example.cards.domain.Card;
import com.example.cards.infrastructure.CardMapper;
import com.example.cards.infrastructure.CardRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
public class CardServiceImpl implements CardService {

    private static final int MAX_TAGS = 8;

    private final CardRepository cardRepository;
    private final CardMapper cardMapper;

    public CardServiceImpl(CardRepository cardRepository, CardMapper cardMapper) {
        this.cardRepository = cardRepository;
        this.cardMapper = cardMapper;
    }

    @Override
    @Transactional(readOnly = true)
    public CardPageResponse listCards(int page, int size) {
        Page<Card> result = cardRepository.findAll(PageRequest.of(page, size));
        List<CardResponse> items = result.getContent().stream()
                .map(cardMapper::toResponse)
                .collect(Collectors.toList());
        return new CardPageResponse(items, page, size, result.getTotalElements());
    }

    @Override
    @Transactional(readOnly = true)
    public CardResponse getCard(UUID id) {
        return cardMapper.toResponse(findOrThrow(id));
    }

    @Override
    @Transactional
    public CardResponse createCard(CardRequest request) {
        Card card = new Card(UUID.randomUUID(), request.title(), request.body(), normalizeTags(request.tags()));
        return cardMapper.toResponse(cardRepository.save(card));
    }

    @Override
    @Transactional
    public CardResponse updateCard(UUID id, CardRequest request) {
        Card card = findOrThrow(id);
        card.update(request.title(), request.body(), normalizeTags(request.tags()));
        return cardMapper.toResponse(card);
    }

    @Override
    @Transactional
    public void deleteCard(UUID id) {
        if (!cardRepository.existsById(id)) {
            throw new CardNotFoundException(id);
        }
        cardRepository.deleteById(id);
    }

    private Card findOrThrow(UUID id) {
        return cardRepository.findById(id).orElseThrow(() -> new CardNotFoundException(id));
    }

    private List<String> normalizeTags(List<String> tags) {
        if (tags == null) {
            return List.of();
        }
        return tags.stream()
                .filter(tag -> tag != null && !tag.isBlank())
                .map(tag -> tag.trim().toLowerCase())
                .distinct()
                .limit(MAX_TAGS)
                .collect(Collectors.toList());
    }
}
