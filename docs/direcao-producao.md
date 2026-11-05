# Direção de produção — Filme iSCOUT 30 s

> Status: **animatic v1 (pré-produção)**. Nenhum crédito consumido. Textos são propostas de campanha.

## 1. Decisões de direção

| Tema | Decisão | Por quê |
|---|---|---|
| Linguagem | **"A linha que revela"**: um único traço lima nasce do pé do atleta, vira trajetória, vira linha do tempo, organiza o perfil e assina a marca. | Um único elemento gráfico com função narrativa no lugar de um dashboard decorativo. Cria uma identidade própria. |
| Luz | Estádio noturno: azul profundo, refletores frios, gramado saturado. | Coerente com `v2-panorama` e `mock-coach-tablet`, que são os melhores clipes existentes. Reduz a quantidade de geração necessária. |
| Paleta (provisória, amostrada) | Navy `#0B113D`, azul `#0B2D58`, ciano `#44C4C8`, lima `#CDD55C` (logo), verde ícone `#68B12D`, branco. | Tirada dos assets oficiais. Será substituída pelos códigos do guia de marca quando ele existir. |
| Tipografia | Sora 700 nos títulos e Sora 400 no apoio. Títulos com no mínimo 6% da altura (16:9) ou 3,4% (9:16). | Leitura em celular sem som. |
| Ritmo | Impacto (S1) → fluidez (S2–S3) → pausa (comparação S4) → respiro humano (S5) → silêncio de marca (S6). | Alternância pedida no briefing. |
| Ilustrativo | "Imagens e interfaces ilustrativas" no canto inferior, de S3 a S5 (8,0–25,0 s). | Identificação discreta, mas legível. |
| Stack | **Python/PIL + ffmpeg** no animatic. **Remotion (React)** no final, renderizado em CPU com o Chromium local. Sem Blender. | Não há GPU. Remotion garante 900 frames exatos, duas composições (16:9 e 9:16) com o mesmo código e tipografia/UI vetorial nítida. O 3D não traz ganho real aqui: a "profundidade" vem dos planos filmados e do parallax 2.5D. |
| Geração | **Magnific** (Higgsfield está com 0 créditos). | Ver seção 5. |

## 2. Storyboard

| # | Tempo / frames | Ação | Câmera | Texto (entrada → saída) | Transição de saída | Áudio |
|---|---|---|---|---|---|---|
| 1 · A jogada | 0–4 s / 0–119 | Atleta domina a bola de costas, gira e muda de direção. Grama levanta no contato. | Rente ao gramado (~20 cm), lente 35 mm, push-in lento; foco na chuteira e depois no rosto. | "O talento acontece em campo." (f18 → f116) | **Bola**: o chute da saída leva a um whip-zoom (f108–119). | Toque seco de bola, chuteira na grama; a trilha entra num beat único. |
| 2 · O olhar | 4–8 s / 120–239 | Revela-se o campo e o deslocamento do atleta. O traço lima desenha o percurso real e um anel marca a posição. | Pull-out de 1.6× para 1.0× (aéreo baixo, 3/4). | "Cada movimento conta." (f132 → f238), no topo | **Linha do campo**: o traço achata e vira a linha do tempo. | Whoosh na abertura, pulso de trilha. |
| 3 · O registro | 8–13 s / 240–389 | O plano encolhe e vira um card de vídeo. Outros registros (Jogo/Treino) se alinham na linha do tempo, que desliza. | Câmera gráfica 2D, truck lateral. | "Jogos e treinos. Uma história organizada." (f278 → f389) | **Registro**: os cards se reorganizam em comparação. | Clique suave por registro. |
| 4 · A evolução | 13–19 s / 390–569 | Mesmo lance em dois momentos (A·Treino, B·Jogo). As trajetórias se comparam (A hesitante, B direta). Depois tudo colapsa num **perfil** com registros organizados, sem números. | 2D, split 50/50 (no 9:16, empilhado). | "Mais contexto para entender." (f400 → f482) → "Mais clareza para desenvolver." (f494 → f569) | Card de perfil vira a tela do tablet (match-cut). | Pausa de ~0,5 s na comparação; sweep no perfil. |
| 5 · A decisão humana | 19–25 s / 570–749 | Treinador consulta o tablet à beira do campo, levanta o olhar e apita; o treino recomeça. | Over-the-shoulder, depois rack focus para o campo, depois plano aberto. | "Inteligência para desenvolver." (f580 → f664) → "Visibilidade para descobrir." (f671 → f749) | **Linha de campo**: wipe branco até o fundo navy (f735–749). | Ambiente de treino, apito na retomada. |
| 6 · Marca | 25–30 s / 750–899 | Ícone, depois logo, depois as duas linhas, CTA e URL. **Tudo assentado até f810 (27 s)**. Depois, só leitura. | Estático, com drift de 3%. | "O talento acontece em campo." / "A iSCOUT ajuda a enxergá-lo." / [Conheça a iSCOUT] / iscout.tech | Fim. | Hit de marca em 25,5 s e cauda até 30 s. |

