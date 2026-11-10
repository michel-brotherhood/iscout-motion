# Revisão V3 — iSCOUT 2:07 (feedback Bernardo Canto, 08/11/2026)

Fonte: `animatic/hype/filme_v3.py` (reutiliza `filme_v2.py`: mesma timeline, locução e legendas sincronizadas).
Saídas (fora do git): `animatic/out/v3/entregas/iSCOUT_V3_2min_{239,16x9}[_whatsapp].mp4`.
A V2 continua intacta em `animatic/out/v2/entregas/`.

## 1. O que os áudios confirmam

| Tema | Evidência | Conclusão |
|---|---|---|
| Roteiro / locução | WA0008 274 s ("o conteúdo, o roteiro tá muito bom"), WA0016 5 s ("a roteirização tá boa"), WA0017 84–102 s ("o script em si, para mim, está ótimo") | **Manter roteiro e voz.** O pitch é referência visual, não substitui a copy. |
| Overlay verde / P&B | Texto 17:47; WA0008 121–160 s; WA0017 36–51 s | Verde só em lettering, telas do app e motion. Cenas em cor natural, vibrantes. |
| Música | WA0008 154–170 s e 250 s ("mais upbeat, mais BPM, pulsante"); WA0017 51–67 s ("mais energizante… juventude, vitalidade") | **Trocar a trilha** (pedido só em áudio). |
| Ambientes | Texto 17:49 + WA0013/WA0014; WA0008 174–228 s (parede desmantelada, lixo, favela como tônica) | Ambientes premium/high-end; várzea pode aparecer pontualmente, não como tônica. |
| 5 dimensões | Texto 17:51 + WA0015 | Radar animado. |
| Pitch / PDF | WA0016 30–63 s | Referência de cenas em cor natural com verde dosado e logo dosada. |
| Telas do app | WA0017 1–36 s; Michel 17:58 | Refletir o app atual "ao máximo possível". Bernardo não validou as telas novas. |
| WA0022 | 25–56 s | Alinhamento ("na mesma página"). Ele cita os vídeos do site como referência. |

## 2. Matriz de alterações

| # | Evidência | Ação na V3 | Cena (tempo do filme) | Status |
|---|---|---|---|---|
| 1 | Texto + áudio (cor) | Gradação natural em todas as cenas. Saíram `duo`, P&B, `scan` verde e o filtro "X-Files". Saturação +12 % e contraste suave. Vinheta mais leve e grão menor. | Todas | Feito |
| 2 | Áudio (proposta de direção) | Removidos fumaça, halo (`edges`), linhas em V sobre o atleta, glitches e flash verde. O verde ficou em legendas, cartões, radar, telas e nas linhas de marca do fechamento. | Todas | Feito |
| 3 | Texto + WA0013/0014 + áudio | Treino na favela (coach1/2) trocado por `kids.png` (CT moderno) e `soccer-training-hero.jpg`. Escritório velho (club1/2) trocado por `club.png` (escritório moderno com vista do campo) e `youth-soccer-academy.jpg`. Câmeras na favela (c1/c2/c3) trocadas por `wa2` (atleta com celular) e `v2-panorama` (estádio, câmera no tripé, vídeo do site). | 15–23 s, 66–71 s, 94–102 s | Feito |
| 4 | WA0009 (gráficos sobre o atleta) | O plano do wa6 com "Performance Profile" sobreposto foi substituído pelo #8 em ação (`p_b2.png`). | 10,8–13,2 s | Feito |
| 5 | WA0011 / WA0012 (fumaça, "X-Files") | Retratos p1–p4 com fumaça verde trocados por 4 retratos novos do #8 em cor natural (estádio moderno, luz de fim de tarde e dia). | 13–15 s, 59–62 s, 105 s, 112–119 s | Feito |
| 6 | Texto 17:51 + WA0015 | Radar animado. Os eixos surgem em "cinco dimensões" e cada rótulo e valor entra quando a dimensão é falada. Cada cartão ganha um mini-radar com a dimensão em foco. Em "potencial", o polígono atual se abre para o contorno tracejado do potencial. Valores marcados como **ilustrativos**. | 40,9–46,7 s; 46,7–62,6 s; 62,6–66,5 s | Feito |
| 7 | Metodologia | WA0015 (app) tem 6 eixos (Velocidade, Força, Precisão, Resistência, Técnica, Visão). O radar segue o **painel de análise** enviado por Michel: Técnica, Tática, Físico, Resiliência, Potencial, que bate com "cinco dimensões" da locução. Por isso o cartão "FÍSICA" virou **FÍSICO**. | Bloco das dimensões | Feito (decisão de Michel) |
| 8 | Áudio (música) | Trilha nova (Lyria 3 Pro, pedida a 126 BPM, upbeat, pop-eletrônica com percussão brasileira). Mixada sob a voz com duck. -14,2 LUFS, pico -1,7 dBFS. | Todo o filme | Feito, falta ouvir |
| 9 | WA0016 (logo dosada) | Mantidos o ícone fixo no canto e a assinatura final. A logo não foi repetida em outras cenas. | — | Mantido |
| 10 | WA0017 (telas atuais) | Usadas as telas de `assets/interfaces/redesign` (as mais recentes do repositório), com nomes de exemplo trocados por "Atleta #8". | App | Feito; Bernardo ainda não validou |
| 11 | Pitch (copy comercial) | Não usada. Roteiro institucional mantido (confirmado nos áudios). | — | Mantido |
| 12 | Abertura (campo com IA) | Mantida: foi pedida por Michel na V2 e o verde ali é motion de marca. **Ponto de atenção:** são cerca de 6 s de grade verde. Se o Bernardo achar dominante, dá para encurtar ou trocar. | 0–10,8 s | A validar |

