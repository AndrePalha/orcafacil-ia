import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import tempfile
import os

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="OrçaFácil IA", page_icon="🎙️", layout="centered")

# --- SEGURANÇA ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Configure a chave no Secrets do Streamlit!")

# Usando o modelo que sabemos que funciona na sua conta
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
    
    # Tratamento de erros de caracteres (acentos)
    texto_limpo = texto_orcamento.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=texto_limpo)
    
    nome_arquivo = f"Orcamento_{nome_cliente}.pdf"
    caminho = os.path.join(tempfile.gettempdir(), nome_arquivo)
    pdf.output(caminho)
    return caminho

# --- TELA ---
st.title("🎙️ OrçaFácil V2")
st.write("Fale o serviço, receba o PDF.")

with st.expander("👤 Seus Dados", expanded=False):
    meu_nome = st.text_input("Seu Nome", "Renato Profissional")
    meu_contato = st.text_input("Seu Zap", "(11) 99999-9999")

nome_cliente = st.text_input("Nome do Cliente", "Sr. João")

# --- ÁREA DE ÁUDIO ---
st.write("---")
audio_gravado = st.audio_input("🎙️ Clique para gravar o orçamento")
texto_manual = st.text_area("✍️ Ou escreva aqui:")

if st.button("🚀 GERAR PDF"):
    if not audio_gravado and not texto_manual:
        st.warning("Grave ou escreva algo!")
        st.stop()
        
    with st.spinner("Processando..."):
        try:
            prompt_texto = f"""
            Aja como um orçamentista experiente.
            Prestador: {meu_nome}, {meu_contato}.
            Cliente: {nome_cliente}.
            
            Tarefa: Crie um orçamento formal e técnico.
            1. Liste materiais e mão de obra separados.
            2. Calcule o total.
            3. Use linguagem profissional.
            """
            
            conteudo_para_enviar = []
            
            # LÓGICA NOVA: ENVIO DIRETO (SEM UPLOAD)
            if audio_gravado:
                # Lê os bytes do áudio direto da memória
                dados_audio = audio_gravado.read()
                
                # Monta o pacote para a IA
                conteudo_para_enviar = [
                    prompt_texto,
                    {
                        "mime_type": "audio/wav",
                        "data": dados_audio
                    }
                ]
            else:
                # Apenas texto
                conteudo_para_enviar = [prompt_texto + f"\n\nServiço: {texto_manual}"]
            
            # Chama a IA
            resposta = model.generate_content(conteudo_para_enviar)
            msg_final = resposta.text
            
            # Mostra na tela
            st.markdown("### Resultado:")
            st.write(msg_final)
            
            # Gera PDF
            pdf_path = gerar_pdf(msg_final.replace("*", ""), nome_cliente)
            with open(pdf_path, "rb") as f:
                st.download_button("⬇️ Baixar Orçamento em PDF", f, file_name=f"Orcamento_{nome_cliente}.pdf")
                
        except Exception as e:
            st.error(f"Erro: {e}")