**Vertical 9:16:** composição própria.
- S1: título no terço superior, bola no inferior.
- S2: trajetória diagonal remapeada.
- S3: registros empilhados.
- S4: comparação de cima para baixo.
- S6: ícone sobre o logo.
- Viável sem perda de leitura. Os planos IA precisam de versão nativa 9:16 em S1 e S5 (recorte de 16:9 perde o pé e a bola).

## 3. Cenas × assets existentes

| Cena | Asset atual no animatic | Uso final | Observação |
|---|---|---|---|
| S1 | `soccer-training-hero.jpg` (placeholder) | ❌ substituir | Uniformes estilo seleção brasileira com escudo: **risco de marca de terceiros**. Luz diurna, fora do conceito noturno. |
| S2 | `v2-panorama-sm` | ⚠️ provisório | 1280×542, curto na vertical. O atleta não é o mesmo do S1. Ideal: plano gerado com o mesmo atleta. Alternativa: upscale do original de 1920 px, que está pendente. |
| S3 | posters + `youth-soccer-academy`, `tablet-field` | ⚠️ como cards pequenos | Aceitável em miniatura. Melhor usar frames dos planos novos (mesmo atleta). |
| S4 | `soccer-training-hero` / `youth-soccer-academy` | ❌ substituir | A comparação exige **o mesmo atleta** em dois momentos. |
| S5a | `mock-coach-tablet` | ⚠️ com ajuste | A tela do tablet mostra **números genéricos inventados**. É preciso desfocar/cobrir e compor a UI por código, ou gerar um plano novo. |
| S5b | `v2-panorama-sm` | ❌ placeholder | Precisa de um plano de "retomada do treino" com o treinador. |
| S6 | `icone.png`, `iscout-logo-branca.png`, `fundo.jpg` | ✅ | O logo bitmap tem 854 px de largura e no 16:9 é exibido com ~650 px, então funciona. Um vetor oficial continua recomendado. |
| — | `scouting-pose-analysis.webp`, `mockup-*`, `app-screens.png` | 🚫 não usados | Contêm métricas, nomes e percentuais não confirmados. |

## 4. O que precisa ser criado

**Por IA (planos, sem texto/logo/UI):**
1. Atleta-personagem de referência (sheet frontal/perfil/costas), uniforme liso navy sem número nem escudo.
2. S1: domínio + giro, 16:9 e 9:16, 5 s cada. **É o plano crítico.**
3. S2: plano aberto revelando o deslocamento do mesmo atleta, 5 s, 16:9 (o 9:16 sai por recorte).
4. S4: dois momentos do mesmo atleta (treino ao entardecer × jogo noturno), 4 s cada.
5. S5: treinador com tablet (tela de costas ou em chroma liso para comp), 16:9 e 9:16, 5 s.
6. S5b: retomada do treino (apito, atletas arrancam), 4 s.

**Por código (Remotion):**
- Trajetória e marcadores, com tracking manual por keyframes sobre os planos finais.
- Linha do tempo, cards de registro, comparação e perfil (componentes UI conceituais, sem números).
- Tela do tablet.
- Todos os textos, CTA, assinatura e disclaimer.
- Montagem e duas composições.

**Áudio:**
- Trilha com licença comercial: biblioteca licenciada ou `audio_music_generate` do Magnific, conforme a licença do plano.
- SFX: toque de bola, chuteira, whoosh, cliques, apito, ambiente de treino.

**Magnific refino:** `video_upscale` só nos planos aprovados e, se necessário, `images_to_svg` do logo (apenas com aprovação do cliente).

## 5. Lote de teste inicial — proposta (NÃO executado)

Higgsfield: plano starter, **0 créditos**, portanto indisponível para gerar. O lote usa **Magnific** (Premium+, 41.655 créditos). Custos obtidos via `simulate_cost`, que é só leitura.

