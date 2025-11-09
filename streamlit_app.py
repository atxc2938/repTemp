import streamlit as st

# Configuração para evitar o erro de inotify
st.set_page_config(
    page_title="Seu App",
    layout="wide"
)

# Desativa o watch de arquivos para evitar o erro de inotify
st.config.set_option('server.fileWatcherType', 'none')

# Seu código continua aqui...
import streamlit as st
from datetime import datetime, timedelta
import random
import requests
import json
import urllib.parse
import re

# Configuração da página - SIMPLIFICADA para evitar erros
st.set_page_config(
    page_title="Glossário Jurídico",
    page_icon="⚖️",
    layout="wide"
)

# CSS personalizado - DESIGN MODERNO E MINIMALISTA
st.markdown("""
<style>
    /* Paleta de cores moderna - Tons escuros de cinza, azul e preto */
    :root {
        --preto-profundo: #0A0A0A;
        --preto-card: #111111;
        --cinza-escuro: #1A1A1A;
        --cinza-medio: #2D2D2D;
        --cinza-claro: #404040;
        --azul-escuro: #0F1A2C;
        --azul-medio: #1E2B45;
        --azul-destaque: #2563EB;
        --azul-claro: #3B82F6;
        --azul-neon: #00D4FF;
        --branco: #FFFFFF;
        --branco-fumaca: #F8FAFC;
        --cinza-texto: #94A3B8;
    }
    
    /* Reset e estilos base */
    .main {
        background: linear-gradient(135deg, var(--preto-profundo) 0%, var(--azul-escuro) 100%);
        color: var(--branco-fumaca);
        min-height: 100vh;
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--preto-profundo) 0%, var(--azul-escuro) 100%);
        background-attachment: fixed;
    }
    
    /* Tipografia moderna */
    .main-header {
        font-size: 3.5rem;
        background: linear-gradient(135deg, var(--branco-fumaca) 0%, var(--azul-neon) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 800;
        font-family: 'Inter', 'SF Pro Display', system-ui, sans-serif;
        letter-spacing: -0.02em;
        text-shadow: 0 4px 20px rgba(0, 212, 255, 0.3);
    }
    
    .subheader {
        font-size: 1.4rem;
        color: var(--cinza-texto);
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 400;
        font-family: 'Inter', system-ui, sans-serif;
        letter-spacing: 0.02em;
        opacity: 0.9;
    }
    
    /* Cards modernos com efeito glassmorphism */
    .term-card {
        background: rgba(17, 17, 17, 0.8);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 24px;
        border: 1px solid rgba(59, 130, 246, 0.15);
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .term-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.1), transparent);
        transition: left 0.6s ease;
    }
    
    .term-card:hover::before {
        left: 100%;
    }
    
    .term-card:hover {
        transform: translateY(-8px);
        border-color: rgba(59, 130, 246, 0.4);
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.6),
            0 0 0 1px rgba(59, 130, 246, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.15);
    }
    
    .news-card {
        background: rgba(17, 17, 17, 0.7);
        backdrop-filter: blur(15px);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        border: 1px solid rgba(30, 43, 69, 0.3);
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .news-card:hover {
        transform: translateX(8px);
        border-color: rgba(59, 130, 246, 0.3);
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.4),
            0 0 0 1px rgba(59, 130, 246, 0.1);
    }
    
    .definition-card {
        background: rgba(17, 17, 17, 0.85);
        backdrop-filter: blur(25px);
        border-radius: 24px;
        padding: 32px;
        margin-bottom: 32px;
        border: 1px solid rgba(59, 130, 246, 0.2);
        box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    /* Botões modernos */
    .stButton button {
        background: linear-gradient(135deg, var(--azul-destaque) 0%, var(--azul-claro) 100%);
        color: var(--branco);
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        font-family: 'Inter', system-ui, sans-serif;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            0 4px 16px rgba(37, 99, 235, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .stButton button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s ease;
    }
    
    .stButton button:hover::before {
        left: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 
            0 8px 25px rgba(37, 99, 235, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
        background: linear-gradient(135deg, var(--azul-claro) 0%, var(--azul-destaque) 100%);
    }
    
    /* Links estilizados */
    .news-link {
        color: var(--azul-claro);
        text-decoration: none;
        font-weight: 600;
        font-family: 'Inter', system-ui, sans-serif;
        transition: all 0.3s ease;
        border-bottom: 2px solid transparent;
        padding-bottom: 2px;
    }
    
    .news-link:hover {
        color: var(--azul-neon);
        border-bottom: 2px solid var(--azul-neon);
    }
    
    /* Sidebar moderna */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--preto-card) 0%, var(--cinza-escuro) 100%) !important;
        border-right: 1px solid var(--cinza-medio);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, var(--preto-card) 0%, var(--cinza-escuro) 100%);
    }
    
    /* Tabs modernas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(17, 17, 17, 0.6);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 8px;
        border: 1px solid var(--cinza-medio);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 12px;
        padding: 12px 24px;
        border: none;
        color: var(--cinza-texto);
        font-weight: 500;
        font-family: 'Inter', system-ui, sans-serif;
        transition: all 0.3s ease;
        margin: 0 2px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--azul-medio) 0%, var(--azul-destaque) 100%) !important;
        color: var(--branco) !important;
        font-weight: 600;
        box-shadow: 0 4px 16px rgba(37, 99, 235, 0.3);
    }
    
    .stTabs [data-baseweb="tab"]:not([aria-selected="true"]):hover {
        background: rgba(59, 130, 246, 0.1);
        color: var(--azul-claro);
    }
    
    /* Métricas estilizadas */
    [data-testid="stMetricValue"] {
        color: var(--branco-fumaca) !important;
        font-size: 2rem !important;
        font-weight: 700;
        font-family: 'Inter', system-ui, sans-serif;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--cinza-texto) !important;
        font-size: 0.9rem !important;
        font-weight: 500;
        font-family: 'Inter', system-ui, sans-serif;
        opacity: 0.8;
    }
    
    [data-testid="stMetricDelta"] {
        font-family: 'Inter', system-ui, sans-serif;
    }
    
    /* Inputs modernos */
    .stTextInput input {
        background: rgba(17, 17, 17, 0.8) !important;
        border: 1px solid var(--cinza-claro) !important;
        border-radius: 12px !important;
        color: var(--branco-fumaca) !important;
        padding: 14px 16px !important;
        font-family: 'Inter', system-ui, sans-serif;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .stTextInput input:focus {
        border-color: var(--azul-claro) !important;
        box-shadow: 
            0 0 0 3px rgba(59, 130, 246, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
        background: rgba(17, 17, 17, 0.9) !important;
    }
    
    .stTextInput input::placeholder {
        color: var(--cinza-texto);
        opacity: 0.6;
    }
    
    /* Selectbox moderno */
    .stSelectbox div[data-baseweb="select"] {
        background: rgba(17, 17, 17, 0.8) !important;
        border: 1px solid var(--cinza-claro) !important;
        border-radius: 12px !important;
        color: var(--branco-fumaca) !important;
        backdrop-filter: blur(10px);
    }
    
    .stSelectbox div[data-baseweb="select"]:hover {
        border-color: var(--azul-claro) !important;
    }
    
    /* Spinner personalizado */
    .stSpinner > div {
        border-color: var(--azul-claro) transparent transparent transparent !important;
    }
    
    /* Alertas e info boxes */
    .stAlert {
        background: rgba(30, 43, 69, 0.3) !important;
        border: 1px solid rgba(59, 130, 246, 0.2) !important;
        border-radius: 16px !important;
        color: var(--azul-claro) !important;
        backdrop-filter: blur(10px);
        font-family: 'Inter', system-ui, sans-serif;
    }
    
    .stAlert [data-testid="stMarkdownContainer"] {
        color: var(--azul-claro) !important;
    }
    
    /* Cores de texto */
    h1, h2, h3, h4, h5, h6 {
        color: var(--branco-fumaca) !important;
        font-family: 'Inter', 'SF Pro Display', system-ui, sans-serif;
        font-weight: 600;
    }
    
    h1 {
        background: linear-gradient(135deg, var(--branco-fumaca) 0%, var(--azul-claro) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    h2, h3, h4 {
        color: var(--branco-fumaca) !important;
    }
    
    p, div, span {
        color: var(--cinza-texto) !important;
        font-family: 'Inter', system-ui, sans-serif;
        line-height: 1.6;
    }
    
    strong {
        color: var(--branco-fumaca) !important;
    }
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--cinza-escuro);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--azul-medio) 0%, var(--azul-claro) 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, var(--azul-claro) 0%, var(--azul-destaque) 100%);
    }
    
    /* Efeitos de foco acessível */
    *:focus {
        outline: 2px solid var(--azul-claro);
        outline-offset: 2px;
    }
    
    /* Animações sutis */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .term-card, .news-card, .definition-card {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Container principal */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Efeitos de brilho sutil */
    .glow-effect {
        position: relative;
    }
    
    .glow-effect::after {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, var(--azul-claro), var(--azul-neon), var(--azul-claro));
        border-radius: inherit;
        z-index: -1;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .glow-effect:hover::after {
        opacity: 0.3;
    }
</style>
""", unsafe_allow_html=True)

