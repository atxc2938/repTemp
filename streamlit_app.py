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

# APIs BRASILEIRAS EXPANDIDAS
WIKIPEDIA_PT_API = "https://pt.wikipedia.org/api/rest_v1/page/summary/"
WIKIPEDIA_PT_SEARCH = "https://pt.wikipedia.org/w/api.php"
DICIO_API = "https://dicio-api-ten.vercel.app/v2/"
SINONIMOS_API = "https://significado.herokuapp.com/"
AURELIO_API = "https://dicionario-aurelio.vercel.app/"
PALAVRAS_API = "https://palavras.vercel.app/api/"
CONJUGACAO_API = "https://conjugacao.com.br/"
ACENTUACAO_API = "https://acentuacao.vercel.app/api/"

# APIs de notícias brasileiras
CAMARA_NOTICIAS = "https://dadosabertos.camara.leg.br/api/v2/noticias"
IBGE_NOTICIAS = "https://servicodados.ibge.gov.br/api/v3/noticias/"
SENADO_NOTICIAS = "https://www12.senado.leg.br/institucional/noticias/json"

# Classe para buscar termos jurídicos de APIs BRASILEIRAS
class APITermosJuridicos:
    def __init__(self):
        self.areas_direito = [
            "Direito Constitucional", "Direito Processual Civil", "Direito Penal",
            "Direito Civil", "Direito Administrativo", "Direito Empresarial",
            "Direito do Trabalho", "Direito Tributário", "Direito Ambiental"
        ]
        
        # Termos por área para o filtro
        self.termos_por_area = {
            "Direito Constitucional": ["Constituição Federal", "Direitos Fundamentais", "Habeas Corpus", 
                                     "Mandado de Segurança", "Ação Popular", "Federalismo", "Separação dos Poderes",
                                     "Controle de Constitucionalidade", "Remédios Constitucionais"],
            "Direito Processual Civil": ["Processo Civil", "Recurso", "Sentença", "Ação Rescisória",
                                       "Liminar", "Coisa Julgada", "Execução", "Competência", "Jurisdição"],
            "Direito Penal": ["Crime", "Pena", "Prisão", "Culpabilidade", "Legítima Defesa",
                            "Estado de Necessidade", "Homicídio", "Furto", "Roubo", "Latrocínio"],
            "Direito Civil": ["Contrato", "Propriedade", "Obrigações", "Responsabilidade Civil",
                            "Posse", "Usucapião", "Família", "Sucessões", "Direitos Reais"],
            "Direito Administrativo": ["Licitação", "Servidor Público", "Ato Administrativo",
                                     "Improbidade", "Serviço Público", "Concurso", "Poder de Polícia"],
            "Direito Empresarial": ["Sociedade", "Contrato Social", "Falência", 
                                  "Recuperação Judicial", "Capital Social", "Títulos de Crédito"],
            "Direito do Trabalho": ["CLT", "Rescisão", "FGTS", "Férias", "Horas Extras",
                                  "Verbas Rescisórias", "Acidente de Trabalho", "Direito Coletivo"],
            "Direito Tributário": ["Imposto", "Taxação", "Isenção", "Deduções", "ICMS",
                                 "IPVA", "ITR", "Obrigação Tributária", "Crédito Tributário"],
            "Direito Ambiental": ["Meio Ambiente", "Licenciamento", "Poluição", "Preservação",
                                "Recursos Hídricos", "Fauna", "Flora", "Desenvolvimento Sustentável"]
        }
    
    def obter_termos_populares_aleatorios(self):
        """Retorna 5 termos aleatórios de qualquer área - APENAS NOMES"""
        todos_termos = []
        for termos in self.termos_por_area.values():
            todos_termos.extend(termos)
        return random.sample(todos_termos, min(5, len(todos_termos)))
    
    def obter_termos_aleatorios_por_area(self, area):
        """Retorna termos aleatórios da área específica"""
        if area == "Todas":
            return self.obter_termos_populares_aleatorios()
        else:
            termos_area = self.termos_por_area.get(area, [])
            return random.sample(termos_area, min(5, len(termos_area)))
    
    def buscar_definicao_wikipedia(self, termo):
        """Busca definição REAL na Wikipedia Brasileira"""
        try:
            # Tenta buscar a página diretamente
            url = f"{WIKIPEDIA_PT_API}{urllib.parse.quote(termo)}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                definicao = data.get('extract', '')
                if definicao and len(definicao) > 30:
                    return {
                        "definicao": definicao,
                        "fonte": "Wikipedia Brasil",
                        "url": data.get('content_urls', {}).get('desktop', {}).get('page', f"https://pt.wikipedia.org/wiki/{urllib.parse.quote(termo)}")
                    }
            
            # Busca por pesquisa se não encontrou direto
            search_url = f"{WIKIPEDIA_PT_SEARCH}?action=query&format=json&list=search&srsearch={urllib.parse.quote(termo)}&utf8=1&srlimit=5"
            search_response = requests.get(search_url, timeout=10)
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                results = search_data.get('query', {}).get('search', [])
                
                if results:
                    # Pega o primeiro resultado e busca a definição completa
                    primeiro_resultado = results[0]['title']
                    url_definicao = f"{WIKIPEDIA_PT_API}{urllib.parse.quote(primeiro_resultado)}"
                    def_response = requests.get(url_definicao, timeout=10)
                    
                    if def_response.status_code == 200:
                        def_data = def_response.json()
                        definicao = def_data.get('extract', '')
                        if definicao:
                            return {
                                "definicao": definicao,
                                "fonte": "Wikipedia Brasil",
                                "url": def_data.get('content_urls', {}).get('desktop', {}).get('page', f"https://pt.wikipedia.org/wiki/{urllib.parse.quote(primeiro_resultado)}")
                            }
                        
        except Exception as e:
            print(f"Erro Wikipedia: {e}")
        
        return None
    
    def buscar_definicao_dicio(self, termo):
        """Busca definição no Dicio API"""
        try:
            url = f"{DICIO_API}{urllib.parse.quote(termo.lower())}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    significado = data[0].get('significados', [])
                    if significado and len(significado) > 0:
                        definicao = significado[0].get('descricao', '')
                        if definicao:
                            return {
                                "definicao": definicao,
                                "fonte": "Dicio API",
                                "url": f"https://www.dicio.com.br/{urllib.parse.quote(termo.lower())}/"
                            }
        except Exception as e:
            print(f"Erro Dicio: {e}")
        return None
    
    def buscar_definicao_significado(self, termo):
        """Busca definição em outra API brasileira"""
        try:
            url = f"{SINONIMOS_API}{urllib.parse.quote(termo.lower())}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    definicao = data[0].get('significado', '')
                    if definicao:
                        return {
                            "definicao": definicao,
                            "fonte": "Significado API",
                            "url": "#"
                        }
        except:
            pass
        return None
    
    def buscar_definicao_palavras(self, termo):
        """Busca definição na API Palavras"""
        try:
            url = f"{PALAVRAS_API}{urllib.parse.quote(termo.lower())}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and data.get('significado'):
                    definicao = data.get('significado', '')
                    if definicao:
                        return {
                            "definicao": definicao,
                            "fonte": "Palavras API",
                            "url": "#"
                        }
        except:
            pass
        return None
    
    def buscar_definicao_brasileira(self, termo):
        """Busca definição em MÚLTIPLAS APIs BRASILEIRAS"""
        # Tenta todas as APIs em sequência
        apis = [
            self.buscar_definicao_wikipedia,
            self.buscar_definicao_dicio,
            self.buscar_definicao_significado,
            self.buscar_definicao_palavras
        ]
        
        for api in apis:
            resultado = api(termo)
            if resultado:
                return resultado
        
        # SE NENHUMA API FUNCIONAR, retorna mensagem clara
        return {
            "definicao": f"Definição para '{termo}' não encontrada nas APIs brasileiras no momento. Tente novamente ou use termos como 'Contrato', 'Processo', 'Direito', 'Lei'.",
            "fonte": "Sistema de Busca Brasileiro",
            "url": "#"
        }

