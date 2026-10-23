"""
MIT License

Copyright (c) 2026 Arquiteto de Software IA

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
from openai import OpenAI
import streamlit as st

# ==========================================
# CONFIGURAÇÃO DA PÁGINA DO STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Extrator de Dados Inteligente | Azure OpenAI",
    page_icon="🤖",
    layout="centered",
)

# ==========================================
# INICIALIZAÇÃO DO CLIENTE OPENAI (COMPATÍVEL COM AZURE AI FOUNDRY)
# ==========================================
try:
  AZURE_ENDPOINT = st.secrets["azure_openai"]["endpoint"]
  AZURE_API_KEY = st.secrets["azure_openai"]["api_key"]
  MODEL_NAME = st.secrets["azure_openai"].get("deployment_name", "gpt-4.1-mini")
except Exception:
  # Valores padrão fornecidos para execução imediata
  AZURE_ENDPOINT = (
      "https://marcelomaffeis-7430-resource.services.ai.azure.com/openai/v1"
  )
  AZURE_API_KEY = (
      "1gsyJYiGIr1rIjIm6heIq96VWJI5gMgXeXCaYCHx5WeeWGm3AMYvJQQJ99CJACHYHv6XJ3w3AAAAACOGUF3S"
  )
  MODEL_NAME = "gpt-4.1-mini"

# Instanciação corrigida usando o cliente padrão OpenAI com base_url
client = OpenAI(api_key=AZURE_API_KEY, base_url=AZURE_ENDPOINT)

# ==========================================
# INTERFACE DO USUÁRIO (UI)
# ==========================================
st.title("🤖 Extrator de Dados Inteligente")
st.markdown(
    "Aplicação corporativa integrada à infraestrutura **Microsoft Azure"
    " OpenAI / AI Foundry** para análise estruturada de texto."
)

st.divider()

# Campo de entrada de texto
texto_usuario = st.text_area(
    "Digite ou cole o texto a ser analisado:",
    placeholder=(
        "Exemplo: 'Reunião urgente agendada com Ana Souza e Carlos para"
        " amanhã às 15h. Precisamos corrigir o bug crítico no servidor"
        " principal antes do lançamento...'"
    ),
    height=150,
)

# Botão de processamento
if st.button("Processar Texto", type="primary", use_container_width=True):
  if not texto_usuario.strip():
    st.warning(
        "Por favor, insira um texto válido no campo acima antes de processar."
    )
  else:
    with st.spinner("Analisando dados via Azure OpenAI..."):
      try:
        # System Prompt rígido garantindo o contrato de saída em JSON
        system_prompt = (
            "Você é um Arquiteto de Software e Analista de Dados especialista"
            " em extração de informações.\nAnalise o texto fornecido pelo"
            " usuário e retorne EXCLUSIVAMENTE um objeto JSON válido contendo"
            " exatamente as seguintes chaves:\n1. 'sentimento': String"
            " indicando o sentimento geral (ex: Positivo, Negativo, Neutro).\n2."
            " 'porcentagem_sentimento': Número inteiro de 0 a 100 indicando a"
            " intensidade/confiança desse sentimento.\n3."
            " 'assunto_principal': String resumindo o assunto principal do"
            " texto em poucas palavras.\n4. 'pessoas_citadas': Lista (array)"
            " de strings contendo os nomes das pessoas mencionadas no texto"
            " (vazia se nenhuma).\n5. 'nivel_de_urgencia': String contendo"
            " estritamente um destes três valores: 'Baixo', 'Medio' ou"
            " 'Alto'."
        )

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": texto_usuario},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )

        # Captura e desserializa o JSON retornado pela API
        conteudo_json = response.choices[0].message.content
        dados_extraidos = json.loads(conteudo_json)

        st.success("Processamento concluído com sucesso!")
        st.divider()

        # Exibição estruturada dos resultados usando métricas e componentes visuais
        st.subheader("📊 Resultados Extraídos")

        col1, col2 = st.columns(2)

        sentimento = dados_extraidos.get("sentimento", "N/A")
        porcentagem = dados_extraidos.get("porcentagem_sentimento", 0)
        urgencia = dados_extraidos.get("nivel_de_urgencia", "Baixo")

        with col1:
          st.metric(
              label="Sentimento Detectado",
              value=sentimento,
              delta=f"{porcentagem}% de intensidade",
          )

        with col2:
          st.metric(label="Nível de Urgência", value=urgencia)

        st.markdown(
            "**Assunto Principal:**"
            f" {dados_extraidos.get('assunto_principal', 'N/A')}"
        )

        pessoas = dados_extraidos.get("pessoas_citadas", [])
        if pessoas:
          st.markdown("**Pessoas Citadas:**")
          for pessoa in pessoas:
            st.markdown(f"- {pessoa}")
        else:
          st.markdown("**Pessoas Citadas:** Nenhuma pessoa identificada.")

        with st.expander("🔍 Visualizar JSON Bruto (Raw JSON)"):
          st.json(dados_extraidos)

      except Exception as e:
        st.error(f"Ocorreu um erro durante a chamada à API do Azure OpenAI: {e}")
