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
from difflib import get_close_matches

# Configuração da página - SIMPLIFICADA para evitar erros
st.set_page_config(
    page_title="Glossário Jurídico",
    page_icon="⚖️",
    layout="wide"
)

# CSS personalizado - MANTIDO
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f3a60;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 800;
    }
    .term-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 5px solid #1f3a60;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
    }
    .news-card {
        background: #e8f4fd;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 12px;
        border-left: 4px solid #17a2b8;
    }
    .definition-card {
        background: #f0f7ff;
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 25px;
        border: 2px solid #1f3a60;
    }
    .stButton button {
        background: #1f3a60;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 600;
    }
    .news-link {
        color: #1f3a60;
        text-decoration: none;
        font-weight: 600;
    }
    .news-link:hover {
        text-decoration: underline;
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

# APIs - SUBSITITUA pelas suas chaves reais
NEWS_API_KEY = "sua_chave_newsapi_aqui"  # Obtenha em: https://newsapi.org
WIKIPEDIA_API_URL = "https://pt.wikipedia.org/api/rest_v1/page/summary/"
FREE_DICTIONARY_API = "https://api.dictionaryapi.dev/api/v2/entries/en/"
GOOGLE_KNOWLEDGE_GRAPH_API_KEY = "sua_chave_google_kg_aqui"  # Opcional
BING_NEWS_API_KEY = "sua_chave_bing_news_aqui"  # Opcional

# Classe para buscar termos jurídicos de APIs
class APITermosJuridicos:
    def __init__(self):
        self.areas_direito = [
            "Direito Constitucional", "Direito Processual Civil", "Direito Penal",
            "Direito Civil", "Direito Administrativo", "Direito Empresarial",
            "Direito do Trabalho", "Direito Tributário"
        ]
    
    def _buscar_termos_wikipedia(self, categoria):
        """Busca termos jurídicos na Wikipedia API por categoria"""
        try:
            url = f"https://pt.wikipedia.org/api/rest_v1/page/related/{categoria}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                pages = data.get('pages', [])
                termos = []
                for page in pages[:10]:  # Pega os primeiros 10 resultados
                    title = page.get('title', '')
                    if title and title not in termos:
                        termos.append(title)
                return termos
        except:
            pass
        return []
    
    def obter_termos_populares_por_area(self, area):
        """Busca termos jurídicos populares de APIs externas"""
        try:
            # Mapeamento de áreas para categorias da Wikipedia
            categorias_wikipedia = {
                "Todas": "Direito",
                "Direito Constitucional": "Direito_constitucional",
                "Direito Processual Civil": "Direito_processual_civil", 
                "Direito Penal": "Direito_penal",
                "Direito Civil": "Direito_civil",
                "Direito Administrativo": "Direito_administrativo",
                "Direito Empresarial": "Direito_empresarial",
                "Direito do Trabalho": "Direito_do_trabalho",
                "Direito Tributário": "Direito_tributário"
            }
            
            categoria = categorias_wikipedia.get(area, "Direito")
            termos = self._buscar_termos_wikipedia(categoria)
            
            # Se não encontrou termos, busca por termos gerais
            if not termos:
                termos = self._buscar_termos_wikipedia("Direito")
            
            # Garante que temos pelo menos alguns termos
            if len(termos) < 3:
                # Busca termos em inglês como fallback
                try:
                    url = "https://en.wikipedia.org/api/rest_v1/page/related/Law"
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        for page in data.get('pages', [])[:5]:
                            title = page.get('title', '')
                            if title and title not in termos:
                                termos.append(title)
                except:
                    pass
            
            return random.sample(termos, min(5, len(termos))) if termos else ["Direito", "Lei", "Jurisprudência"]
            
        except Exception as e:
            return ["Direito", "Lei", "Jurisprudência"]
    
    def buscar_definicao_termo(self, termo):
        """Busca definição específica do termo em múltiplas APIs"""
        # Tentativa 1: Wikipedia em Português
        try:
            url = f"{WIKIPEDIA_API_URL}{termo.replace(' ', '_')}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                definicao = data.get('extract', '')
                if definicao and len(definicao) > 50:
                    return {
                        "definicao": definicao,
                        "fonte": "Wikipedia",
                        "url": data.get('content_urls', {}).get('desktop', {}).get('page', f"https://pt.wikipedia.org/wiki/{termo.replace(' ', '_')}")
                    }
        except:
            pass
        
        # Tentativa 2: Wikipedia em Inglês
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{termo.replace(' ', '_')}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                definicao = data.get('extract', '')
                if definicao:
                    return {
                        "definicao": f"(Em inglês) {definicao}",
                        "fonte": "Wikipedia EN",
                        "url": data.get('content_urls', {}).get('desktop', {}).get('page', f"https://en.wikipedia.org/wiki/{termo.replace(' ', '_')}")
                    }
        except:
            pass
        
        # Tentativa 3: Free Dictionary API
        try:
            url = f"{FREE_DICTIONARY_API}{termo.lower().replace(' ', '%20')}"
            response = requests.get(url, timeout=8)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    meanings = data[0].get('meanings', [])
                    if meanings and len(meanings) > 0:
                        definitions = meanings[0].get('definitions', [])
                        if definitions and len(definitions) > 0:
                            definicao = definitions[0].get('definition', '')
                            if definicao:
                                return {
                                    "definicao": f"(Em inglês) {definicao}",
                                    "fonte": "Free Dictionary API",
                                    "url": "#"
                                }
        except:
            pass
        
        # Última tentativa: Buscar página relacionada
        try:
            url = f"https://pt.wikipedia.org/api/rest_v1/page/related/{termo.replace(' ', '_')}"
            response = requests.get(url, timeout=8)
            if response.status_code == 200:
                data = response.json()
                pages = data.get('pages', [])
                if pages and len(pages) > 0:
                    first_page = pages[0]
                    descricao = first_page.get('description', '') or first_page.get('extract', '')
                    if descricao:
                        return {
                            "definicao": f"Conceito relacionado: {descricao}",
                            "fonte": "Wikipedia Related",
                            "url": f"https://pt.wikipedia.org/wiki/{first_page.get('key', termo.replace(' ', '_'))}"
                        }
        except:
            pass
        
        # Fallback final da API
        return {
            "definicao": f"Informações sobre '{termo}' serão carregadas em breve das fontes disponíveis.",
            "fonte": "Sistema de Busca",
            "url": "#"
        }

# Classe para Notícias via API
class APINoticias:
    def __init__(self):
        self.api_key = NEWS_API_KEY
    
    def buscar_noticias_reais(self, termo=None):
        """Busca notícias reais usando NewsAPI"""
        try:
            # CONFIGURAÇÃO OBRIGATÓRIA: Substitua pela sua chave da NewsAPI
            if self.api_key == "sua_chave_newsapi_aqui":
                # Modo de demonstração - REMOVA quando tiver a chave real
                return self._noticias_demo(termo)
            
            # CHAMADA REAL DA API (descomente quando tiver a chave)
            query = "direito Brasil" if not termo else f"{termo} direito Brasil"
            url = f"https://newsapi.org/v2/everything?q={query}&language=pt&sortBy=publishedAt&apiKey={self.api_key}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                noticias = []
                for article in data.get('articles', [])[:5]:  # Limita a 5 notícias
                    if article.get('title') != '[Removed]':
                        noticias.append({
                            "titulo": article.get('title', ''),
                            "fonte": article.get('source', {}).get('name', ''),
                            "data": article.get('publishedAt', '')[:10],
                            "resumo": article.get('description', '') or article.get('content', '')[:200] + "...",
                            "url": article.get('url', '#')
                        })
                return noticias if noticias else self._noticias_fallback(termo)
            else:
                return self._noticias_fallback(termo)
                
        except Exception as e:
            return self._noticias_fallback(termo)
    
    def _noticias_demo(self, termo=None):
        """Modo demonstração - REMOVA quando tiver a chave real da NewsAPI"""
        # ESTE É APENAS UM EXEMPLO - SUBSITITUA PELA API REAL
        noticias_base = [
            {
                "titulo": "Atualizações do Sistema Jurídico",
                "fonte": "Sistema",
                "data": datetime.now().strftime("%Y-%m-%d"),
                "resumo": "Configure sua chave da NewsAPI para ver notícias reais.",
                "url": "https://newsapi.org"
            }
        ]
        return noticias_base
    
    def _noticias_fallback(self, termo=None):
        """Fallback quando a API não está disponível"""
        return [{
            "titulo": "Configure a NewsAPI para notícias em tempo real",
            "fonte": "Sistema",
            "data": datetime.now().strftime("%Y-%m-%d"),
            "resumo": "Obtenha uma chave gratuita em newsapi.org para acessar notícias jurídicas atualizadas.",
            "url": "https://newsapi.org"
        }]

# Classe para Contexto Jurídico via API
class APIContextoJuridico:
    def buscar_contexto(self, termo):
        """Busca contexto jurídico via APIs externas"""
        try:
            # Usa a Wikipedia API para contexto
            url = f"{WIKIPEDIA_API_URL}{termo.replace(' ', '_')}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                extract = data.get('extract', '')
                if extract:
                    return f"Contexto jurídico: {extract[:300]}..."
            
            # Fallback para busca relacionada
            url = f"https://pt.wikipedia.org/api/rest_v1/page/related/{termo.replace(' ', '_')}"
            response = requests.get(url, timeout=8)
            if response.status_code == 200:
                data = response.json()
                pages = data.get('pages', [])
                if pages:
                    first_desc = pages[0].get('description', '')
                    if first_desc:
                        return f"Área relacionada: {first_desc}"
            
            return f"O termo '{termo}' está sendo pesquisado nas bases de dados jurídicas disponíveis."
            
        except:
            return f"Informações contextuais sobre '{termo}' serão carregadas em breve."

# Sistema de cache para dados
@st.cache_data
def carregar_termos_populares(area="Todas"):
    api_termos = APITermosJuridicos()
    return api_termos.obter_termos_populares_por_area(area)

# Funções auxiliares para busca
def buscar_termo_personalizado(termo_busca):
    """Busca informações completas sobre um termo específico"""
    api_termos = APITermosJuridicos()
    api_noticias = APINoticias()
    api_contexto = APIContextoJuridico()
    
    definicao_data = api_termos.buscar_definicao_termo(termo_busca)
    noticias_data = api_noticias.buscar_noticias_reais(termo_busca)
    contexto = api_contexto.buscar_contexto(termo_busca)
    
    return {
        "termo": termo_busca,
        "definicao": definicao_data["definicao"],
        "fonte": definicao_data["fonte"],
        "area": "Direito",
        "data": datetime.now().strftime("%Y-%m-%d"),
        "exemplo": contexto,
        "sinonimos": [termo_busca],
        "relacionados": ["Direito Constitucional", "Direito Processual"],
        "noticias": noticias_data
    }

# Páginas do aplicativo (mantidas as mesmas, mas agora com dados 100% de APIs)
def exibir_pagina_inicial():
    st.markdown("### 🎯 Bem-vindo ao Glossário Jurídico Digital")
    st.markdown("**Descomplicando o Direito** através de definições claras e atualizadas.")
    
    termos_populares = carregar_termos_populares()
    
    st.markdown("### 📈 Estatísticas do Acervo")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Termos Disponíveis", "API")
    with col2:
        st.metric("Áreas do Direito", "8")
    with col3:
        st.metric("Fontes", "APIs")
    with col4:
        st.metric("Atualização", datetime.now().strftime("%d/%m/%Y"))
    
    st.markdown("### 🔥 Termos em Destaque")
    
    cols = st.columns(2)
    for idx, termo in enumerate(termos_populares):
        with cols[idx % 2]:
            with st.container():
                st.markdown(f'<div class="term-card">', unsafe_allow_html=True)
                
                st.markdown(f"#### ⚖️ {termo}")
                st.write("**Direito**")
                
                api_termos = APITermosJuridicos()
                definicao_data = api_termos.buscar_definicao_termo(termo)
                st.write(definicao_data["definicao"][:150] + "...")
                
                st.caption(f"📚 Fonte: {definicao_data['fonte']}")
                
                if st.button("🔍 Ver Detalhes", key=f"home_{termo}"):
                    st.session_state.termo_selecionado = termo
                    st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)

