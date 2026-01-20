import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import tempfile
import os

# --- CONFIGURAÇÃO ---
MINHA_CHAVE = "AIzaSyCPtc_Ajj51xH578kOnY34trlLGiHpwVw8"
genai.configure(api_key=MINHA_CHAVE)
model = genai.GenerativeModel('models/gemini-flash-latest')

st.set_page_config(page_title="OrçaFácil IA", page_icon="🛠️", layout="centered")

# --- FUNÇÃO PARA GERAR PDF ---
def gerar_pdf(texto_orcamento, nome_cliente):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Cabeçalho Simulado
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="ORÇAMENTO DE PRESTAÇÃO DE SERVIÇOS", ln=1, align='C')
    pdf.ln(10)
    
    # Corpo do texto
    pdf.set_font("Arial", size=12)
    # O multi_cell quebra o texto automaticamente
    # Precisamos tratar caracteres especiais, o FPDF é chato com acentos diretos,
    # então vamos usar uma codificação simples latin-1 para o MVP
    texto_limpo = texto_orcamento.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=texto_limpo)
    
    # Salvar temporariamente
    nome_arquivo = f"Orcamento_{nome_cliente}.pdf"
    caminho = os.path.join(tempfile.gettempdir(), nome_arquivo)
    pdf.output(caminho)
    return caminho

# --- INTERFACE ---
st.title("🛠️ OrçaFácil IA")
st.subheader("Fale o que precisa ser feito, e eu crio o documento.")

# 1. Dados do Profissional (Simulação)
with st.expander("👤 Seus Dados (Configuração)", expanded=False):
    meu_nome = st.text_input("Seu Nome/Empresa", "Renato Soluções Técnicas")
    meu_contato = st.text_input("Seu Telefone", "(45) 99999-9999")

# 2. Dados do Cliente
col1, col2 = st.columns(2)
nome_cliente = col1.text_input("Nome do Cliente", "Cliente Exemplo")
data_prazo = col2.date_input("Prazo de Validade")

# 3. Entrada de Áudio ou Texto
tab1, tab2 = st.tabs(["🎙️ Gravar Áudio", "✍️ Digitar"])

with tab1:
    audio_bytes = st.audio_input("Grave os detalhes do serviço:")

with tab2:
    texto_manual = st.text_area("Ou digite os detalhes aqui:")

# --- O CÉREBRO DA OPERAÇÃO ---
if st.button("🚀 Gerar Orçamento Profissional", type="primary"):
    
    conteudo_para_ia = ""
    
    if audio_bytes:
        # Gemini processa áudio diretamente? 
        # Para simplificar neste código MVP sem subir arquivo complexo, 
        # vamos pedir para você descrever o áudio ou usar o texto.
        # *Nota Técnica: Para áudio real no Gemini via API, precisa de upload de arquivo.
        # Vamos usar o modo TEXTO primeiro para validar a ideia, 
        # ou simular que o áudio foi transcrito.*
        st.warning("⚠️ Nesta versão V1, por favor use a aba 'Digitar' enquanto configuramos o processamento de áudio na nuvem.")
        conteudo_para_ia = None # Travando áudio por enquanto para não dar erro
    elif texto_manual:
        conteudo_para_ia = texto_manual
    
    if conteudo_para_ia:
        with st.spinner("🤖 A IA está calculando, formatando e criando a proposta..."):
            try:
                # O Prompt de Engenharia (O Segredo do Negócio)
                prompt = f"""
                Aja como um orçamentista profissional.
                Eu sou: {meu_nome}, Contato: {meu_contato}.
                Cliente: {nome_cliente}.
                
                Informações bruta do serviço: "{conteudo_para_ia}"
                
                Sua tarefa:
                1. Identifique materiais e mão de obra.
                2. Se eu falei de um jeito informal, reescreva de forma técnica e profissional.
                3. Crie uma tabela de valores somados.
                4. Escreva um texto cordial de apresentação.
                5. O resultado deve ser um texto formatado pronto para virar documento.
                """
                
                resposta = model.generate_content(prompt)
                texto_final = resposta.text
                
                # Mostra na tela
                st.markdown("### 📄 Prévia do Documento")
                st.markdown(texto_final)
                
                # Gera o PDF
                # Limpeza básica para o PDF não quebrar com Markdown
                texto_para_pdf = texto_final.replace("*", "").replace("#", "") 
                arquivo_pdf = gerar_pdf(texto_para_pdf, nome_cliente)
                
                # Botão de Download
                with open(arquivo_pdf, "rb") as pdf_file:
                    st.download_button(
                        label="⬇️ Baixar PDF Pronto",
                        data=pdf_file,
                        file_name=f"Orcamento_{nome_cliente}.pdf",
                        mime="application/pdf"
                    )
                    
            except Exception as e:
                st.error(f"Erro: {e}")
    else:
        if not audio_bytes:
            st.warning("Descreva o serviço primeiro!")