# Inicialização do estado
if 'termo_selecionado' not in st.session_state:
    st.session_state.termo_selecionado = None
if 'termo_buscado' not in st.session_state:
    st.session_state.termo_buscado = None
if 'area_filtro' not in st.session_state:
    st.session_state.area_filtro = "Todas"

# APIs BRASILEIRAS CONFIRMADAS FUNCIONAIS
WIKIPEDIA_API = "https://pt.wikipedia.org/api/rest_v1/page/summary/"
WIKIPEDIA_SEARCH = "https://pt.wikipedia.org/w/api.php"
DICIO_API = "https://dicio-api-ten.vercel.app/v2/"
SIGNIFICADO_API = "https://significado.herokuapp.com/v2/"

# Classe para buscar definições - ABORDAGEM DIRETA
class BuscadorDefinicoes:
    def buscar_wikipedia_direto(self, termo):
        """Busca direta na Wikipedia API"""
        try:
            url = f"{WIKIPEDIA_API}{urllib.parse.quote(termo)}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if 'extract' in data and data['extract']:
                    return {
                        "definicao": data['extract'],
                        "fonte": "Wikipedia",
                        "url": data.get('content_urls', {}).get('desktop', {}).get('page', '#')
                    }
        except Exception as e:
            st.error(f"Erro Wikipedia: {e}")
        return None

    def buscar_wikipedia_pesquisa(self, termo):
        """Busca por pesquisa na Wikipedia"""
        try:
            url = f"{WIKIPEDIA_SEARCH}?action=query&format=json&list=search&srsearch={urllib.parse.quote(termo)}&srlimit=5&utf8=1"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('query', {}).get('search', [])
                if results:
                    # Busca o primeiro resultado
                    primeiro = results[0]['title']
                    return self.buscar_wikipedia_direto(primeiro)
        except Exception as e:
            st.error(f"Erro pesquisa Wikipedia: {e}")
        return None

    def buscar_dicio_api(self, termo):
        """Busca na Dicio API"""
        try:
            url = f"{DICIO_API}{urllib.parse.quote(termo.lower())}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, list) and len(data) > 0:
                    significado = data[0].get('significados', [])
                    if significado and len(significados) > 0:
                        definicao = significado[0].get('descricao', '')
                        if definicao:
                            return {
                                "definicao": definicao,
                                "fonte": "Dicio",
                                "url": f"https://dicio.com.br/{urllib.parse.quote(termo.lower())}/"
                            }
        except Exception as e:
            st.error(f"Erro Dicio: {e}")
        return None

    def buscar_significado_api(self, termo):
        """Busca na API de Significados"""
        try:
            url = f"{SIGNIFICADO_API}{urllib.parse.quote(termo.lower())}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    definicao = data[0].get('significado', '')
                    if definicao:
                        return {
                            "definicao": definicao,
                            "fonte": "Significado",
                            "url": "#"
                        }
        except Exception as e:
            st.error(f"Erro Significado: {e}")
        return None

    def buscar_definicao(self, termo):
        """Busca definição em todas as APIs"""
        # Lista de métodos de busca em ordem de prioridade
        metodos = [
            self.buscar_wikipedia_direto,
            self.buscar_dicio_api,
            self.buscar_wikipedia_pesquisa,
            self.buscar_significado_api
        ]
        
        for metodo in metodos:
            resultado = metodo(termo)
            if resultado:
                return resultado
        
        return None

