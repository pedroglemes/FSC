import streamlit as st
from openai import OpenAI
from personagens import *

# ==========================================
# 🔑 API KEY (secure via Streamlit Secrets)
# ==========================================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Elaboração de ESRA - FSC", layout="wide")

# ==========================================
# SESSION STATE
# ==========================================

if "etapa" not in st.session_state:
    st.session_state.etapa = "apresentacao"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "personagem_atual" not in st.session_state:
    st.session_state.personagem_atual = None

# ==========================================
# ETAPA 1 — APRESENTAÇÃO DA ATIVIDADE
# ==========================================

if st.session_state.etapa == "apresentacao":

    col1, col2, col3 = st.columns([1, 5, 1])

    with col2:
        st.title("🌳🐛 PBL – Elaboração de ESRA (FSC)")

    col1, col2, col3 = st.columns([1, 5, 1])

    with col2:

        st.markdown("""
## 📚 Atividade

Vocês foram contratados pela empresa florestal **SilvaFlora Reflorestamentos S.A.** localizada em **Bocaiúva, Minas Gerais – Brasil**.

A empresa possui certificação FSC e está enfrentando problemas com o **psilídeo-de-concha** em seus plantios de eucalipto.

O produto utilizado para o controle da praga será um pesticida classificado como **altamente perigoso segundo o FSC**, e portanto exige a elaboração de um **ESRA – Environmental & Social Risk Assessment (Avaliação de Riscos Ambientais e Sociais)**.

---

## 🎯 Missão dos Grupos

Em grupos, vocês deverão:

- Fazer perguntas aos funcionários da empresa  
- Coletar informações com diferentes setores  
- Elaborar um ESRA completo, conforme as exigências do FSC  

---

## ⚠️ Importante:

Cada setor da empresa possui apenas parte das informações.

Vocês precisarão entrevistar diferentes profissionais para reunir todos os dados necessários.

Algumas informações técnicas deverão ser pesquisadas externamente. Eles não possuem respostas para tudo.

Ao terminar, clique na "Área do professor", salve o arquivo e envie para o professor.

---

Quando estiverem prontos, iniciem a conversa com os funcionários.
""")

        # ✅ Botão agora DENTRO da mesma coluna
        btn_col1, btn_col2, btn_col3 = st.columns([1, 5, 1])

        with btn_col2:
            if st.button("▶️ Iniciar Bate-papo"):
                st.session_state.etapa = "simulacao"
                st.rerun()
# ==========================================
# ETAPA 2 — SIMULAÇÃO
# ==========================================
# ==========================================
# ETAPA 2 — SIMULAÇÃO
# ==========================================

elif st.session_state.etapa == "simulacao":

    col1, col2, col3 = st.columns([1, 5, 1])

    with col2:

        st.title("👷 Funcionários da Empresa SilvaFlora 🧑‍💻")

        if st.button("🔙 Voltar para as instruções"):
            st.session_state.messages = []
            st.session_state.etapa = "apresentacao"
            st.rerun()

        # ==========================================
        # SELEÇÃO DE PERSONAGEM
        # ==========================================

        personagem = st.selectbox(
            "Selecione o profissional que deseja conversar:",
            [
                "👷🏽Cristiano – Gerente de Plantação",
                "👷🏻‍♀️Natália – Analista Ambiental",
                "👩🏻‍💼Isadora – RH",
                "🧑🏻‍💻Yuri – Relações com Comunidade"
            ]
        )

        if personagem != st.session_state.personagem_atual:
            st.session_state.messages = []
            st.session_state.personagem_atual = personagem

        # Definir prompt e voz
        if "Cristiano" in personagem:
            system_prompt = prompt_cristiano
            voz = "onyx"
            avatar_assistente = "👷🏽"
        elif "Natália" in personagem:
            system_prompt = prompt_natalia
            voz = "coral"
            avatar_assistente = "👷🏻‍♀️"
        elif "Isadora" in personagem:
            system_prompt = prompt_isadora
            voz = "shimmer"
            avatar_assistente = "👩🏻‍💼"
        else:
            system_prompt = prompt_yuri
            voz = "onyx"
            avatar_assistente = "🧑🏻‍💻"

        st.divider()

        # ==========================================
        # INPUT ESTILO CHATGPT
        # ==========================================

        pergunta_texto = st.chat_input("Digite sua pergunta e pressione Enter...")
        audio_file = st.audio_input("Ou grave sua pergunta:")

        # ==========================================
        # FUNÇÃO PROCESSAR
        # ==========================================

        def processar_pergunta(pergunta):

            st.session_state.messages.append(
                {"role": "user", "content": pergunta}
            )

           
            with st.spinner("Respondendo..."):
                response = client.responses.create(
                    model="gpt-5.2",
                    input=[
                        {"role": "system", "content": system_prompt},
                        *st.session_state.messages
                    ]
                )

            resposta = response.output_text

            st.session_state.messages.append(
                {"role": "assistant", "content": resposta}
            )

            
            # Gerar áudio
            with client.audio.speech.with_streaming_response.create(
                model="gpt-4o-mini-tts",
                voice=voz,
                input=resposta[:1200]
            ) as audio_response:

                audio_bytes = audio_response.read()

            st.audio(audio_bytes)

        # ==========================================
        # PROCESSAR TEXTO
        # ==========================================

        if pergunta_texto:
            processar_pergunta(pergunta_texto)

        # ==========================================
        # PROCESSAR ÁUDIO
        # ==========================================

        if audio_file is not None:

            with st.spinner("Transcrevendo áudio..."):
                transcript = client.audio.transcriptions.create(
                    model="gpt-4o-transcribe",
                    file=audio_file
                )

            pergunta = transcript.text
            processar_pergunta(pergunta)

        # ==========================================
        # HISTÓRICO COMPLETO
        # ==========================================

        st.divider()

        for msg in st.session_state.messages:

            if msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(msg["content"])
            else:
                with st.chat_message("assistant", avatar=avatar_assistente):
                    st.markdown(msg["content"])

        st.divider()

        # ==========================================
        # BOTÃO NOVA CONVERSA
        # ==========================================

        btn1, btn2, btn3 = st.columns([1,2,1])
        with btn2:
            if st.button("🔄 Nova Conversa", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        # ==========================================
        # ÁREA DO PROFESSOR
        # ==========================================

        st.divider()

        with st.expander("🔒 Área do Professor"):

            import json

            log_json = json.dumps(
                st.session_state.messages,  # ou messages_log_professor se você estiver usando
                indent=2,
                ensure_ascii=False
            )

            st.download_button(
                label="📥 Baixar histórico completo",
                data=log_json,
                file_name="historico_esra.json",
                mime="application/json",
                use_container_width=True
            )