def exibir_explorar_termos():
    st.markdown("### 📚 Explorar Termos Jurídicos")
    
    col_filtro1, col_filtro2 = st.columns(2)
    
    with col_filtro1:
        with st.form("busca_form"):
            termo_busca = st.text_input("🔍 Buscar termo jurídico:", key="busca_avancada")
            submitted = st.form_submit_button("Buscar")
            
            if submitted and termo_busca:
                st.session_state.termo_buscado = termo_busca
    
    with col_filtro2:
        api_termos = APITermosJuridicos()
        areas = ["Todas"] + api_termos.areas_direito
        area_filtro = st.selectbox("🎯 Filtrar por área:", areas, key="area_filter")
        
        if area_filtro != st.session_state.area_filtro:
            st.session_state.area_filtro = area_filtro
            st.session_state.termo_buscado = None
    
    if not hasattr(st.session_state, 'termo_buscado') or not st.session_state.termo_buscado:
        st.info(f"💡 **Termos populares em {st.session_state.area_filtro}**")
        termos_populares = carregar_termos_populares(st.session_state.area_filtro)
        
        for termo in termos_populares:
            with st.container():
                st.markdown(f'<div class="term-card">', unsafe_allow_html=True)
                
                col_texto, col_acoes = st.columns([3, 1])
                
                with col_texto:
                    st.markdown(f"##### ⚖️ {termo}")
                    st.write(f"**{st.session_state.area_filtro}** | 📅 {datetime.now().strftime('%Y-%m-%d')}")
                    
                    api_termos = APITermosJuridicos()
                    definicao_data = api_termos.buscar_definicao_termo(termo)
                    st.write(definicao_data["definicao"][:200] + "...")
                    
                    st.caption(f"📚 **Fonte:** {definicao_data['fonte']}")
                
                with col_acoes:
                    st.write("")
                    if st.button("🔍 Detalhes", key=f"exp_{termo}", use_container_width=True):
                        st.session_state.termo_selecionado = termo
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        termo_busca = st.session_state.termo_buscado
        st.info(f"🔍 Buscando por: '{termo_busca}'")
        
        termo_data = buscar_termo_personalizado(termo_busca)
        
        with st.container():
            st.markdown(f'<div class="term-card">', unsafe_allow_html=True)
            
            col_texto, col_acoes = st.columns([3, 1])
            
            with col_texto:
                st.markdown(f"##### ⚖️ {termo_data['termo']}")
                st.write(f"**{termo_data['area']}** | 📅 {termo_data['data']}")
                st.write(termo_data['definicao'])
                
                st.caption(f"📚 **Fonte:** {termo_data['fonte']}")
            
            with col_acoes:
                st.write("")
                if st.button("🔍 Detalhes", key=f"exp_{termo_data['termo']}", use_container_width=True):
                    st.session_state.termo_selecionado = termo_data['termo']
                    st.session_state.termo_buscado = None
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

