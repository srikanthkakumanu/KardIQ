package com.example.cards.infrastructure;

import com.example.cards.domain.Card;
import org.junit.jupiter.api.Test;
import org.mapstruct.factory.Mappers;

import java.util.List;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;

class CardMapperTest {

    private final CardMapper mapper = Mappers.getMapper(CardMapper.class);

    @Test
    void mapsAllFieldsFromEntityToResponse() {
        Card card = new Card(UUID.randomUUID(), "Title", "Body", List.of("a", "b"));

        var response = mapper.toResponse(card);

        assertThat(response.id()).isEqualTo(card.getId());
        assertThat(response.title()).isEqualTo("Title");
        assertThat(response.body()).isEqualTo("Body");
        assertThat(response.tags()).containsExactly("a", "b");
    }
}