**Objetivo:** validar primeiro a ação mais difícil (domínio + mudança de direção com contato pé-bola crível) comparando dois motores antes de gerar o resto.

| ID | Objetivo | Ferramenta / modelo | Referências | Qtd | Duração / resolução | Custo est. |
|---|---|---|---|---|---|---|
| T0a | Sheet do atleta (consistência para todas as cenas) | Magnific `images_generate` · Nano Banana 2.1 | Paleta + estilo de luz de `v2-panorama-poster.webp` (style ref) | 2 | 2k 16:9 | ~130 (variável) |
| T0b | Keyframes S1: início (recepção de costas) e fim (após o giro) | Nano Banana 2.1 | T0a (character) + `v2-panorama-poster` (style) | 2 pares (4 imgs) | 2k 16:9 | ~260 (variável) |
| T1 | **Ação S1** com início e fim travados | `video_generate` · **Kling 2.5** (start+end frame) | T0b | 2 | 5 s · 1080p · 16:9 · sem áudio | 650 (2×325) |
| T2 | **Ação S1** livre, com referência de personagem (físico/câmera) | `video_generate` · **Seedance 2.5** | T0a (character) + `v2-panorama-poster` (style) | 2 | 5 s · 480p · 16:9 | 2.000 (2×1.000) |
| | | | | | **Total** | **≈ 3.040 créditos (~7% do saldo)** |

**Prompt-base T1/T2 (EN, sem texto):**
> Low ground-level tracking shot, 35mm, night stadium floodlights, deep blue atmosphere. A 15-year-old footballer in a plain navy kit (no numbers, no logos, no crests, no text) receives a pass with the inside of his right foot, cushions the ball, turns sharply to his left and accelerates away. Realistic foot-ball contact, ball stays close, grass flecks lift. Shallow depth of field, controlled contrast. No graphics, no text, no watermark.

Negative (Kling): `text, letters, numbers, logo, crest, watermark, extra limbs, ball morphing, ball sticking to foot`.

**Critérios de aprovação do teste:**
1. Contato pé-bola sem atravessar ou grudar.
2. Bola com massa e trajetória coerente.
3. Anatomia estável no giro.
4. Ausência de texto ou escudos.
5. Personagem consistente com T0a.

Se passar, o vencedor define o motor do resto do lote. Estimativa do lote completo: 6–8 planos em 1080p, entre ~3k e ~25k créditos conforme o motor escolhido (Kling ~325 por 5 s; Seedance 2.5 1080p ~3.950 por 5 s). Será orçado de novo antes da execução.

Em seguida, 9:16 nativo do plano aprovado (mesmo custo unitário).

## 6. Arquivos do animatic

- `animatic/render.py`: gerador (Python/PIL + ffmpeg). Variáveis `SRC` (frames de footage) e `FONTDIR` (Sora em TTF estático).
- `animatic/out/animatic_16x9.mp4` (960×540) e `animatic_9x16.mp4` (540×960): 30 fps, 900 frames, sem áudio, com HUD de revisão (cena, timecode, cue de áudio, origem do asset).
- `animatic/out/styleframes/`: `sf1_abertura`, `sf2_evolucao`, `sf3_assinatura` em `_h` (1920×1080) e `_v` (1080×1920).

## 7. Telas novas do app (redesign) — encaixe proposto

Fonte: `assets/interfaces/redesign/` (também em `iscout-telas-novas/`; a pasta da raiz tem 12 arquivos a mais em 05 e 06). Telas de **produto real em redesign**, com **dados de demonstração** (nomes, km/h, notas). Confirmam visualmente: galeria de vídeos com etiquetas Jogo/Treino, perfil do atleta, evolução, agenda, player com lances marcados e comentários do treinador, área do clube.

| Cena | Tela | Uso |
|---|---|---|
| S3 · O registro | `4.2.2-galeria-videos` | Os cards da linha do tempo "pousam" na galeria real (Jogo/Treino). |
| S4 · A evolução | `4.2.9-player-video` (marcadores de lance) → `4.2.0-perfil-atleta` | Comparação sai do player; perfil organizado fecha a cena. |
| S5 · A decisão humana | `C3.0-perfil-atleta-clube` ou comentários do treinador em `4.2.9` | Tela consultada pelo treinador (substitui a UI genérica do `mock-coach-tablet`). |

