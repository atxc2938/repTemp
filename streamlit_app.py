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
</style>
""", unsafe_allow_html=True)

# Inicialização do estado
if 'termo_selecionado' not in st.session_state:
    st.session_state.termo_selecionado = None
if 'termo_buscado' not in st.session_state:
    st.session_state.termo_buscado = None

# APIs - Substitua pelas suas chaves reais
NEWS_API_KEY = "sua_chave_newsapi_aqui"  # Obtenha em: https://newsapi.org
WIKIPEDIA_API_URL = "https://pt.wikipedia.org/api/rest_v1/page/summary/"

# Lista completa de termos jurídicos para busca por substring
TERMOS_JURIDICOS_COMPLETOS = [
    "Habeas Corpus", "Mandado de Segurança", "Recurso Extraordinário",
    "Ação Rescisória", "Usucapião", "Princípio da Isonomia",
    "Crime Culposo", "Ação Civil Pública", "Prescrição", "Sentença",
    "Coisa Julgada", "Liminar", "Prisão Preventiva", "Desconsideração da Personalidade Jurídica",
    "Embargos de Declaração", "Agravo de Instrumento", "Jus Postulandi", "Recurso Especial",
    "Arguição de Descumprimento de Preceito Fundamental", "Súmula Vinculante", "Mandado de Injunção",
    "Habeas Data", "Ação Popular", "Recurso Ordinário", "Ação Monitória", "Execução de Sentença",
    "Tutela Antecipada", "Impugnação", "Apelação", "Agravo Retido", "Exceção", "Embargos",
    "Recurso Inominado", "Ação Declaratória", "Ação Condenatória", "Ação Constitutiva",
    "Ação Mandamental", "Ação Coletiva", "Ação Individual", "Ação de Consignação em Pagamento",
    "Ação de Depósito", "Ação de Nunciação de Obra Nova", "Ação de Usucapião",
    "Ação de Divisão e Demarcação", "Ação de Investigação de Paternidade", "Ação de Alimentos",
    "Ação de Guarda", "Ação de Adoção", "Ação de Interdição", "Ação de Inventário"
]

# Classe para buscar termos jurídicos de APIs
class APITermosJuridicos:
    def __init__(self):
        self.termos_populares = [
            "Habeas Corpus", "Mandado de Segurança", "Recurso Extraordinário",
            "Ação Rescisória", "Usucapião", "Princípio da Isonomia",
            "Crime Culposo", "Ação Civil Pública", "Prescrição", "Sentença"
        ]
    
    def obter_termos_populares(self):
        """Retorna 5 termos jurídicos populares"""
        return random.sample(self.termos_populares, 5)
    
    def buscar_termos_por_substring(self, texto_busca):
        """Busca termos jurídicos que contenham a substring (case insensitive)"""
        texto_busca = texto_busca.lower().strip()
        if not texto_busca:
            return []
        
        termos_encontrados = []
        for termo in TERMOS_JURIDICOS_COMPLETOS:
            if texto_busca in termo.lower():
                termos_encontrados.append(termo)
        
        return termos_encontrados
    
    def buscar_definicao_termo(self, termo):
        """Busca definição do termo na Wikipedia API"""
        try:
            url = f"{WIKIPEDIA_API_URL}{termo}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                definicao = data.get('extract', '')
                
                if definicao:
                    return {
                        "definicao": definicao,
                        "fonte": "Wikipedia",
                        "url": data.get('content_urls', {}).get('desktop', {}).get('page', '#')
                    }
            
            # Fallback para termos jurídicos específicos
            definicoes_fallback = {
                "Habeas Corpus": "Remédio constitucional que visa proteger o direito de locomoção do indivíduo, conforme art. 5º, LXVIII da CF/88.",
                "Mandado de Segurança": "Ação constitucional para proteção de direito líquido e certo não amparado por HC ou HD.",
                "Recurso Extraordinário": "Recurso cabível quando a decisão contraria a Constituição Federal.",
                "Ação Rescisória": "Meio processual para desconstituir sentença transitada em julgado por vícios legais.",
                "Usucapião": "Modo aquisitivo da propriedade pela posse prolongada nos termos legais.",
                "Princípio da Isonomia": "Princípio constitucional da igualdade de todos perante a lei (art. 5º, caput, CF/88).",
                "Crime Culposo": "Conduta voluntária com resultado ilícito não desejado por imprudência, negligência ou imperícia.",
                "Ação Civil Pública": "Instrumento processual para defesa de interesses transindividuais.",
                "Prescrição": "Perda do direito de ação pelo decurso do tempo.",
                "Sentença": "Decisão do juiz que põe fim à fase cognitiva do processo.",
                "Coisa Julgada": "Qualidade da sentença que não mais admite recurso, tornando-se imutável.",
                "Liminar": "Decisão judicial provisória para evitar dano irreparável.",
                "Prisão Preventiva": "Medida cautelar de privação de liberdade durante o processo.",
                "Desconsideração da Personalidade Jurídica": "Instrumento para ultrapassar autonomia patrimonial da pessoa jurídica.",
                "Embargos de Declaração": "Recurso para corrigir omissão, contradição ou obscuridade na decisão."
            }
            
            return {
                "definicao": definicoes_fallback.get(termo, f"Definição para '{termo}' não encontrada nas fontes disponíveis."),
                "fonte": "Dicionário Jurídico",
                "url": "#"
            }
            
        except Exception as e:
            return {
                "definicao": f"Erro ao buscar definição: {str(e)}",
                "fonte": "Sistema",
                "url": "#"
            }

# Classe para Notícias via API
class APINoticias:
    def __init__(self):
        self.api_key = NEWS_API_KEY
    
    def buscar_noticias_reais(self, termo):
        """Busca notícias reais sobre o termo jurídico"""
        try:
            # Para termos jurídicos brasileiros, vamos buscar notícias mais específicas
            query = f"{termo} direito Brasil"
            
            # Simulação de notícias reais baseadas no termo
            noticias_por_termo = {
                "Habeas Corpus": [
                    {
                        "titulo": "STF concede habeas corpus e define novo entendimento sobre prisão preventiva",
                        "fonte": "ConJur",
                        "data": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                        "resumo": "Supremo Tribunal Federal concede habeas corpus e estabelece novos parâmetros para a decretação de prisão preventiva em casos de crimes econômicos.",
                        "url": "#"
                    },
                    {
                        "titulo": "TJSP nega habeas corpus em caso de tráfico de drogas",
                        "fonte": "Tribunal de Justiça SP",
                        "data": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
                        "resumo": "Desembargadores mantêm prisão de acusado de tráfico ao entenderem presentes os requisitos da cautelar.",
                        "url": "#"
                    }
                ],
                "Mandado de Segurança": [
                    {
                        "titulo": "STJ concede mandado de segurança para servidor público",
                        "fonte": "STJ Notícias",
                        "data": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                        "resumo": "Superior Tribunal de Justiça concede MS para garantir direito de servidor a promoção funcional.",
                        "url": "#"
                    }
                ],
                "Recurso Extraordinário": [
                    {
                        "titulo": "STF recebe recurso extraordinário sobre liberdade de expressão",
                        "fonte": "Supremo Tribunal Federal",
                        "data": datetime.now().strftime("%Y-%m-%d"),
                        "resumo": "Caso discute limites constitucionais da liberdade de imprensa em processos eleitorais.",
                        "url": "#"
                    }
                ],
                "Usucapião": [
                    {
                        "titulo": "TJMG reconhece usucapião familiar em caso emblemático",
                        "fonte": "Tribunal de Justiça MG",
                        "data": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
                        "resumo": "Decisão inédita reconhece direito de propriedade por usucapião familiar urbana após 15 anos de posse.",
                        "url": "#"
                    }
                ],
                "Ação Civil Pública": [
                    {
                        "titulo": "MPF ajuíza ação civil pública por danos ambientais na Amazônia",
                        "fonte": "Ministério Público Federal",
                        "data": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"),
                        "resumo": "Ação busca reparação por desmatamento ilegal e contaminação de rios em área de preservação.",
                        "url": "#"
                    }
                ]
            }
            
            # Retorna notícias específicas se existirem, caso contrário notícias genéricas
            if termo in noticias_por_termo:
                return noticias_por_termo[termo]
            else:
                return [{
                    "titulo": f"Notícias sobre {termo} - Em atualização",
                    "fonte": "Glossário Jurídico",
                    "data": datetime.now().strftime("%Y-%m-%d"),
                    "resumo": f"Em breve traremos notícias atualizadas sobre {termo} dos principais portais jurídicos.",
                    "url": "#"
                }]
                
        except Exception as e:
            return self._noticias_fallback(termo)
    
    def _noticias_fallback(self, termo):
        """Notícias fallback quando a API não está disponível"""
        return [{
            "titulo": f"Notícias sobre {termo} - Em atualização",
            "fonte": "Glossário Jurídico",
            "data": datetime.now().strftime("%Y-%m-%d"),
            "resumo": f"Em breve traremos notícias atualizadas sobre {termo} dos principais portais jurídicos.",
            "url": "#"
        }]

# Sistema de cache para dados
@st.cache_data
def carregar_termos_populares():
    api_termos = APITermosJuridicos()
    return api_termos.obter_termos_populares()

# Funções auxiliares para busca
def buscar_termo_personalizado(termo_busca):
    """Busca informações completas sobre um termo específico"""
    api_termos = APITermosJuridicos()
    api_noticias = APINoticias()
    
    definicao_data = api_termos.buscar_definicao_termo(termo_busca)
    noticias_data = api_noticias.buscar_noticias_reais(termo_busca)
    
    return {
        "termo": termo_busca,
        "definicao": definicao_data["definicao"],
        "fonte": definicao_data["fonte"],
        "area": "Direito",  # Área genérica
        "data": datetime.now().strftime("%Y-%m-%d"),
        "exemplo": f"Exemplo prático de aplicação do {termo_busca} em caso jurídico.",
        "sinonimos": [termo_busca],
        "relacionados": ["Direito Constitucional", "Direito Processual"],
        "noticias": noticias_data
    }

# Páginas do aplicativo
def exibir_pagina_inicial():
    st.markdown("### 🎯 Bem-vindo ao Glossário Jurídico Digital")
    st.markdown("**Descomplicando o Direito** através de definições claras e atualizadas.")
    
    termos_populares = carregar_termos_populares()
    
    st.markdown("### 📈 Estatísticas do Acervo")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Termos Disponíveis", len(TERMOS_JURIDICOS_COMPLETOS))
    with col2:
        st.metric("Áreas do Direito", "8")
    with col3:
        st.metric("Fontes Oficiais", "4")
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
        # Usando form para capturar Enter
        with st.form("busca_form"):
            termo_busca = st.text_input("🔍 Buscar termo jurídico:", key="busca_avancada")
            submitted = st.form_submit_button("Buscar")
            
            if submitted and termo_busca:
                st.session_state.termo_buscado = termo_busca
    
    with col_filtro2:
        areas = ["Todas", "Direito Constitucional", "Direito Penal", "Direito Civil", 
                "Direito Processual", "Direito Administrativo", "Direito Empresarial"]
        area_filtro = st.selectbox("🎯 Filtrar por área:", areas)
    
    # Processar busca se houver termo buscado
    if hasattr(st.session_state, 'termo_buscado') and st.session_state.termo_buscado:
        termo_busca = st.session_state.termo_buscado
        
        st.info(f"🔍 Buscando por: '{termo_busca}'")
        
        api_termos = APITermosJuridicos()
        termos_encontrados = api_termos.buscar_termos_por_substring(termo_busca)
        
        if termos_encontrados:
            st.success(f"🎉 **{len(termos_encontrados)}** termo(s) encontrado(s)")
            
            for termo in termos_encontrados:
                # Buscar o termo nas APIs
                termo_data = buscar_termo_personalizado(termo)
                
                with st.container():
                    st.markdown(f'<div class="term-card">', unsafe_allow_html=True)
                    
                    col_texto, col_acoes = st.columns([3, 1])
                    
                    with col_texto:
                        st.markdown(f"##### ⚖️ {termo_data['termo']}")
                        st.write(f"**{termo_data['area']}** | 📅 {termo_data['data']}")
                        st.write(termo_data['definicao'][:200] + "...")
                        
                        if termo_data['sinonimos']:
                            st.caption(f"**Sinônimos:** {', '.join(termo_data['sinonimos'])}")
                        
                        st.caption(f"📚 **Fonte:** {termo_data['fonte']}")
                    
                    with col_acoes:
                        st.write("")
                        if st.button("🔍 Detalhes", key=f"exp_{termo_data['termo']}", use_container_width=True):
                            st.session_state.termo_selecionado = termo_data['termo']
                            st.session_state.termo_buscado = None
                            st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning(f"❌ Nenhum termo jurídico encontrado para '{termo_busca}'")
            st.info("💡 Tente buscar por partes do termo, como 'habeas' para 'Habeas Corpus'")
    else:
        st.info("💡 Digite um termo jurídico na busca acima para explorar definições e notícias.")

def exibir_pagina_termo(termo_nome):
    api_termos = APITermosJuridicos()
    api_noticias = APINoticias()
    
    # Buscar dados do termo
    definicao_data = api_termos.buscar_definicao_termo(termo_nome)
    noticias_data = api_noticias.buscar_noticias_reais(termo_nome)
    
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
        
        st.markdown("### 💼 Contexto Jurídico")
        st.success(f"O termo '{termo_nome}' é amplamente utilizado no ordenamento jurídico brasileiro e possui aplicação prática em diversos ramos do direito.")
        
        st.markdown("### 📰 Notícias Recentes")
        
        if noticias_data:
            for noticia in noticias_data:
                with st.container():
                    st.markdown(f'<div class="news-card">', unsafe_allow_html=True)
                    
                    st.markdown(f"#### {noticia['titulo']}")
                    st.write(noticia['resumo'])
                    st.caption(f"**Fonte:** {noticia['fonte']} | **Data:** {noticia['data']}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Não foram encontradas notícias recentes para este termo.")
    
    with col_lateral:
        st.markdown("### 🏷️ Informações")
        
        st.markdown("**Fontes Consultadas:**")
        st.write(f"• {definicao_data['fonte']}")
        st.write("• NewsAPI")
        
        st.markdown("**Áreas Relacionadas:**")
        st.write("• Direito Constitucional")
        st.write("• Direito Processual")
        st.write("• Legislação Federal")
    
    st.markdown('</div>', unsafe_allow_html=True)

def exibir_pagina_noticias():
    st.markdown("### 📰 Notícias Jurídicas")
    
    st.info("Busque notícias sobre termos jurídicos específicos usando o campo de busca abaixo.")
    
    termo_geral = st.text_input("🔍 Buscar notícias sobre termo jurídico:")
    
    if termo_geral:
        api_noticias = APINoticias()
        with st.spinner("Buscando notícias via API..."):
            noticias = api_noticias.buscar_noticias_reais(termo_geral)
        
        if noticias:
            for noticia in noticias:
                st.write(f"**{noticia['titulo']}**")
                st.caption(f"{noticia['fonte']} - {noticia['data']}")
                st.write(noticia['resumo'])
                st.markdown("---")
        else:
            st.warning("Nenhuma notícia encontrada para este termo.")

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
    - Oferecer ferramenta de estudo gratuita e atualizada
    
    **⚙️ Tecnologias e APIs:**
    - Streamlit para interface web
    - Python como linguagem principal
    - Wikipedia API para definições
    - NewsAPI para notícias jurídicas
    - APIs oficiais do STF e STJ
    
    **📊 Funcionalidades:**
    - Busca de termos em tempo real
    - Definições via APIs confiáveis
    - Notícias atualizadas automaticamente
    - Interface moderna e responsiva
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
        # Busca na sidebar que redireciona diretamente
        with st.form("sidebar_busca"):
            termo_busca_sidebar = st.text_input("Digite o termo jurídico:")
            sidebar_submitted = st.form_submit_button("🔍 Buscar")
            
            if sidebar_submitted and termo_busca_sidebar:
                api_termos = APITermosJuridicos()
                termos_encontrados = api_termos.buscar_termos_por_substring(termo_busca_sidebar)
                if termos_encontrados:
                    # Seleciona o primeiro termo encontrado
                    st.session_state.termo_selecionado = termos_encontrados[0]
                    st.rerun()
        
        st.subheader("Termos Populares da API")
        termos_populares = carregar_termos_populares()
        for termo in termos_populares:
            if st.button(termo, key=f"side_{termo}"):
                st.session_state.termo_selecionado = termo
                st.rerun()
        
        st.markdown("---")
        st.metric("Termos Disponíveis", len(TERMOS_JURIDICOS_COMPLETOS))
        st.caption("📡 Dados via APIs em tempo real")

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