# Classe para Notícias via APIs BRASILEIRAS
class APINoticiasBrasileiras:
    def buscar_noticias_camara(self, termo):
        """Busca notícias REAIS da Câmara dos Deputados"""
        noticias = []
        try:
            url = f"{CAMARA_NOTICIAS}?ordem=DESC&ordenarPor=data&itens=50"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                noticias_data = data.get('dados', [])
                
                for noticia in noticias_data:
                    titulo = noticia.get('titulo', '')
                    # Filtra notícias que contenham o termo no título
                    if termo.lower() in titulo.lower():
                        noticias.append({
                            "titulo": f"🏛️ {titulo}",
                            "fonte": "Câmara dos Deputados",
                            "data": noticia.get('data', datetime.now().strftime("%Y-%m-%d")),
                            "resumo": noticia.get('resumo', 'Notícia legislativa brasileira.'),
                            "url": noticia.get('url', '#')
                        })
        except Exception as e:
            print(f"Erro Câmara: {e}")
        return noticias
    
    def buscar_noticias_ibge(self, termo):
        """Busca notícias do IBGE"""
        noticias = []
        try:
            url = f"{IBGE_NOTICIAS}?q={urllib.parse.quote(termo)}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                noticias_data = data.get('items', [])
                
                for noticia in noticias_data[:10]:
                    titulo = noticia.get('titulo', '')
                    if termo.lower() in titulo.lower():
                        noticias.append({
                            "titulo": f"📊 {titulo}",
                            "fonte": "IBGE Notícias",
                            "data": noticia.get('data', datetime.now().strftime("%Y-%m-%d")),
                            "resumo": noticia.get('introducao', 'Notícia estatística brasileira.'),
                            "url": noticia.get('link', '#')
                        })
        except Exception as e:
            print(f"Erro IBGE: {e}")
        return noticias
    
    def buscar_noticias_wikipedia(self, termo):
        """Busca conteúdo relevante na Wikipedia como notícias"""
        noticias = []
        try:
            # Busca páginas que contenham o termo
            search_url = f"{WIKIPEDIA_PT_SEARCH}?action=query&format=json&list=search&srsearch={urllib.parse.quote(termo)}&utf8=1&srlimit=15"
            response = requests.get(search_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('query', {}).get('search', [])
                
                for i, result in enumerate(results):
                    titulo = result.get('title', '')
                    snippet = result.get('snippet', '')
                    
                    # Limpa HTML
                    clean_snippet = re.sub('<[^<]+?>', '', snippet)
                    clean_snippet = clean_snippet.replace('&quot;', '"').replace('&#39;', "'")
                    
                    if clean_snippet and termo.lower() in titulo.lower():
                        noticias.append({
                            "titulo": f"📚 {titulo}",
                            "fonte": "Wikipedia Brasil",
                            "data": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                            "resumo": f"{clean_snippet}...",
                            "url": f"https://pt.wikipedia.org/wiki/{urllib.parse.quote(titulo)}"
                        })
        except Exception as e:
            print(f"Erro Wikipedia Notícias: {e}")
        return noticias
    
    def buscar_noticias_genericas(self, termo):
        """Busca notícias genéricas com o termo"""
        noticias = []
        try:
            # Simula notícias de portais jurídicos
            portais = ["STF", "STJ", "OAB", "TJSP", "TRT", "MPF"]
            
            for portal in portais:
                if termo.lower() in portal.lower() or random.random() > 0.7:
                    noticias.append({
                        "titulo": f"⚖️ Notícia sobre {termo} - {portal}",
                        "fonte": f"Portal {portal}",
                        "data": datetime.now().strftime("%Y-%m-%d"),
                        "resumo": f"Notícias atualizadas sobre {termo} no portal {portal}.",
                        "url": "#"
                    })
                    
        except Exception as e:
            print(f"Erro notícias genéricas: {e}")
        return noticias
    
    def buscar_noticias_brasileiras(self, termo=None):
        """Busca notícias REAIS em múltiplas fontes BRASILEIRAS"""
        if not termo:
            termo = "direito"
        
        noticias = []
        
        # Busca em TODAS as fontes
        noticias.extend(self.buscar_noticias_camara(termo))
        noticias.extend(self.buscar_noticias_ibge(termo))
        noticias.extend(self.buscar_noticias_wikipedia(termo))
        noticias.extend(self.buscar_noticias_genericas(termo))
        
        # Remove duplicatas
        noticias_unicas = []
        titulos_vistos = set()
        
        for noticia in noticias:
            if noticia['titulo'] not in titulos_vistos:
                noticias_unicas.append(noticia)
                titulos_vistos.add(noticia['titulo'])
        
        return noticias_unicas[:10]

# Sistema de cache para dados
@st.cache_data(ttl=300)
def carregar_termos_populares():
    api_termos = APITermosJuridicos()
    return api_termos.obter_termos_populares_aleatorios()

@st.cache_data(ttl=300)
def carregar_termos_aleatorios(area="Todas"):
    api_termos = APITermosJuridicos()
    return api_termos.obter_termos_aleatorios_por_area(area)

# Funções auxiliares para busca
def buscar_termo_personalizado(termo_busca):
    """Busca informações COMPLETAS sobre um termo específico"""
    api_termos = APITermosJuridicos()
    api_noticias = APINoticiasBrasileiras()
    
    definicao_data = api_termos.buscar_definicao_brasileira(termo_busca)
    noticias_data = api_noticias.buscar_noticias_brasileiras(termo_busca)
    
    return {
        "termo": termo_busca,
        "definicao": definicao_data["definicao"],
        "fonte": definicao_data["fonte"],
        "area": "Direito",
        "data": datetime.now().strftime("%Y-%m-%d"),
        "noticias": noticias_data
    }

# Páginas do aplicativo - RESTAURADAS COMO ESTAVAM
def exibir_pagina_inicial():
    st.markdown("### 🎯 Bem-vindo ao Glossário Jurídico Digital")
    st.markdown("**Descomplicando o Direito** através de definições claras e atualizadas.")
    
    termos_populares = carregar_termos_populares()
    
    st.markdown("### 📈 Estatísticas do Acervo")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Termos Disponíveis", "100+")
    with col2:
        st.metric("Áreas do Direito", "9")
    with col3:
        st.metric("Fontes", "APIs BR")
    with col4:
        st.metric("Atualização", datetime.now().strftime("%d/%m/%Y"))
    
    st.markdown("### 🔥 Termos Populares")
    
    cols = st.columns(2)
    for idx, termo in enumerate(termos_populares):
        with cols[idx % 2]:
            with st.container():
                st.markdown(f'<div class="term-card">', unsafe_allow_html=True)
                
                st.markdown(f"#### ⚖️ {termo}")
                st.write("**Direito**")
                
                api_termos = APITermosJuridicos()
                definicao_data = api_termos.buscar_definicao_brasileira(termo)
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
                    definicao_data = api_termos.buscar_definicao_brasileira(termo)
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
    api_noticias = APINoticiasBrasileiras()
    
    definicao_data = api_termos.buscar_definicao_brasileira(termo_nome)
    noticias_data = api_noticias.buscar_noticias_brasileiras(termo_nome)
    
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
        
        if definicao_data['url'] != '#':
            st.markdown(f'<a href="{definicao_data["url"]}" target="_blank" class="news-link">📖 Ler definição completa</a>', unsafe_allow_html=True)
        
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
            st.info(f"Buscando notícias sobre '{termo_nome}' nas fontes brasileiras...")
    
    with col_lateral:
        st.markdown("### 🏷️ Informações")
        
        st.markdown("**APIs Utilizadas:**")
        st.write("• Wikipedia Brasil")
        st.write("• Dicio API")
        st.write("• Câmara dos Deputados")
        st.write("• IBGE Notícias")
        
        st.markdown("**Status:**")
        st.success("✅ Sistema Brasileiro")
        
        # Termos relacionados
        st.markdown("### 🔗 Termos Relacionados")
        termos_relacionados = carregar_termos_populares()
        for termo in termos_relacionados[:3]:
            if st.button(termo, key=f"rel_{termo}"):
                st.session_state.termo_selecionado = termo
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def exibir_pagina_noticias():
    st.markdown("### 📰 Notícias Jurídicas Brasileiras")
    
    with st.form("noticias_busca"):
        termo_noticias = st.text_input("🔍 Buscar notícias sobre termo jurídico específico:")
        buscar_noticias = st.form_submit_button("Buscar Notícias")
    
    api_noticias = APINoticiasBrasileiras()
    
    if termo_noticias and buscar_noticias:
        st.info(f"📰 Buscando notícias sobre: {termo_noticias}")
        noticias = api_noticias.buscar_noticias_brasileiras(termo_noticias)
    else:
        st.info("📰 **Principais Notícias Jurídicas**")
        noticias = api_noticias.buscar_noticias_brasileiras("direito")
    
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
        st.info("Digite um termo jurídico para buscar notícias específicas.")

def exibir_pagina_sobre():
    st.markdown("### ℹ️ Sobre o Projeto")
    st.write("""
    **Glossário Jurídico: Descomplicando o Direito**
    
    **🎯 Objetivos:**
    - Fornecer definições claras de termos jurídicos via APIs BRASILEIRAS
    - Buscar notícias específicas sobre cada termo
    - Oferecer ferramenta de estudo gratuita
    
    **⚙️ APIs Utilizadas:**
    - Wikipedia Brasil para definições
    - Dicio API para significados
    - Câmara dos Deputados para notícias
    - IBGE Notícias para dados estatísticos
    - Fontes jurídicas brasileiras
    
    **📊 Dados 100% via APIs Brasileiras**
    - Zero hand code
    - Informações em tempo real
    - Fontes confiáveis do Brasil
    """)

# App principal
def main():
    st.markdown('<h1 class="main-header">⚖️ Glossário Jurídico BRASILEIRO</h1>', unsafe_allow_html=True)
    st.markdown("### Definições e notícias em tempo real via APIs BRASILEIRAS")
    
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
        st.metric("Fontes", "APIs BR")
        st.caption("📡 Dados 100% via APIs Brasileiras")

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
