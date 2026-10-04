package com.example.cards.infrastructure;

import com.example.cards.api.dto.CardResponse;
import com.example.cards.domain.Card;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import javax.annotation.processing.Generated;
import org.springframework.stereotype.Component;

@Generated(
    value = "org.mapstruct.ap.MappingProcessor",
    date = "2026-10-04T22:25:05+0530",
    comments = "version: 1.6.3, compiler: Eclipse JDT (IDE) 3.46.100.v20260826-1225, environment: Java 21.0.12.1 (Eclipse Adoptium)"
)
@Component
public class CardMapperImpl implements CardMapper {

    @Override
    public CardResponse toResponse(Card card) {
        if ( card == null ) {
            return null;
        }

        UUID id = null;
        String title = null;
        String body = null;
        List<String> tags = null;
        Instant createdAt = null;
        Instant updatedAt = null;

        id = card.getId();
        title = card.getTitle();
        body = card.getBody();
        List<String> list = card.getTags();
        if ( list != null ) {
            tags = new ArrayList<String>( list );
        }
        createdAt = card.getCreatedAt();
        updatedAt = card.getUpdatedAt();

        CardResponse cardResponse = new CardResponse( id, title, body, tags, createdAt, updatedAt );

        return cardResponse;
    }
}
