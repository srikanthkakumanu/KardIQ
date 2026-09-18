package com.example.cards.application;

import com.example.cards.api.dto.CardPageResponse;
import com.example.cards.api.dto.CardRequest;
import com.example.cards.api.dto.CardResponse;
import com.example.cards.domain.Card;
import com.example.cards.infrastructure.CardMapper;
import com.example.cards.infrastructure.CardRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;

import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class CardServiceImplTest {

    @Mock
    private CardRepository cardRepository;

    @Mock
    private CardMapper cardMapper;

    private CardServiceImpl cardService;

    @org.junit.jupiter.api.BeforeEach
    void setUp() {
        cardService = new CardServiceImpl(cardRepository, cardMapper);
    }

    @Test
    void createCardNormalizesTrimsAndDedupesTags() {
        var request = new CardRequest("Title", "Body", List.of(" Tag ", "tag", "Other"));
        when(cardRepository.save(any(Card.class))).thenAnswer(inv -> inv.getArgument(0));
        when(cardMapper.toResponse(any(Card.class))).thenAnswer(inv -> {
            Card c = inv.getArgument(0);
            return new CardResponse(c.getId(), c.getTitle(), c.getBody(), c.getTags(), Instant.now(), Instant.now());
        });

        CardResponse response = cardService.createCard(request);

        assertThat(response.tags()).containsExactly("tag", "other");
    }

    @Test
    void getCardThrowsCardNotFoundWhenMissing() {
        UUID id = UUID.randomUUID();
        when(cardRepository.findById(id)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> cardService.getCard(id))
                .isInstanceOf(CardNotFoundException.class);
    }

    @Test
    void deleteCardThrowsCardNotFoundWhenMissing() {
        UUID id = UUID.randomUUID();
        when(cardRepository.existsById(id)).thenReturn(false);

        assertThatThrownBy(() -> cardService.deleteCard(id))
                .isInstanceOf(CardNotFoundException.class);
    }

    @Test
    void listCardsMapsPageToCardPageResponse() {
        Card card = new Card(UUID.randomUUID(), "T", "B", List.of());
        when(cardRepository.findAll(PageRequest.of(0, 20)))
                .thenReturn(new PageImpl<>(List.of(card)));
        when(cardMapper.toResponse(card))
                .thenReturn(new CardResponse(card.getId(), "T", "B", List.of(), Instant.now(), Instant.now()));

        CardPageResponse page = cardService.listCards(0, 20);

        assertThat(page.items()).hasSize(1);
        assertThat(page.totalElements()).isEqualTo(1);
        assertThat(page.page()).isZero();
        assertThat(page.size()).isEqualTo(20);
    }
}