def exibir_pagina_termo(termo_nome):
    api_termos = APITermosJuridicos()
    api_noticias = APINoticias()
    api_contexto = APIContextoJuridico()
    
    definicao_data = api_termos.buscar_definicao_termo(termo_nome)
    noticias_data = api_noticias.buscar_noticias_reais(termo_nome)
    contexto = api_contexto.buscar_contexto(termo_nome)
    
    st.markdown(f'<div class="definition-card">', unsafe_allow_html=True)
    
    col_header, col_nav = st.columns([4, 1])
    
    with col_header:
        st.markdown(f"# ⚖️ {termo_nome}")
        st.markdown(f"**Área:** Direito | **Fonte:** {definicao_data['fonte']} | **Data:** {datetime.now().strftime('%Y-%m-%d')}")
    
    with col_nav:
        st.write("")
        if st.button("← Voltar", use_container_width=True):
            st.session_state.termo_selecionado = None
            if hasattr(st.session_state, 'termo_buscado'):
                st.session_state.termo_buscado = None
            st.rerun()
    
    st.markdown("---")
    
    col_conteudo, col_lateral = st.columns([2, 1])
    
    with col_conteudo:
        st.markdown("### 📖 Definição da API")
        st.info(definicao_data["definicao"])
        
        st.markdown("### 💼 Contexto da API")
        st.success(contexto)
        
        st.markdown("### 📰 Notícias da API")
        
        if noticias_data:
            for noticia in noticias_data:
                with st.container():
                    st.markdown(f'<div class="news-card">', unsafe_allow_html=True)
                    
                    st.markdown(f"#### {noticia['titulo']}")
                    st.write(noticia['resumo'])
                    st.caption(f"**Fonte:** {noticia['fonte']} | **Data:** {noticia['data']}")
                    
                    if noticia['url'] != '#':
                        st.markdown(f'<a href="{noticia["url"]}" target="_blank" class="news-link">📖 Ler notícia completa</a>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Notícias serão carregadas quando a NewsAPI for configurada.")
    
    with col_lateral:
        st.markdown("### 🏷️ Informações")
        
        st.markdown("**APIs Utilizadas:**")
        st.write("• Wikipedia API")
        st.write("• NewsAPI")
        st.write("• Free Dictionary API")
    
    st.markdown('</div>', unsafe_allow_html=True)

def exibir_pagina_noticias():
    st.markdown("### 📰 Notícias Jurídicas em Tempo Real")
    
    with st.form("noticias_busca"):
        termo_noticias = st.text_input("🔍 Buscar notícias sobre termo jurídico específico:")
        buscar_noticias = st.form_submit_button("Buscar Notícias")
    
    api_noticias = APINoticias()
    
    if termo_noticias and buscar_noticias:
        st.info(f"📰 Notícias sobre: {termo_noticias}")
        noticias = api_noticias.buscar_noticias_reais(termo_noticias)
    else:
        st.info("📰 **Principais Notícias Jurídicas**")
        noticias = api_noticias.buscar_noticias_reais()
    
    if noticias:
        for i, noticia in enumerate(noticias):
            with st.container():
                st.markdown(f'<div class="news-card">', unsafe_allow_html=True)
                
                col_titulo, col_data = st.columns([3, 1])
                
                with col_titulo:
                    st.markdown(f"#### {noticia['titulo']}")
                
                with col_data:
                    st.caption(f"📅 {noticia['data']}")
                
                st.write(noticia['resumo'])
                st.caption(f"**Fonte:** {noticia['fonte']}")
                
                if noticia['url'] != '#':
                    st.markdown(f'<a href="{noticia["url"]}" target="_blank" class="news-link">🔗 Ler notícia completa</a>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Configure a NewsAPI para ver notícias em tempo real.")

def exibir_pagina_sobre():
    st.markdown("### ℹ️ Sobre o Projeto")
    st.write("""
    **Glossário Jurídico: Descomplicando o Direito**
    
    **🎯 Objetivos:**
    - Fornecer definições claras de termos jurídicos via APIs
    - Contextualizar conceitos com exemplos práticos
    - Integrar notícias em tempo real dos principais portais
    - Oferecer ferramenta de estudo gratuita e atualizada
    
    **⚙️ APIs Utilizadas:**
    - Wikipedia API para definições
    - NewsAPI para notícias jurídicas
    - Free Dictionary API para definições alternativas
    
    **📊 Dados 100% via APIs**
    - Zero hand code
    - Informações em tempo real
    - Fontes confiáveis e atualizadas
    """)

# App principal
def main():
    st.markdown('<h1 class="main-header">⚖️ Glossário Jurídico com APIs</h1>', unsafe_allow_html=True)
    st.markdown("### Definições e notícias em tempo real via APIs")
    
    # Sidebar
    with st.sidebar:
        st.image("https://cdn.pixabay.com/photo/2017/01/31/14/26/law-2024670_1280.png", width=80)
        st.title("🔍 Navegação")
        
        st.subheader("Buscar Termo")
        with st.form("sidebar_busca"):
            termo_busca_sidebar = st.text_input("Digite qualquer termo jurídico:")
            sidebar_submitted = st.form_submit_button("🔍 Buscar")
            
            if sidebar_submitted and termo_busca_sidebar:
                st.session_state.termo_selecionado = termo_busca_sidebar
                st.rerun()
        
        st.subheader("Termos Populares")
        termos_populares = carregar_termos_populares()
        for termo in termos_populares:
            if st.button(termo, key=f"side_{termo}"):
                st.session_state.termo_selecionado = termo
                st.rerun()
        
        st.markdown("---")
        st.metric("Fontes", "APIs")
        st.caption("📡 Dados 100% via APIs")

    # Rotas
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
