import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import tempfile
import os

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="OrçaFácil IA", page_icon="🎙️", layout="centered")

# --- SEGURANÇA (COFRE) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Configure a chave no Secrets do Streamlit!")

# --- MODELO CORRIGIDO (O SEGREDO ESTÁ AQUI) ---
model = genai.GenerativeModel('models/gemini-flash-latest')

# --- FUNÇÃO PDF ---
def gerar_pdf(texto_orcamento, nome_cliente):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="ORÇAMENTO PROFISSIONAL", ln=1, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    # Correção de caracteres
    texto_limpo = texto_orcamento.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=texto_limpo)
    
    nome_arquivo = f"Orcamento_{nome_cliente}.pdf"
    caminho = os.path.join(tempfile.gettempdir(), nome_arquivo)
    pdf.output(caminho)
    return caminho

# --- TELA ---
st.title("🎙️ OrçaFácil: Fale e Pronto")
st.info("Dica: Fale o serviço e o valor, eu faço o resto.")

with st.expander("👤 Seus Dados", expanded=False):
    meu_nome = st.text_input("Seu Nome", "Renato Profissional")
    meu_contato = st.text_input("Seu Zap", "(11) 99999-9999")

nome_cliente = st.text_input("Nome do Cliente", "Sr. João")

# --- ÁREA DE ÁUDIO ---
st.write("---")
st.markdown("### 🗣️ O que precisa fazer?")
audio_gravado = st.audio_input("Clique para gravar")
texto_manual = st.text_area("Ou escreva aqui:")

if st.button("🚀 GERAR ORÇAMENTO"):
    if not audio_gravado and not texto_manual:
        st.warning("Grave ou escreva algo!")
        st.stop()
        
    with st.spinner("Ouvindo e escrevendo..."):
        try:
            prompt = f"""
            Aja como um orçamentista. Dados: {meu_nome}, {meu_contato}.
            Cliente: {nome_cliente}.
            Crie um orçamento técnico, com tabela de valores e total.
            Seja formal.
            """
            
            # Processamento
            if audio_gravado:
                # Salva áudio temporário
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(audio_gravado.read())
                    path = tmp.name
                
                # Envia pro Google
                arquivo = genai.upload_file(path)
                resposta = model.generate_content([prompt, arquivo])
                msg_final = resposta.text
            else:
                resposta = model.generate_content(prompt + f"\nServiço: {texto_manual}")
                msg_final = resposta.text
            
            st.markdown(msg_final)
            
            # Baixar PDF
            pdf_path = gerar_pdf(msg_final.replace("*", ""), nome_cliente)
            with open(pdf_path, "rb") as f:
                st.download_button("⬇️ Baixar PDF", f, file_name="Orcamento.pdf")
                
        except Exception as e:
            st.error(f"Erro: {e}")