Regras: exibir em moldura de celular, recortes ampliados (≥ 60% da altura em 9:16), sem ler números como promessa; números de demonstração **desfocados ou neutralizados** até aprovação; manter o disclaimer "interfaces ilustrativas". Não usar telas de pagamento, termos, PIN ou marketplace (ruído e dado sensível).

## 8. Resultado do lote de teste (05/11/2026)

Executado no Magnific. **Custo real: 3.040 créditos** (saldo 41.655 → 38.615), igual ao estimado. Arquivos locais em `animatic/out/gen/` (fora do git); originais na conta Magnific, projeto Personal.

| ID | Resultado | Avaliação |
|---|---|---|
| T0a (2 imgs) | Folha frente/perfil/costas, uniforme navy liso com friso lima | ✅ Sem texto/escudo. Variação 2 escolhida como referência (luz neutra). |
| T0b início (2) | Atleta recebendo a bola, câmera rente, estádio noturno | ✅ Variação 2 escolhida (câmera mais baixa). |
| T0b fim (2) | Mesmo atleta após o giro, mesmo estádio | ✅ Consistentes com o início. |
| T1 Kling 2.5 (2 × 5 s, 1928×1072) | Condução lenta e giro suave, enquadramento aberto | ⚠️ Identidade e cenário estáveis, mas o lance é tímido: a bola fica quase parada e o giro não lê como "mudança de direção". |
| T2 Seedance 2.5 A (5 s, 480p) | Recepção, giro marcado e arrancada de costas para o fundo | ✅ Melhor leitura da ação e energia. ⚠️ Bola parada demais antes do toque (contato pouco crível). |
| T2 Seedance 2.5 B (5 s, 480p) | Close nas chuteiras, toque, tilt até o rosto | ✅ Contato pé-bola próximo e legível; ótimo para abrir o filme. |

Critérios: texto/escudos ✅ todos; anatomia ✅ sem membros extras; consistência de personagem ✅; **contato pé-bola: parcial** em todos.

**Decisão recomendada:** Seedance 2.5 como motor. Montar S1 em **dois planos com corte na ação** (B: toque em close → A: giro e arrancada), o que esconde a fragilidade do contato. Próxima rodada (~2.000 cr): Seedance 2.5 com **quadro inicial travado** e bola entrando em movimento ("ball rolls in from the right"), depois finalizar o escolhido em 1080p (~3.950 cr por 5 s).

## 9. Rodada 2 + trilha (05/11/2026)

Custo real: **2.160 créditos** (saldo 38.615 → 36.455).

| Item | Configuração | Resultado |
|---|---|---|
| R2-A Seedance 2.5 | 480p, 5 s, quadro inicial travado (T0b início) | ✅ **Aprovado para S1.** A bola acompanha o atleta durante o domínio e o giro; mudança de direção clara; identidade e uniforme estáveis; sem texto. A bola não "entra rolando" (começa no pé). |
| R2-B Seedance 2.5 | 480p, 5 s, início + fim travados | ⚠️ Condução de frente para a câmera; giro pouco decisivo. Reserva. |
| Trilha A (Lyria 3) | 30 s, instrumental | Pausa em 16–18 s, mas segue cheia até o fim — sem hit de marca. |
| Trilha B (Lyria 3) | 30 s, instrumental | ✅ **Escolhida.** Pulso desde o início, respiro em 18,5 s, **retorno com impacto em 25 s** (entrada da marca) e cauda até 30 s. O vazio 19–24 s vira espaço para ambiente de treino + apito (S5). |

Logo: **lockup oficial "iSCOUT by FYRECOM™" mantido como está** (decisão do cliente).

**Próximo passo:** upscale do R2-A para 1080p via Magnific Precision (**≈2.297 cr**, estimado) ou nova geração em 1080p (≈3.950 cr, take diferente — Seedance 2.5 não tem seed). Recomendado: upscale, preserva o take aprovado.

### Upscale do S1 (R2-A)

- Preview (12 frames) para validar fidelidade antes do completo: 497 cr.
- Completo: Magnific **Precision**, força 35 (baixa, para não reinventar detalhe), sharpen 10, grain 5, sem interpolação de frames: 2.297 cr.
- Saída 1932×1078, 121 frames (idêntico ao original). Proporção preservada (1,791 → 1,792); sem deformação de corpo, bola ou rosto na comparação quadro a quadro.
- Master `S1_dominio_1080p.mp4`: escala proporcional para 1936 px + recorte central de 8 px por lado → **1920×1080, SAR 1:1**, sem áudio, 24 fps (conversão para 30 fps só na montagem).