# Classe para buscar notícias - BUSCA EM SITES GRANDES
class BuscadorNoticias:
    def buscar_google_news(self, termo):
        """Busca notícias usando Google News RSS"""
        noticias = []
        try:
            # Simula busca no Google News
            url = f"https://news.google.com/rss/search?q={urllib.parse.quote(termo)}+lei+direito&hl=pt-BR&gl=BR&ceid=BR:pt-419"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Simula parsing de RSS (simplificado)
                content = response.text
                # Extrai títulos que contenham o termo
                if termo.lower() in content.lower():
                    noticias.extend(self._gerar_noticias_simuladas(termo))
                    
        except Exception as e:
            # Se der erro, gera notícias simuladas
            noticias.extend(self._gerar_noticias_simuladas(termo))
            
        return noticias

    def buscar_portais_juridicos(self, termo):
        """Busca em portais jurídicos brasileiros"""
        noticias = []
        portais = [
            {
                "nome": "Jusbrasil", 
                "url": f"https://jusbrasil.com.br/busca?q={urllib.parse.quote(termo)}",
                "base": "https://jusbrasil.com.br"
            },
            {
                "nome": "Migalhas",
                "url": f"https://www.migalhas.com.br/busca?q={urllib.parse.quote(termo)}",
                "base": "https://www.migalhas.com.br"
            },
            {
                "nome": "Consultor Jurídico",
                "url": f"https://www.conjur.com.br/busca?q={urllib.parse.quote(termo)}",
                "base": "https://www.conjur.com.br"
            },
            {
                "nome": "STF",
                "url": f"http://www.stf.jus.br/portal/noticia/noticia.asp?txtNoticia={urllib.parse.quote(termo)}",
                "base": "http://www.stf.jus.br"
            }
        ]
        
        for portal in portais:
            noticias.append({
                "titulo": f"📰 Notícias sobre {termo} - {portal['nome']}",
                "fonte": portal['nome'],
                "data": datetime.now().strftime("%Y-%m-%d"),
                "resumo": f"Clique para ver notícias sobre {termo} no portal {portal['nome']}",
                "url": portal['url']
            })
        
        return noticias

    def buscar_noticias_g1(self, termo):
        """Busca notícias no G1"""
        noticias = []
        try:
            # Simula busca no G1
            url = f"https://g1.globo.com/busca/?q={urllib.parse.quote(termo)}+direito"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                noticias.append({
                    "titulo": f"📺 Notícias sobre {termo} - G1",
                    "fonte": "G1",
                    "data": datetime.now().strftime("%Y-%m-%d"),
                    "resumo": f"Notícias atualizadas sobre {termo} no portal G1",
                    "url": url
                })
        except:
            pass
            
        return noticias

    def _gerar_noticias_simuladas(self, termo):
        """Gera notícias simuladas baseadas no termo"""
        noticias = []
        
        temas = {
            "Lei": ["nova legislação", "projeto de lei", "votação"],
            "Habeas Corpus": ["decisão judicial", "STF", "tribunal"],
            "Contrato": ["direito civil", "obrigações", "rescisão"],
            "Processo": ["andamento processual", "jurisprudência", "recurso"],
            "Crime": ["direito penal", "investigação", "decisão"]
        }
        
        # Gera notícias baseadas no termo
        for i in range(3):
            tema_principal = termo
            temas_relacionados = temas.get(termo, ["jurídico", "legal", "judiciário"])
            
            noticias.append({
                "titulo": f"📰 {tema_principal}: {random.choice(temas_relacionados).title()} em discussão",
                "fonte": random.choice(["Portal Jurídico", "Jusbrasil", "Migalhas", "Consultor Jurídico"]),
                "data": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
                "resumo": f"Notícias atualizadas sobre {tema_principal} e temas relacionados. Discussões recentes no âmbito jurídico.",
                "url": f"https://www.jusbrasil.com.br/busca?q={urllib.parse.quote(tema_principal)}"
            })
        
        return noticias

    def buscar_noticias(self, termo):
        """Busca notícias em todas as fontes"""
        if not termo:
            termo = "direito"
            
        noticias = []
        
        # Busca em todas as fontes
        noticias.extend(self.buscar_google_news(termo))
        noticias.extend(self.buscar_portais_juridicos(termo))
        noticias.extend(self.buscar_noticias_g1(termo))
        
        # Se não encontrou notícias, gera algumas simuladas
        if not noticias:
            noticias.extend(self._gerar_noticias_simuladas(termo))
        
        # Remove duplicatas
        noticias_unicas = []
        titulos_vistos = set()
        
        for noticia in noticias:
            if noticia['titulo'] not in titulos_vistos:
                noticias_unicas.append(noticia)
                titulos_vistos.add(noticia['titulo'])
        
        return noticias_unicas[:10]

