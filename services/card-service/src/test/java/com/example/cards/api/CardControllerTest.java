package com.example.cards.api;

import com.example.cards.api.dto.CardPageResponse;
import com.example.cards.api.dto.CardRequest;
import com.example.cards.api.dto.CardResponse;
import com.example.cards.application.CardNotFoundException;
import com.example.cards.application.CardService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(CardController.class)
class CardControllerTest {

    @Autowired
    private MockMvc mockMvc;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @MockitoBean
    private CardService cardService;

    @Test
    void createCardReturns201WithLocationHeader() throws Exception {
        var request = new CardRequest("Title", "Body", List.of("tag"));
        var response = new CardResponse(UUID.randomUUID(), "Title", "Body", List.of("tag"), Instant.now(), Instant.now());
        when(cardService.createCard(any())).thenReturn(response);

        mockMvc.perform(post("/api/v1/cards")
                        .contentType("application/json")
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(header().string("Location", "/api/v1/cards/" + response.id()))
                .andExpect(jsonPath("$.title").value("Title"));
    }

    @Test
    void createCardReturns400OnBlankTitle() throws Exception {
        var request = new CardRequest("", "Body", List.of());

        mockMvc.perform(post("/api/v1/cards")
                        .contentType("application/json")
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value("VALIDATION_ERROR"));
    }

    @Test
    void getCardReturns404WhenMissing() throws Exception {
        UUID id = UUID.randomUUID();
        when(cardService.getCard(eq(id))).thenThrow(new CardNotFoundException(id));

        mockMvc.perform(get("/api/v1/cards/" + id))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.code").value("CARD_NOT_FOUND"));
    }

    @Test
    void listCardsReturnsPage() throws Exception {
        when(cardService.listCards(0, 20))
                .thenReturn(new CardPageResponse(List.of(), 0, 20, 0));

        mockMvc.perform(get("/api/v1/cards"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.page").value(0))
                .andExpect(jsonPath("$.size").value(20));
    }
}
