package com.example.cards.infrastructure;

import com.example.cards.api.dto.CardResponse;
import com.example.cards.domain.Card;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface CardMapper {

    CardResponse toResponse(Card card);
}