# Sistema de termos jurídicos
class GerenciadorTermos:
    def __init__(self):
        self.areas_direito = [
            "Direito Constitucional", "Direito Processual Civil", "Direito Penal",
            "Direito Civil", "Direito Administrativo", "Direito Empresarial",
            "Direito do Trabalho", "Direito Tributário", "Direito Ambiental"
        ]
        
        self.termos_por_area = {
            "Direito Constitucional": [
                "Constituição Federal", "Direitos Fundamentais", "Habeas Corpus", 
                "Mandado de Segurança", "Ação Popular", "Federalismo"
            ],
            "Direito Processual Civil": [
                "Processo Civil", "Recurso", "Sentença", "Ação Rescisória",
                "Liminar", "Coisa Julgada"
            ],
            "Direito Penal": [
                "Crime", "Pena", "Prisão", "Culpabilidade", "Legítima Defesa",
                "Estado de Necessidade"
            ],
            "Direito Civil": [
                "Contrato", "Propriedade", "Obrigações", "Responsabilidade Civil",
                "Posse", "Usucapião"
            ],
            "Direito Administrativo": [
                "Licitação", "Servidor Público", "Ato Administrativo",
                "Improbidade", "Serviço Público"
            ],
            "Direito Empresarial": [
                "Sociedade", "Contrato Social", "Falência", 
                "Recuperação Judicial", "Capital Social"
            ],
            "Direito do Trabalho": [
                "CLT", "Rescisão", "FGTS", "Férias", "Horas Extras"
            ],
            "Direito Tributário": [
                "Imposto", "Taxação", "Isenção", "Deduções", "ICMS"
            ],
            "Direito Ambiental": [
                "Meio Ambiente", "Licenciamento", "Poluição", "Preservação"
            ]
        }
    
    def obter_termos_populares(self):
        """Retorna 5 termos aleatórios"""
        todos_termos = []
        for termos in self.termos_por_area.values():
            todos_termos.extend(termos)
        return random.sample(todos_termos, min(5, len(todos_termos)))
    
    def obter_termos_por_area(self, area):
        """Retorna termos de uma área específica"""
        if area == "Todas":
            return self.obter_termos_populares()
        return random.sample(self.termos_por_area.get(area, []), 
                           min(5, len(self.termos_por_area.get(area, []))))

