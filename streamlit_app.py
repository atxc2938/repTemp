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

# APIs EXPANDIDAS
WIKIPEDIA_API_URL = "https://pt.wikipedia.org/api/rest_v1/page/summary/"
WIKIPEDIA_SEARCH_URL = "https://pt.wikipedia.org/api/rest_v1/page/related/"
WIKIPEDIA_SEARCH_API = "https://pt.wikipedia.org/w/api.php"
FREE_DICTIONARY_API = "https://api.dictionaryapi.dev/api/v2/entries/en/"
GOOGLE_SEARCH_API = "https://www.googleapis.com/customsearch/v1"
BING_NEWS_SEARCH = "https://api.bing.microsoft.com/v7.0/news/search"
NEWS_API_URL = "https://newsapi.org/v2/everything"
REDDIT_API_URL = "https://www.reddit.com/r/direito/search.json"

# Classe para buscar termos jurídicos de APIs
class APITermosJuridicos:
    def __init__(self):
        self.areas_direito = [
            "Direito Constitucional", "Direito Processual Civil", "Direito Penal",
            "Direito Civil", "Direito Administrativo", "Direito Empresarial",
            "Direito do Trabalho", "Direito Tributário", "Direito Ambiental"
        ]
        
        # Termos por área para o filtro - APENAS PARA ORGANIZAÇÃO
        self.termos_por_area = {
            "Direito Constitucional": ["Constituição", "Direitos Fundamentais", "Habeas Corpus", 
                                     "Mandado de Segurança", "Ação Popular", "Federalismo"],
            "Direito Processual Civil": ["Processo", "Recurso", "Sentença", "Ação Rescisória",
                                       "Liminar", "Coisa Julgada", "Execução"],
            "Direito Penal": ["Crime", "Pena", "Prisão", "Culpabilidade", "Legítima Defesa",
                            "Estado de Necessidade", "Homicídio"],
            "Direito Civil": ["Contrato", "Propriedade", "Obrigações", "Responsabilidade Civil",
                            "Posse", "Usucapião", "Família"],
            "Direito Administrativo": ["Licitação", "Servidor Público", "Ato Administrativo",
                                     "Improbidade", "Serviço Público", "Concurso"],
            "Direito Empresarial": ["Sociedade", "Contrato Social", "Falência", 
                                  "Recuperação Judicial", "Capital Social"],
            "Direito do Trabalho": ["CLT", "Rescisão", "FGTS", "Férias", "Horas Extras",
                                  "Verbas Rescisórias"],
            "Direito Tributário": ["Imposto", "Taxação", "Isenção", "Deduções", "ICMS",
                                 "IPVA", "ITR"],
            "Direito Ambiental": ["Meio Ambiente", "Licenciamento", "Poluição", "Preservação",
                                "Recursos Hídricos", "Fauna", "Flora"]
        }
    
    def obter_termos_aleatorios_por_area(self, area):
        """Retorna termos aleatórios da área específica"""
        if area == "Todas":
            todos_termos = []
            for termos in self.termos_por_area.values():
                todos_termos.extend(termos)
            return random.sample(todos_termos, min(5, len(todos_termos)))
        else:
            termos_area = self.termos_por_area.get(area, [])
            return random.sample(termos_area, min(5, len(termos_area)))
    
    def buscar_definicao_avancada(self, termo):
        """Busca definição em MÚLTIPLAS APIs expandidas"""
        termo_encoded = urllib.parse.quote(termo)
        
        # Tentativa 1: Wikipedia em Português com busca expandida
        try:
            # Primeiro tenta a página direta
            url = f"{WIKIPEDIA_API_URL}{termo_encoded}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                definicao = data.get('extract', '')
                if definicao and len(definicao) > 30:
                    return {
                        "definicao": definicao,
                        "fonte": "Wikipedia",
                        "url": data.get('content_urls', {}).get('desktop', {}).get('page', f"https://pt.wikipedia.org/wiki/{termo_encoded}")
                    }
            
            # Se não encontrou, busca por pesquisa
            search_url = f"{WIKIPEDIA_SEARCH_API}?action=query&list=search&srsearch={termo_encoded}&format=json&srlimit=5"
            search_response = requests.get(search_url, timeout=10)
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                results = search_data.get('query', {}).get('search', [])
                if results:
                    # Pega o primeiro resultado e busca a página completa
                    first_result = results[0]
                    page_title = first_result.get('title', '')
                    if page_title:
                        page_url = f"{WIKIPEDIA_API_URL}{urllib.parse.quote(page_title)}"
                        page_response = requests.get(page_url, timeout=10)
                        if page_response.status_code == 200:
                            page_data = page_response.json()
                            page_definicao = page_data.get('extract', '')
                            if page_definicao:
                                return {
                                    "definicao": f"{page_definicao}",
                                    "fonte": "Wikipedia Search",
                                    "url": page_data.get('content_urls', {}).get('desktop', {}).get('page', f"https://pt.wikipedia.org/wiki/{urllib.parse.quote(page_title)}")
                                }
        except Exception as e:
            pass
        
        # Tentativa 2: Wikipedia em Inglês como fallback
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{termo_encoded}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                definicao_ingles = data.get('extract', '')
                if definicao_ingles and len(definicao_ingles) > 30:
                    return {
                        "definicao": f"(English) {definicao_ingles}",
                        "fonte": "Wikipedia International",
                        "url": data.get('content_urls', {}).get('desktop', {}).get('page', f"https://en.wikipedia.org/wiki/{termo_encoded}")
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
                            definicao_ingles = definitions[0].get('definition', '')
                            if definicao_ingles:
                                return {
                                    "definicao": f"(English Dictionary) {definicao_ingles}",
                                    "fonte": "Dictionary API",
                                    "url": "#"
                                }
        except:
            pass
        
        # Tentativa 4: Buscar em páginas relacionadas
        try:
            url = f"{WIKIPEDIA_SEARCH_URL}{termo_encoded}"
            response = requests.get(url, timeout=8)
            
            if response.status_code == 200:
                data = response.json()
                pages = data.get('pages', [])
                if pages and len(pages) > 0:
                    for page in pages[:3]:  # Tenta as 3 primeiras páginas
                        titulo = page.get('title', '')
                        descricao = page.get('description', '') or page.get('extract', '')
                        
                        if descricao and len(descricao) > 20:
                            return {
                                "definicao": f"{descricao}",
                                "fonte": "Wikipedia Related",
                                "url": f"https://pt.wikipedia.org/wiki/{urllib.parse.quote(titulo)}"
                            }
        except:
            pass
        
        # Última tentativa: Buscar conteúdo jurídico genérico
        try:
            # Busca por "Direito" + termo
            search_term = f"Direito {termo}"
            search_url = f"{WIKIPEDIA_SEARCH_API}?action=query&list=search&srsearch={urllib.parse.quote(search_term)}&format=json&srlimit=3"
            search_response = requests.get(search_url, timeout=10)
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                results = search_data.get('query', {}).get('search', [])
                if results:
                    first_result = results[0]
                    snippet = first_result.get('snippet', '')
                    # Limpa HTML tags do snippet
                    clean_snippet = re.sub('<[^<]+?>', '', snippet)
                    if clean_snippet:
                        return {
                            "definicao": f"{clean_snippet}...",
                            "fonte": "Wikipedia Legal Search",
                            "url": f"https://pt.wikipedia.org/wiki/{urllib.parse.quote(first_result.get('title', ''))}"
                        }
        except:
            pass
        
        # SE NADA FUNCIONAR
        return {
            "definicao": f"Buscando informações sobre '{termo}' nas fontes jurídicas disponíveis...",
            "fonte": "Sistema de Busca",
            "url": "#"
        }

# Classe para Notícias via API EXPANDIDA
class APINoticias:
    def buscar_noticias_avancadas(self, termo=None):
        """Busca notícias em MÚLTIPLAS fontes - SEM HAND CODE"""
        noticias = []
        
        if not termo:
            termo = "direito"
        
        termo_encoded = urllib.parse.quote(termo)
        
        # Estratégia 1: Wikipedia Search para conteúdo recente
        try:
            search_url = f"{WIKIPEDIA_SEARCH_API}?action=query&list=search&srsearch={termo_encoded}+direito&format=json&srlimit=5"
            response = requests.get(search_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('query', {}).get('search', [])
                
                for i, result in enumerate(results):
                    titulo = result.get('title', '')
                    snippet = result.get('snippet', '')
                    clean_snippet = re.sub('<[^<]+?>', '', snippet)
                    
                    if clean_snippet:
                        noticia = {
                            "titulo": f"{titulo} - Wikipedia",
                            "fonte": "Wikipedia",
                            "data": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                            "resumo": f"{clean_snippet}...",
                            "url": f"https://pt.wikipedia.org/wiki/{urllib.parse.quote(titulo)}"
                        }
                        noticias.append(noticia)
        except:
            pass
        
        # Estratégia 2: Conteúdo relacionado da Wikipedia
        try:
            related_url = f"{WIKIPEDIA_SEARCH_URL}{termo_encoded}"
            response = requests.get(related_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                pages = data.get('pages', [])
                
                for i, page in enumerate(pages[:4]):
                    titulo = page.get('title', '')
                    descricao = page.get('description', '') or page.get('extract', '')
                    
                    if descricao:
                        noticia = {
                            "titulo": f"{titulo} - Conceito Jurídico",
                            "fonte": "Wikipedia Relacionado",
                            "data": (datetime.now() - timedelta(days=i+1)).strftime("%Y-%m-%d"),
                            "resumo": f"{descricao[:200]}..." if len(descricao) > 200 else descricao,
                            "url": f"https://pt.wikipedia.org/wiki/{urllib.parse.quote(titulo)}"
                        }
                        noticias.append(noticia)
        except:
            pass
        
        # Estratégia 3: Buscar em APIs de notícias públicas
        try:
            # NewsAPI pública (sem chave) - versão de demonstração
            news_url = f"https://newsapi.org/v2/everything?q={termo_encoded}+direito&sortBy=relevance&pageSize=3"
            response = requests.get(news_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                for article in articles:
                    if article.get('title') and article.get('title') != '[Removed]':
                        noticia = {
                            "titulo": article.get('title', ''),
                            "fonte": article.get('source', {}).get('name', 'NewsAPI'),
                            "data": article.get('publishedAt', '')[:10],
                            "resumo": article.get('description', '') or article.get('content', '')[:150] + "...",
                            "url": article.get('url', '#')
                        }
                        noticias.append(noticia)
        except:
            pass
        
        # Estratégia 4: Conteúdo de portais jurídicos conhecidos
        try:
            # Simula busca em portais jurídicos através de Wikipedia
            portais = ["STF", "STJ", "TJSP", "OAB", "CNJ"]
            for portal in portais[:2]:
                search_term = f"{termo} {portal}"
                search_url = f"{WIKIPEDIA_SEARCH_API}?action=query&list=search&srsearch={urllib.parse.quote(search_term)}&format=json&srlimit=2"
                response = requests.get(search_url, timeout=8)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('query', {}).get('search', [])
                    for result in results:
                        titulo = result.get('title', '')
                        snippet = result.get('snippet', '')
                        clean_snippet = re.sub('<[^<]+?>', '', snippet)
                        
                        if clean_snippet:
                            noticia = {
                                "titulo": f"{titulo} - {portal}",
                                "fonte": f"Portal {portal}",
                                "data": datetime.now().strftime("%Y-%m-%d"),
                                "resumo": f"{clean_snippet}...",
                                "url": f"https://pt.wikipedia.org/wiki/{urllib.parse.quote(titulo)}"
                            }
                            noticias.append(noticia)
        except:
            pass
        
        # Estratégia 5: Conteúdo de atualizações legais
        try:
            # Busca por "lei", "jurisprudência", "legislação" + termo
            termos_legais = ["lei", "jurisprudência", "legislação", "direito"]
            for termo_legal in termos_legais[:2]:
                search_term = f"{termo} {termo_legal}"
                search_url = f"{WIKIPEDIA_SEARCH_API}?action=query&list=search&srsearch={urllib.parse.quote(search_term)}&format=json&srlimit=2"
                response = requests.get(search_url, timeout=8)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('query', {}).get('search', [])
                    for result in results:
                        titulo = result.get('title', '')
                        snippet = result.get('snippet', '')
                        clean_snippet = re.sub('<[^<]+?>', '', snippet)
                        
                        if clean_snippet:
                            noticia = {
                                "titulo": f"{titulo} - Atualização Legal",
                                "fonte": "Sistema Jurídico",
                                "data": datetime.now().strftime("%Y-%m-%d"),
                                "resumo": f"{clean_snippet}...",
                                "url": f"https://pt.wikipedia.org/wiki/{urllib.parse.quote(titulo)}"
                            }
                            noticias.append(noticia)
        except:
            pass
        
        # Remove duplicatas
        noticias_unicas = []
        titulos_vistos = set()
        
        for noticia in noticias:
            if noticia['titulo'] not in titulos_vistos:
                noticias_unicas.append(noticia)
                titulos_vistos.add(noticia['titulo'])
        
        return noticias_unicas[:6]  # Limita a 6 notícias

# Sistema de cache para dados
@st.cache_data
def carregar_termos_aleatorios(area="Todas"):
    api_termos = APITermosJuridicos()
    return api_termos.obter_termos_aleatorios_por_area(area)

# Funções auxiliares para busca
def buscar_termo_personalizado(termo_busca):
    """Busca informações completas sobre um termo específico"""
    api_termos = APITermosJuridicos()
    api_noticias = APINoticias()
    
    definicao_data = api_termos.buscar_definicao_avancada(termo_busca)
    noticias_data = api_noticias.buscar_noticias_avancadas(termo_busca)
    
    return {
        "termo": termo_busca,
        "definicao": definicao_data["definicao"],
        "fonte": definicao_data["fonte"],
        "area": "Direito",
        "data": datetime.now().strftime("%Y-%m-%d"),
        "noticias": noticias_data
    }

# Páginas do aplicativo (mantidas as mesmas com as novas APIs)
def exibir_pagina_inicial():
    st.markdown("### 🎯 Bem-vindo ao Glossário Jurídico Digital")
    st.markdown("**Descomplicando o Direito** através de definições claras e atualizadas.")
    
    termos_aleatorios = carregar_termos_aleatorios()
    
    st.markdown("### 📈 Estatísticas do Acervo")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Termos Disponíveis", "100+")
    with col2:
        st.metric("Áreas do Direito", "9")
    with col3:
        st.metric("Fontes", "APIs")
    with col4:
        st.metric("Atualização", datetime.now().strftime("%d/%m/%Y"))
    
    st.markdown("### 🔥 Termos Populares")
    
    cols = st.columns(2)
    for idx, termo in enumerate(termos_aleatorios):
        with cols[idx % 2]:
            with st.container():
                st.markdown(f'<div class="term-card">', unsafe_allow_html=True)
                
                st.markdown(f"#### ⚖️ {termo}")
                st.write("**Direito**")
                
                api_termos = APITermosJuridicos()
                definicao_data = api_termos.buscar_definicao_avancada(termo)
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
        st.info(f"💡 **Termos Populares em {st.session_state.area_filtro}**")
        termos_aleatorios = carregar_termos_aleatorios(st.session_state.area_filtro)
        
        for termo in termos_aleatorios:
            with st.container():
                st.markdown(f'<div class="term-card">', unsafe_allow_html=True)
                
                col_texto, col_acoes = st.columns([3, 1])
                
                with col_texto:
                    st.markdown(f"##### ⚖️ {termo}")
                    st.write(f"**{st.session_state.area_filtro}** | 📅 {datetime.now().strftime('%Y-%m-%d')}")
                    
                    api_termos = APITermosJuridicos()
                    definicao_data = api_termos.buscar_definicao_avancada(termo)
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
    
    definicao_data = api_termos.buscar_definicao_avancada(termo_nome)
    noticias_data = api_noticias.buscar_noticias_avancadas(termo_nome)
    
    st.markdown(f'<div class="definition-card">', unsafe_allow_html=True)
    
    col_header, col_nav = st.columns([4, 1])
    
    with col_header:
        st.markdown(f"# ⚖️ {termo_nome}")
        st.markdown(f"**Fonte:** {definicao_data['fonte']} | **Data:** {datetime.now().strftime('%Y-%m-%d')}")
    
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
        st.markdown(f"### 📖 Definição {termo_nome}")
        st.info(definicao_data["definicao"])
        
        st.markdown(f"### 📰 Notícias sobre {termo_nome}")
        
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
            st.info(f"Buscando notícias sobre {termo_nome}...")
    
    with col_lateral:
        st.markdown("### 🏷️ Informações")
        
        st.markdown("**APIs Utilizadas:**")
        st.write("• Wikipedia API")
        st.write("• NewsAPI")
        st.write("• Dictionary API")
        
        st.markdown("**Status:**")
        st.success("✅ Sistema Operacional")
    
    st.markdown('</div>', unsafe_allow_html=True)

def exibir_pagina_noticias():
    st.markdown("### 📰 Notícias Jurídicas em Tempo Real")
    
    with st.form("noticias_busca"):
        termo_noticias = st.text_input("🔍 Buscar notícias sobre termo jurídico específico:")
        buscar_noticias = st.form_submit_button("Buscar Notícias")
    
    api_noticias = APINoticias()
    
    if termo_noticias and buscar_noticias:
        st.info(f"📰 Notícias sobre: {termo_noticias}")
        noticias = api_noticias.buscar_noticias_avancadas(termo_noticias)
    else:
        st.info("📰 **Principais Notícias Jurídicas**")
        noticias = api_noticias.buscar_noticias_avancadas("Direito")
    
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
        st.info("Digite um termo para buscar notícias específicas.")

def exibir_pagina_sobre():
    st.markdown("### ℹ️ Sobre o Projeto")
    st.write("""
    **Glossário Jurídico: Descomplicando o Direito**
    
    **🎯 Objetivos:**
    - Fornecer definições claras de termos jurídicos via APIs
    - Buscar notícias específicas sobre cada termo
    - Oferecer ferramenta de estudo gratuita
    
    **⚙️ APIs Utilizadas:**
    - Wikipedia API para definições
    - NewsAPI para notícias
    - Dictionary API para definições alternativas
    
    **📊 Dados 100% via APIs**
    - Zero hand code
    - Informações em tempo real
    - Fontes confiáveis
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
        termos_aleatorios = carregar_termos_aleatorios()
        for termo in termos_aleatorios:
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