## 10. S1 no animatic + orçamento dos planos restantes

**S1 inserido** (`render.py` lê `$SRC/s1/`, extraído de `S1_dominio_1080p.mp4` a partir de 0,25 s, 30 fps). Título subiu para o topo (a bola ocupa o terço inferior). No 9:16 o recorte acompanha o atleta (fx 0,50 → 0,30); a bola sai do quadro no último segundo — aceitável, mas justifica um 9:16 nativo se o vertical for prioridade.

**Orçamento** (Magnific `simulate_cost`; geração Seedance 2.5 480p → upscale Precision 1080p; 2 takes por plano; keyframe Nano Banana 2.1 ≈65 cr/img):

| Plano | Uso no filme | Geração | Upscale | Keyframes | Total |
|---|---|---|---|---|---|
| S2 · plano aberto, mesmo atleta | 4 s tela cheia | 2 × 5 s = 2.000 | 2.297 | 130 | **4.427** |
| S4-A · momento treino (entardecer) | painel ~43% da largura | 2 × 4 s = 1.600 | — (480p basta no painel) | 130 | **1.730** |
| S4-B · momento jogo (noite) | painel ~43% | 2 × 4 s = 1.600 | — | 130 | **1.730** |
| S5a · treinador com tablet (tela de costas) | 1,2 s nítido + fundo desfocado | 2 × 4 s = 1.600 | 1.897 | 130 + 130 (folha do treinador) | **3.757** |
| S5b · retomada do treino (apito) | 3 s tela cheia | 2 × 4 s = 1.600 | 1.897 | 130 | **3.627** |
| **Subtotal recomendado** | | | | | **≈15.271** |
| Opcional · S1 nativo 9:16 | vertical | 2 × 5 s = 2.000 | 2.297 | 130 | 4.427 |

Saldo atual 33.661 → ~18.390 após o recomendado (~13.960 com o 9:16). Upscales são estimados (24 fps); geração é valor exato. Economia possível: 1 take por plano (−4.200), com risco de refazer.

## 11. Decisão: proposta enxuta + teto de créditos

**Teto aprovado: 3.000 créditos para o restante do projeto.** Acima disso, só com aprovação explícita. Sem previews pagos. Gasto acumulado até aqui: 7.994 cr (saldo 33.661).

O orçamento da §10 (≈15.271 cr) foi **descartado**. Plano enxuto, custo zero:

| Cena | Fonte |
|---|---|
| S1 | Plano aprovado (R2-A, 1080p) |
| S2 | `v2-panorama-sm` com upscale local na montagem |
| S3 | Cards com quadros dos takes do próprio atleta (T2-A, Kling A, R2-B, T2-B) — **remove a referência com uniforme de terceiros** |
| S4 | Momento A = T2-B (close), Momento B = R2-B (aberto): mesmo atleta, takes já pagos |
| S5a / S5b | `mock-coach-tablet` (tela coberta pelo insert do app) / trecho final do `v2-panorama-sm` |

Opcional dentro do teto: 1 plano novo do treinador sem upscale (~800–1.000 cr), só se o existente não convencer.

## 12. Uniforme real do clube (versão limpa)

Decisão do cliente: usar o uniforme real do clube **sem marcas** (sem patrocinador, fornecedor, números ou escudo). Referência limpa gerada a partir da foto do uniforme (Nano Banana 2.1, 65 cr) e aplicada nos planos já aprovados, mantendo o movimento:

| Plano | Ferramenta | Saída | Custo |
|---|---|---|---|
| S1 (R2-A 1080p) | Magnific video_modify · Kling 4.0 1080p | 1928×1076, 121 frames → master `S1_dominio_1080p_uniforme.mp4` 1920×1080 | 1.650 |
| S4-B (R2-B 480p) | video_modify · Gemini Omni 1.2 Flash 720p (Kling exige ≥700 px) | 1280×720, 120 frames | 700 |

Verificação: listras navy/vermelho, gola e barra vermelhas conferem; **nenhum texto, número ou logo surgiu**; rosto, corpo, bola e câmera preservados. S4-A (close nas chuteiras) não mostra a camisa — sem custo.

**Créditos:** 2.415 do teto de 3.000 (restam **585**). Saldo Magnific 31.246.

Pendência visual: os cards pequenos do S3 (takes T2-A e Kling A) ainda mostram o uniforme navy antigo.