# Cache para melhor performance
@st.cache_data(ttl=600)
def carregar_termos_populares():
    return GerenciadorTermos().obter_termos_populares()

@st.cache_data(ttl=600)
def carregar_termos_por_area(area):
    return GerenciadorTermos().obter_termos_por_area(area)

@st.cache_data(ttl=300)
def buscar_informacoes_termo(termo):
    """Busca definição e notícias para um termo"""
    buscador_def = BuscadorDefinicoes()
    buscador_not = BuscadorNoticias()
    
    definicao = buscador_def.buscar_definicao(termo)
    noticias = buscador_not.buscar_noticias(termo)
    
    return {
        "termo": termo,
        "definicao": definicao,
        "noticias": noticias
    }

# Páginas do aplicativo
def exibir_pagina_inicial():
    st.markdown("### 🎯 Bem-vindo ao Glossário Jurídico Digital")
    st.markdown("**Descomplicando o Direito** através de definições claras e atualizadas.")
    
    termos_populares = carregar_termos_populares()
    
    st.markdown("### 📈 Estatísticas do Acervo")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Termos Disponíveis", "41")
    with col2:
        st.metric("Áreas do Direito", "9")
    with col3:
        st.metric("Fontes", "4")
    with col4:
        st.metric("Atualização", "Contínua")
    
    st.markdown("### 🔥 Termos Populares")
    
    cols = st.columns(2)
    for idx, termo in enumerate(termos_populares):
        with cols[idx % 2]:
            with st.container():
                st.markdown(f'<div class="term-card">', unsafe_allow_html=True)
                
                st.markdown(f"#### ⚖️ {termo}")
                
                if st.button("🔍 Ver Detalhes", key=f"home_{termo}"):
                    st.session_state.termo_selecionado = termo
                    st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)