## 3. Mapa de cenas (V2 → V3)

| Tempo | V2 | V3 |
|---|---|---|
| 0–10,8 | Campo IA (Kling) | Igual |
| 10,8–13,2 | wa6 com gráficos sobrepostos, P&B | #8 em ação, estádio moderno |
| 13,2–15,7 | p4 com fumaça e halo | #8 retrato com bola, fim de tarde |
| 15,7–19,4 | Treino na favela (coach2) | Crianças e treinador em CT moderno |
| 19,4–20,9 | Treino na favela (coach1) | Treino em estádio (soccer-training-hero) |
| 20,9–41 | Telas do app sobre fundo verde | Mesmas telas sobre a família em cor natural |
| 40,9–46,7 | Palavras em fundo preto | **Radar animado** |
| 46,7–62,6 | Cartões sobre lances verdes | Cartões + mini-radar sobre lances em cor natural; potencial com retrato natural |
| 62,6–66,5 | p1 com fumaça | **Radar de evolução (atual → potencial)** |
| 66,5–71 | Câmeras na favela | Atleta com celular + estádio com câmera no tripé |
| 71–80,6 | Demo de análise + player | Igual |
| 80,4–90,5 | Monitor e tablet em verde | Os mesmos planos em cor natural |
| 94–101,8 | Escritório velho / favela | Escritório moderno + treinador com tablet |
| 105–119 | Retratos com fumaça e montagem com glitch | Retratos naturais e montagem limpa |
| 119–127,5 | Assinatura | Igual |

## 4. Verificações

- Feito: transcrição dos 4 áudios do Bernardo e da locução, por palavra, para sincronizar as legendas.
- Feito: quadros de teste do radar, dos cartões, dos planos de celular e das cenas novas, conferidos visualmente.
- Feito: loudness do mix medido (-14,2 LUFS, pico -1,7 dBFS) e duração conferida (127,48 s).
- Não feito: escuta humana da trilha nova. Não tenho como ouvir; o BPM não foi medido, só pedido no prompt.

## 5. Pendências

- O PDF `iSCOUT_ESCOLAS_v2.pdf` e o vídeo `VID-20261108-WA0018` não vieram nos pacotes. A referência visual foi aplicada a partir da descrição e do áudio WA0016.
- Bernardo precisa validar as telas do app (ele mesmo disse que não viu as versões novas).
- Clipes do #8 (wa1–wa5) continuam em campos de bairro bem cuidados, sem lixo nem paredes quebradas, que cabem como cena pontual. Se quiserem tudo premium, eles precisam ser trocados.
- Créditos Magnific: 610 usados (6 imagens a 75 + trilha a 160). Ficaram 50 acima dos 560 aprovados porque o custo por imagem foi 75, e não os 65 estimados.

## Render

```bash
S=<scratchpad>; cd animatic/hype
export SRCWA=$S/wa PORT=$PWD/../out/hype V2=$PWD/../out/v2 V3=$PWD/../out/v3 FONTDIR=$S SCREENS=$S/src/screens DEMO=$PWD/../out/v2/demo.mp4
FMT=239 python3 filme_v3.py ../out/v3/v3_239_video.mp4   # depois FMT=169; um por vez (memória)
# mux com out/v3/mix3.wav (trilha nova + locução); versão WhatsApp em 1280 px, crf 26
```
