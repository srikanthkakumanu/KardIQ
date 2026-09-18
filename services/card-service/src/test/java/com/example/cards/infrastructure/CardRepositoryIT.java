package com.example.cards.infrastructure;

import com.example.cards.AbstractIntegrationTest;
import com.example.cards.domain.Card;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;
import org.springframework.boot.jdbc.test.autoconfigure.AutoConfigureTestDatabase;
import org.springframework.data.domain.PageRequest;

import java.util.List;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
class CardRepositoryIT extends AbstractIntegrationTest {

    @Autowired
    private CardRepository cardRepository;

    @Test
    void savesAndFindsACardById() {
        Card saved = cardRepository.save(new Card(UUID.randomUUID(), "Neo4j", "Graph database", List.of("db", "graph")));

        var found = cardRepository.findById(saved.getId());

        assertThat(found).isPresent();
        assertThat(found.get().getTitle()).isEqualTo("Neo4j");
        assertThat(found.get().getTags()).containsExactly("db", "graph");
    }

    @Test
    void listsCardsWithPagination() {
        cardRepository.save(new Card(UUID.randomUUID(), "A", "body", List.of()));
        cardRepository.save(new Card(UUID.randomUUID(), "B", "body", List.of()));

        var page = cardRepository.findAll(PageRequest.of(0, 1));

        assertThat(page.getContent()).hasSize(1);
        assertThat(page.getTotalElements()).isGreaterThanOrEqualTo(2);
    }
}