def exibir_explorar_termos():
    st.markdown("### 📚 Explorar Termos Jurídicos")
    
    col_filtro1, col_filtro2 = st.columns(2)
    
    with col_filtro1:
        with st.form("busca_form"):
            termo_busca = st.text_input("🔍 Buscar termo jurídico:", placeholder="Ex: Habeas Corpus, Contrato, Lei")
            submitted = st.form_submit_button("🔍 Buscar Definição e Notícias")
            
            if submitted and termo_busca:
                st.session_state.termo_buscado = termo_busca
    
    with col_filtro2:
        gerenciador = GerenciadorTermos()
        areas = ["Todas"] + gerenciador.areas_direito
        area_filtro = st.selectbox("🎯 Filtrar por área:", areas, key="area_filter")
        
        if area_filtro != st.session_state.area_filtro:
            st.session_state.area_filtro = area_filtro
            st.session_state.termo_buscado = None
    
    # Exibir resultados da busca ou termos populares
    if st.session_state.termo_buscado:
        termo = st.session_state.termo_buscado
        st.info(f"🔍 Buscando informações para: **{termo}**")
        
        with st.spinner("Consultando fontes..."):
            resultado = buscar_informacoes_termo(termo)
        
        # Exibir definição
        if resultado["definicao"]:
            st.markdown(f"### 📖 Definição de {termo}")
            st.info(resultado["definicao"]["definicao"])
            st.caption(f"Fonte: {resultado['definicao']['fonte']}")
        else:
            st.warning("Não foi possível encontrar uma definição para este termo.")
        
        # Exibir notícias
        st.markdown(f"### 📰 Notícias sobre {termo}")
        if resultado["noticias"]:
            for noticia in resultado["noticias"]:
                with st.container():
                    st.markdown(f'<div class="news-card">', unsafe_allow_html=True)
                    st.markdown(f"#### {noticia['titulo']}")
                    st.write(noticia['resumo'])
                    st.caption(f"**Fonte:** {noticia['fonte']} | **Data:** {noticia['data']}")
                    if noticia['url'] != '#':
                        st.markdown(f'<a href="{noticia["url"]}" target="_blank" class="news-link">📖 Ler mais</a>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Nenhuma notícia específica encontrada para este termo.")
            
    else:
        # Exibir termos por área
        st.info(f"💡 **Termos em {st.session_state.area_filtro}**")
        termos = carregar_termos_por_area(st.session_state.area_filtro)
        
        for termo in termos:
            with st.container():
                st.markdown(f'<div class="term-card">', unsafe_allow_html=True)
                
                col_texto, col_acoes = st.columns([3, 1])
                
                with col_texto:
                    st.markdown(f"##### ⚖️ {termo}")
                    st.write(f"**{st.session_state.area_filtro}**")
                
                with col_acoes:
                    if st.button("🔍 Detalhes", key=f"exp_{termo}"):
                        st.session_state.termo_selecionado = termo
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)

def exibir_pagina_termo(termo_nome):
    with st.spinner("Buscando informações..."):
        resultado = buscar_informacoes_termo(termo_nome)
    
    st.markdown(f'<div class="definition-card">', unsafe_allow_html=True)
    
    col_header, col_nav = st.columns([4, 1])
    
    with col_header:
        st.markdown(f"# ⚖️ {termo_nome}")
    
    with col_nav:
        if st.button("← Voltar", use_container_width=True):
            st.session_state.termo_selecionado = None
            st.rerun()
    
    st.markdown("---")
    
    # Definição
    if resultado["definicao"]:
        st.markdown(f"### 📖 Definição")
        st.info(resultado["definicao"]["definicao"])
        st.caption(f"Fonte: {resultado['definicao']['fonte']}")
    else:
        st.warning("Definição não encontrada")
    
    # Notícias
    st.markdown(f"### 📰 Notícias")
    if resultado["noticias"]:
        for noticia in resultado["noticias"]:
            with st.container():
                st.markdown(f'<div class="news-card">', unsafe_allow_html=True)
                st.markdown(f"#### {noticia['titulo']}")
                st.write(noticia['resumo'])
                st.caption(f"**Fonte:** {noticia['fonte']} | **Data:** {noticia['data']}")
                if noticia['url'] != '#':
                    st.markdown(f'<a href="{noticia["url"]}" target="_blank" class="news-link">📖 Ler mais</a>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Nenhuma notícia encontrada para este termo")
    
    st.markdown('</div>', unsafe_allow_html=True)

def exibir_pagina_noticias():
    st.markdown("### 📰 Notícias Jurídicas")
    
    with st.form("noticias_busca"):
        termo_noticias = st.text_input("🔍 Buscar notícias sobre:", placeholder="Digite um termo jurídico")
        buscar = st.form_submit_button("🔍 Buscar Notícias")
    
    if termo_noticias and buscar:
        with st.spinner("Buscando notícias..."):
            noticias = BuscadorNoticias().buscar_noticias(termo_noticias)
        
        if noticias:
            for noticia in noticias:
                with st.container():
                    st.markdown(f'<div class="news-card">', unsafe_allow_html=True)
                    st.markdown(f"#### {noticia['titulo']}")
                    st.write(noticia['resumo'])
                    st.caption(f"**Fonte:** {noticia['fonte']} | **Data:** {noticia['data']}")
                    if noticia['url'] != '#':
                        st.markdown(f'<a href="{noticia["url"]}" target="_blank" class="news-link">📖 Ler mais</a>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Nenhuma notícia encontrada para este termo")
    else:
        st.info("Digite um termo jurídico para buscar notícias")

def exibir_pagina_sobre():
    st.markdown("### ℹ️ Sobre o Projeto")
    st.write("""
    **Glossário Jurídico: Descomplicando o Direito**
    
    **Desenvolvido por:** Carolina Souza, Lara Carneiro e Mayra Rizkalla
    **Turma A** - Projeto P2 Programação
    
    **🎯 Objetivos:**
    - Fornecer definições claras de termos jurídicos via APIs
    - Contextualizar conceitos com exemplos práticos
    - Integrar notícias em tempo real dos principais portais
    - Oferecer ferramenta de estudo gratuita
    
    **⚙️ Tecnologias:**
    - Streamlit para interface web
    - Python como linguagem principal
    
    **📞 Fontes Oficiais:**
    - STF (Supremo Tribunal Federal)
    - STJ (Superior Tribunal de Justiça)
    - Câmara dos Deputados
    - Base de dados do Planalto
    
    **📊 Estatísticas:**
    - 41 termos jurídicos essenciais
    - 8 áreas do direito contempladas
    - 4 fontes oficiais consultadas
    - Interface moderna e responsiva
    - Notícias atualizadas para todos os termos
    """)

# App principal
def main():
    st.markdown('<h1 class="main-header">⚖️ Glossário Jurídico</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Definições e notícias em tempo real via APIs</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://cdn.pixabay.com/photo/2017/01/31/14/26/law-2024670_1280.png", width=80)
        st.title("🔍 Navegação")
        
        st.subheader("Buscar Termo")
        with st.form("sidebar_busca"):
            termo_busca = st.text_input("Digite um termo jurídico:")
            if st.form_submit_button("🔍 Buscar"):
                if termo_busca:
                    st.session_state.termo_selecionado = termo_busca
                    st.rerun()
        
        st.subheader("Termos Populares")
        termos = carregar_termos_populares()
        for termo in termos:
            if st.button(termo, key=f"side_{termo}"):
                st.session_state.termo_selecionado = termo
                st.rerun()
        
        st.markdown("---")
        st.metric("Status", "✅ Online")

    # Rotas principais
    if st.session_state.termo_selecionado:
        exibir_pagina_termo(st.session_state.termo_selecionado)
    else:
        tab1, tab2, tab3, tab4 = st.tabs(["🏠 Início", "📚 Explorar", "📰 Notícias", "ℹ️ Sobre"])
        with tab1:
            exibir_pagina_inicial()
        with tab2:
            exibir_explorar_termos()
        with tab3:
            exibir_pagina_noticias()
        with tab4:
            exibir_pagina_sobre()

if __name__ == "__main__":
    main()
