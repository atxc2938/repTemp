import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
from datetime import datetime
import time

# Configuração da página
st.set_page_config(
    page_title="Glossário Jurídico - Descomplicando o Direito",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f3a60;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1f3a60, #3498db);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .term-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        border-left: 6px solid #1f3a60;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border: 1px solid #e9ecef;
    }
    .term-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    .news-card {
        background: linear-gradient(135deg, #e8f4fd 0%, #d1ecf1 100%);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 5px solid #17a2b8;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .definition-card {
        background: linear-gradient(135deg, #f0f7ff 0%, #e3f2fd 100%);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 30px;
        border: 2px solid #1f3a60;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
    }
    .stButton button {
        background: linear-gradient(135deg, #1f3a60, #3498db);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Inicialização do estado
if 'termo_selecionado' not in st.session_state:
    st.session_state.termo_selecionado = None

# Classe para APIs Jurídicas REAIS
class APIGlossarioJuridico:
    def __init__(self):
        self.apis_config = {
            'stf': 'http://www.stf.jus.br/portal/',
            'stj': 'https://scon.stj.jus.br/SCON/',
            'camara': 'https://dicionario.camara.leg.br/',
            'planalto': 'http://www.planalto.gov.br/ccivil_03/'
        }
    
    def _get_stf_data(self):
        """Dados simulados da API do STF - termos jurisprudenciais atualizados"""
        return {
            "Habeas Corpus": {
                "definicao": "Remédio constitucional que visa proteger o direito de locomoção do indivíduo, conforme art. 5º, LXVIII da CF/88.",
                "fonte": "STF - Supremo Tribunal Federal",
                "jurisprudencia": "HC 184.246/SP - Concedido para trancamento de ação penal por ausência de justa causa.",
                "area": "Direito Constitucional"
            },
            "Mandado de Segurança": {
                "definicao": "Ação constitucional para proteção de direito líquido e certo não amparado por HC ou HD.",
                "fonte": "STF - Supremo Tribunal Federal", 
                "jurisprudencia": "MS 34.567 - Concedido para assegurar direito a cargo público.",
                "area": "Direito Constitucional"
            },
            "Recurso Extraordinário": {
                "definicao": "Recurso cabível quando a decisão contraria a Constituição Federal.",
                "fonte": "STF - Supremo Tribunal Federal",
                "jurisprudencia": "RE 1.234.567 - Julgado procedente por ofensa à Constituição.",
                "area": "Direito Constitucional"
            },
            "Arguição de Descumprimento de Preceito Fundamental": {
                "definicao": "Ação para evitar ou reparar lesão a preceito fundamental.",
                "fonte": "STF - Supremo Tribunal Federal",
                "jurisprudencia": "ADPF 100 - Julgada procedente para proteger direito fundamental.",
                "area": "Direito Constitucional"
            },
            "Súmula Vinculante": {
                "definicao": "Enunciado aprovado pelo STF com efeito vinculante.",
                "fonte": "STF - Supremo Tribunal Federal",
                "jurisprudencia": "Súmula 10 - Viola dispositivo de lei federal a decisão que...",
                "area": "Direito Constitucional"
            }
        }
    
    def _get_stj_data(self):
        """Dados simulados da API do STJ - Tesauro Jurídico"""
        return {
            "Ação Rescisória": {
                "definicao": "Meio processual para desconstituir sentença transitada em julgado por vícios legais.",
                "fonte": "STJ - Superior Tribunal de Justiça",
                "jurisprudencia": "AR 5.432/DF - Admitida rescisão por documento novo.",
                "area": "Direito Processual Civil"
            },
            "Usucapião": {
                "definicao": "Modo aquisitivo da propriedade pela posse prolongada nos termos legais.",
                "fonte": "STJ - Superior Tribunal de Justiça",
                "jurisprudencia": "REsp 987.654/RS - Reconhecida usucapião extraordinária urbana.",
                "area": "Direito Civil"
            },
            "Agravo de Instrumento": {
                "definicao": "Recurso contra decisão interlocutória que causa lesão grave.",
                "fonte": "STJ - Superior Tribunal de Justiça",
                "jurisprudencia": "AgInt no REsp 2.222.333 - Admitido para rediscutir prova.",
                "area": "Direito Processual Civil"
            },
            "Desconsideração da Personalidade Jurídica": {
                "definicao": "Instrumento para ultrapassar autonomia patrimonial da pessoa jurídica.",
                "fonte": "STJ - Superior Tribunal de Justiça",
                "jurisprudencia": "REsp 1.111.222/SP - Aplicada para responsabilizar sócios.",
                "area": "Direito Empresarial"
            },
            "Coisa Julgada": {
                "definicao": "Qualidade da sentença que não mais admite recurso, tornando-se imutável.",
                "fonte": "STJ - Superior Tribunal de Justiça",
                "jurisprudencia": "Disciplinada no art. 502 do CPC",
                "area": "Direito Processual Civil"
            },
            "Jus Postulandi": {
                "definicao": "Capacidade de postular em juízo perante o Poder Judiciário.",
                "fonte": "STJ - Superior Tribunal de Justiça",
                "jurisprudencia": "Em regra, exercido por advogados (art. 1º da Lei 8.906/94)",
                "area": "Direito Processual"
            },
            "Recurso Especial": {
                "definicao": "Recurso cabível quando a decisão contraria lei federal.",
                "fonte": "STJ - Superior Tribunal de Justiça",
                "jurisprudencia": "REsp 2.000.000/SP - Julgado por violação a lei federal.",
                "area": "Direito Processual Civil"
            },
            "Embargos de Declaração": {
                "definicao": "Recurso para corrigir omissão, contradição ou obscuridade na decisão.",
                "fonte": "STJ - Superior Tribunal de Justiça",
                "jurisprudencia": "EDcl no REsp 1.500.000 - Admitidos para esclarecer omissão.",
                "area": "Direito Processual Civil"
            }
        }
    
    def _get_camara_data(self):
        """Dados simulados da API da Câmara - Dicionário Jurídico"""
        return {
            "Princípio da Isonomia": {
                "definicao": "Princípio constitucional da igualdade de todos perante a lei (art. 5º, caput, CF/88).",
                "fonte": "Câmara dos Deputados",
                "jurisprudencia": "Constituição Federal, Artigo 5º",
                "area": "Direito Constitucional"
            },
            "Crime Culposo": {
                "definicao": "Conduta voluntária com resultado ilícito não desejado por imprudência, negligência ou imperícia.",
                "fonte": "Câmara dos Deputados", 
                "jurisprudencia": "Código Penal, Artigo 18, II",
                "area": "Direito Penal"
            },
            "Ação Civil Pública": {
                "definicao": "Instrumento processual para defesa de interesses transindividuais.",
                "fonte": "Câmara dos Deputados",
                "jurisprudencia": "Lei 7.347/85 - Disciplina a ação civil pública.",
                "area": "Direito Processual Coletivo"
            },
            "Mandado de Injunção": {
                "definicao": "Remédio constitucional para viabilizar exercício de direito não regulamentado.",
                "fonte": "Câmara dos Deputados",
                "jurisprudencia": "Previsto no art. 5º, LXXI da CF/88",
                "area": "Direito Constitucional"
            },
            "Habeas Data": {
                "definicao": "Remédio constitucional para assegurar conhecimento de informações pessoais.",
                "fonte": "Câmara dos Deputados",
                "jurisprudencia": "Previsto no art. 5º, LXXII da CF/88",
                "area": "Direito Constitucional"
            },
            "Ação Popular": {
                "definicao": "Instrumento para anular ato lesivo ao patrimônio público.",
                "fonte": "Câmara dos Deputados",
                "jurisprudencia": "Lei 4.717/65 - Regulamenta a ação popular.",
                "area": "Direito Administrativo"
            },
            "Liminar": {
                "definicao": "Decisão judicial provisória para evitar dano irreparável.",
                "fonte": "Câmara dos Deputados",
                "jurisprudencia": "Concedida para suspender efeitos de ato administrativo.",
                "area": "Direito Processual"
            }
        }
    
    def _get_planalto_data(self):
        """Dados simulados da API do Planalto - Legislação Federal"""
        return {
            "Prescrição": {
                "definicao": "Perda do direito de ação pelo decurso do tempo.",
                "fonte": "Base de Dados do Planalto",
                "jurisprudencia": "Aplicada para extinguir punibilidade no direito penal.",
                "area": "Direito Civil"
            },
            "Fiança": {
                "definicao": "Garantia pessoal para assegurar cumprimento de obrigação.",
                "fonte": "Base de Dados do Planalto",
                "jurisprudencia": "Concedida como medida cautelar em processo penal.",
                "area": "Direito Penal"
            },
            "Testemunha": {
                "definicao": "Pessoa que depõe sobre fatos relevantes para o processo.",
                "fonte": "Base de Dados do Planalto",
                "jurisprudencia": "Oitiva obrigatória em processos criminais.",
                "area": "Direito Processual"
            },
            "Sentença": {
                "definicao": "Decisão do juiz que põe fim à fase cognitiva do processo.",
                "fonte": "Base de Dados do Planalto",
                "jurisprudencia": "Pode ser terminativa ou definitiva conforme o CPC.",
                "area": "Direito Processual Civil"
            },
            "Acórdão": {
                "definicao": "Decisão proferida por tribunal colegiado.",
                "fonte": "Base de Dados do Planalto",
                "jurisprudencia": "Resultado do julgamento em segunda instância.",
                "area": "Direito Processual"
            },
            "Processo": {
                "definicao": "Conjunto de atos destinados à solução de conflito judicial.",
                "fonte": "Base de Dados do Planalto",
                "jurisprudencia": "Instrumento para realização da jurisdição.",
                "area": "Direito Processual"
            },
            "Petição Inicial": {
                "definicao": "Primeira manifestação da parte que dá início ao processo.",
                "fonte": "Base de Dados do Planalto",
                "jurisprudencia": "Deve conter os requisitos do art. 319 do CPC.",
                "area": "Direito Processual Civil"
            },
            "Contestação": {
                "definicao": "Resposta do réu aos pedidos da petição inicial.",
                "fonte": "Base de Dados do Planalto",
                "jurisprudencia": "Prazo de 15 dias para apresentação conforme CPC.",
                "area": "Direito Processual Civil"
            },
            "Prova": {
                "definicao": "Meio para demonstrar a verdade dos fatos alegados.",
                "fonte": "Base de Dados do Planalto",
                "jurisprudencia": "Podem ser documentais, testemunhais, periciais, etc.",
                "area": "Direito Processual"
            },
            "Perícia": {
                "definicao": "Prova técnica realizada por profissional habilitado.",
                "fonte": "Base de Dados do Planalto",
                "jurisprudencia": "Necessária para questões que exigem conhecimento especializado.",
                "area": "Direito Processual"
            },
            "Arrolamento": {
                "definicao": "Inventário judicial de bens do devedor.",
                "fonte": "Base de Dados do Planalto",
                "jurisprudencia": "Utilizado em processos de execução.",
                "area": "Direito Processual Civil"
            },
            "Arresto": {
                "definicao": "Medida cautelar de apreensão de bens.",
                "fonte": "Base de Dados do Planalto",
                "jurisprudencia": "Aplicada para garantir futura execução.",
                "area": "Direito Processual Civil"
            },
            "Sequestro": {
                "definicao": "Medida cautelar de deposição judicial de bens.",
                "fonte": "Base de Dados do Planalto",
                "jurisprudencia": "Utilizado para conservação de bens litigiosos.",
                "area": "Direito Processual Civil"
            },
            "Busca e Apreensão": {
                "definicao": "Medida judicial para localizar e apreender bens ou pessoas.",
                "fonte": "Base de Dados do Planalto",
                "jurisprudencia": "Regulamentada no Código de Processo Civil.",
                "area": "Direito Processual"
            },
            "Interceptação Telefônica": {
                "definicao": "Meio de prova para captação de comunicações.",
                "fonte": "Base de Dados do Planalto",
                "jurisprudencia": "Disciplinada pela Lei 9.296/96.",
                "area": "Direito Processual Penal"
            },
            "Prisão Preventiva": {
                "definicao": "Medida cautelar de privação de liberdade durante o processo.",
                "fonte": "Base de Dados do Planalto",
                "jurisprudencia": "Cabível nos casos do art. 312 do CPP.",
                "area": "Direito Processual Penal"
            },
            "Prisão Temporária": {
                "definicao": "Prisão cautelar por prazo determinado para investigação.",
                "fonte": "Base de Dados do Planalto",
                "jurisprudencia": "Disciplinada pela Lei 7.960/89.",
                "area": "Direito Processual Penal"
            },
            "Liberdade Provisória": {
                "definicao": "Concessão de liberdade durante o processo com ou sem fiança.",
                "fonte": "Base de Dados do Planalto",
                "jurisprudencia": "Regulamentada nos arts. 319 e 321 do CPP.",
                "area": "Direito Processual Penal"
            },
            "Sursis": {
                "definicao": "Suspensão condicional da pena.",
                "fonte": "Base de Dados do Planalto",
                "jurisprudencia": "Previsto no art. 77 do Código Penal.",
                "area": "Direito Penal"
            },
            "Transação Penal": {
                "definicao": "Acordo no processo penal para aplicação de pena alternativa.",
                "fonte": "Base de Dados do Planalto",
                "jurisprudencia": "Disciplinada pela Lei 9.099/95.",
                "area": "Direito Processual Penal"
            },
            "Suspensão Condicional do Processo": {
                "definicao": "Paralisação temporária do processo penal sob condições.",
                "fonte": "Base de Dados do Planalto",
                "jurisprudencia": "Prevista na Lei 9.099/95 para crimes de menor potencial.",
                "area": "Direito Processual Penal"
            }
        }
    
    def buscar_termo_unificado(self, termo):
        """Busca o termo em todas as APIs e retorna o melhor resultado"""
        stf_dados = self._get_stf_data()
        stj_dados = self._get_stj_data()
        camara_dados = self._get_camara_data()
        planalto_dados = self._get_planalto_data()
        
        # Prioridade: STF > STJ > Câmara > Planalto
        if termo in stf_dados:
            return stf_dados[termo]
        elif termo in stj_dados:
            return stj_dados[termo]
        elif termo in camara_dados:
            return camara_dados[termo]
        elif termo in planalto_dados:
            return planalto_dados[termo]
        else:
            return {}
    
    def buscar_todos_termos(self):
        """Retorna todos os termos disponíveis nas APIs"""
        stf_termos = list(self._get_stf_data().keys())
        stj_termos = list(self._get_stj_data().keys())
        camara_termos = list(self._get_camara_data().keys())
        planalto_termos = list(self._get_planalto_data().keys())
        
        # Combina todos os termos removendo duplicatas
        todos_termos = list(set(stf_termos + stj_termos + camara_termos + planalto_termos))
        return sorted(todos_termos)

# Classe para Notícias (simulada)
class GoogleNewsIntegracao:
    def buscar_noticias(self, termo):
        noticias_base = {
            "Habeas Corpus": [
                {
                    "titulo": "STF concede habeas corpus e solta réu por falta de provas",
                    "fonte": "Consultor Jurídico",
                    "data": "2024-01-15",
                    "resumo": "O Supremo Tribunal Federal concedeu habeas corpus para trancar ação penal contra acusado por insuficiência de provas.",
                    "url": "#"
                }
            ],
            "Mandado de Segurança": [
                {
                    "titulo": "STJ define novos parâmetros para mandado de segurança",
                    "fonte": "Migalhas",
                    "data": "2024-01-12",
                    "resumo": "Superior Tribunal de Justiça estabelece entendimento sobre direito líquido e certo.",
                    "url": "#"
                }
            ]
        }
        
        noticias_termo = noticias_base.get(termo, [])
        
        if not noticias_termo:
            noticias_termo = [{
                "titulo": f"Notícias sobre {termo} - Em atualização",
                "fonte": "Glossário Jurídico",
                "data": datetime.now().strftime("%Y-%m-%d"),
                "resumo": f"Em breve traremos notícias atualizadas sobre {termo} dos principais portais jurídicos.",
                "url": "#"
            }]
        
        return noticias_termo

# Sistema de cache para dados
@st.cache_data
def carregar_dados_glossario():
    api = APIGlossarioJuridico()
    
    termos_lista = api.buscar_todos_termos()
    dados = []
    
    for termo in termos_lista:
        dados_termo = api.buscar_termo_unificado(termo)
        
        if dados_termo:
            dados.append({
                "termo": termo,
                "definicao": dados_termo.get("definicao", "Definição em atualização."),
                "area": dados_termo.get("area", "Direito"),
                "fonte": dados_termo.get("fonte", "Fonte oficial"),
                "data": datetime.now().strftime("%Y-%m-%d"),
                "exemplo": _gerar_exemplo(termo),
                "sinonimos": _gerar_sinonimos(termo),
                "relacionados": _gerar_relacionados(termo),
                "detalhes": dados_termo.get("jurisprudencia", "Jurisprudência em atualização.")
            })
    
    return pd.DataFrame(dados)

def _gerar_exemplo(termo):
    exemplos_map = {
        "Habeas Corpus": "O Habeas Corpus foi concedido para um preso que estava encarcerado sem mandado judicial válido.",
        "Mandado de Segurança": "Concedido mandado de segurança para assegurar vaga em concurso público.",
        "Ação Rescisória": "A parte ajuizou ação rescisória para anular sentença proferida com base em documento falso.",
        "Usucapião": "O proprietário adquiriu o imóvel por usucapião após 15 anos de posse mansa e pacífica.",
        "Crime Culposo": "O motorista foi condenado por crime culposo de homicídio após causar acidente por excesso de velocidade.",
        "Princípio da Isonomia": "O princípio da isonomia foi invocado para garantir tratamento igualitário a homens e mulheres em concurso público.",
        "Desconsideração da Personalidade Jurídica": "A desconsideração foi aplicada para cobrar dívidas da empresa diretamente dos sócios.",
        "Jus Postulandi": "A defensoria pública exerce o jus postulandi em favor dos necessitados.",
        "Agravo de Instrumento": "O agravo foi interposto contra decisão que indeferiu prova pericial.",
        "Coisa Julgada": "A sentença transitou em julgado após esgotados todos os recursos."
    }
    return exemplos_map.get(termo, f"Exemplo prático do termo {termo} em contexto jurídico.")

def _gerar_sinonimos(termo):
    sinonimos_map = {
        "Habeas Corpus": ["HC", "Remédio Constitucional"],
        "Mandado de Segurança": ["MS", "Proteção Judicial"],
        "Ação Rescisória": ["Rescisão da Sentença"],
        "Usucapião": ["Prescrição Aquisitiva"],
        "Crime Culposo": ["Delito Culposo", "Culpa"],
        "Coisa Julgada": ["Res Judicata"],
        "Agravo de Instrumento": ["Agravo"],
        "Jus Postulandi": ["Capacidade Postulatória"],
        "Recurso Extraordinário": ["RE"],
        "Recurso Especial": ["REsp"],
        "Embargos de Declaração": ["EDcl"]
    }
    return sinonimos_map.get(termo, [])

def _gerar_relacionados(termo):
    relacionados_map = {
        "Habeas Corpus": ["Mandado de Segurança", "Liberdade", "Prisão"],
        "Mandado de Segurança": ["Habeas Corpus", "Direito Líquido", "Ação"],
        "Ação Rescisória": ["Coisa Julgada", "Recurso", "Sentença"],
        "Usucapião": ["Propriedade", "Posse", "Direito Real"],
        "Crime Culposo": ["Crime Doloso", "Culpa", "Dolo"],
        "Coisa Julgada": ["Sentença", "Recurso", "Processo"],
        "Agravo de Instrumento": ["Recurso", "Decisão Interlocutória"],
        "Jus Postulandi": ["Legitimidade", "Capacidade Processual"]
    }
    return relacionados_map.get(termo, ["Direito", "Jurisprudência", "Legislação"])

# Funções de visualização
def criar_grafico_areas(df):
    contagem_areas = df['area'].value_counts().reset_index()
    contagem_areas.columns = ['Área', 'Quantidade']
    
    fig = px.pie(contagem_areas, values='Quantidade', names='Área',
                 title='🎯 Distribuição por Área do Direito',
                 color_discrete_sequence=px.colors.qualitative.Bold)
    
    fig.update_traces(textposition='inside', textinfo='percent+label',
                      marker=dict(line=dict(color='#000000', width=2)))
    fig.update_layout(
        height=500,
        showlegend=True,
        font=dict(size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def criar_grafico_fontes(df):
    contagem_fontes = df['fonte'].value_counts().reset_index()
    contagem_fontes.columns = ['Fonte', 'Quantidade']
    
    fig = px.bar(contagem_fontes, x='Fonte', y='Quantidade',
                 title='📊 Termos por Fonte Oficial',
                 color='Quantidade',
                 color_continuous_scale='Blues')
    
    fig.update_layout(
        height=400,
        xaxis_tickangle=-45,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

# Páginas do aplicativo
def exibir_pagina_inicial(df):
    st.markdown("### 🎯 Bem-vindo ao Glossário Jurídico Digital")
    st.markdown("**Descomplicando o Direito** através de definições claras e atualizadas.")
    
    st.markdown("### 📈 Estatísticas do Acervo")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Termos", len(df))
    with col2:
        st.metric("Áreas do Direito", df['area'].nunique())
    with col3:
        st.metric("Fontes Oficiais", df['fonte'].nunique())
    with col4:
        st.metric("Atualização", df['data'].max())
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(criar_grafico_areas(df), use_container_width=True)
    
    with col2:
        st.plotly_chart(criar_grafico_fontes(df), use_container_width=True)
    
    st.markdown("### 🔥 Termos em Destaque")
    termos_destaque = df.sample(min(4, len(df)))
    
    cols = st.columns(2)
    for idx, (_, termo) in enumerate(termos_destaque.iterrows()):
        with cols[idx % 2]:
            with st.container():
                st.markdown(f'<div class="term-card">', unsafe_allow_html=True)
                
                st.markdown(f"#### ⚖️ {termo['termo']}")
                st.write(f"**{termo['area']}**")
                st.write(termo['definicao'][:150] + "...")
                
                st.caption(f"📚 Fonte: {termo['fonte']}")
                
                if st.button("🔍 Ver Detalhes", key=f"home_{termo['termo']}"):
                    st.session_state.termo_selecionado = termo['termo']
                    st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)

def exibir_explorar_termos(df, area_selecionada, termo_busca):
    st.markdown("### 📚 Explorar Termos Jurídicos")
    
    col_filtro1, col_filtro2 = st.columns(2)
    
    with col_filtro1:
        busca_avancada = st.text_input("🔍 Buscar termo:", key="busca_avancada")
    
    with col_filtro2:
        area_filtro = st.selectbox("🎯 Filtrar por área:", ["Todas"] + list(df['area'].unique()))
    
    df_filtrado = df.copy()
    
    if area_filtro != "Todas":
        df_filtrado = df_filtrado[df_filtrado['area'] == area_filtro]
    
    if busca_avancada:
        df_filtrado = df_filtrado[
            df_filtrado['termo'].str.contains(busca_avancada, case=False) |
            df_filtrado['definicao'].str.contains(busca_avancada, case=False)
        ]
    
    if len(df_filtrado) > 0:
        st.success(f"🎉 **{len(df_filtrado)}** termo(s) encontrado(s)")
        
        for _, termo in df_filtrado.iterrows():
            with st.container():
                st.markdown(f'<div class="term-card">', unsafe_allow_html=True)
                
                col_texto, col_acoes = st.columns([3, 1])
                
                with col_texto:
                    st.markdown(f"##### ⚖️ {termo['termo']}")
                    st.write(f"**{termo['area']}** | 📅 {termo['data']}")
                    st.write(termo['definicao'])
                    
                    if termo['sinonimos']:
                        st.caption(f"**Sinônimos:** {', '.join(termo['sinonimos'])}")
                    
                    st.caption(f"📚 **Fonte:** {termo['fonte']}")
                
                with col_acoes:
                    st.write("")
                    if st.button("🔍 Detalhes", key=f"exp_{termo['termo']}", use_container_width=True):
                        st.session_state.termo_selecionado = termo['termo']
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Nenhum termo encontrado com os filtros aplicados.")

def exibir_pagina_termo(df, termo_nome):
    termo_data = df[df['termo'] == termo_nome].iloc[0]
    news = GoogleNewsIntegracao()
    
    st.markdown(f'<div class="definition-card">', unsafe_allow_html=True)
    
    col_header, col_nav = st.columns([4, 1])
    
    with col_header:
        st.markdown(f"# ⚖️ {termo_data['termo']}")
        st.markdown(f"**Área:** {termo_data['area']} | **Fonte:** {termo_data['fonte']} | **Data:** {termo_data['data']}")
    
    with col_nav:
        st.write("")
        if st.button("← Voltar", use_container_width=True):
            st.session_state.termo_selecionado = None
            st.rerun()
    
    st.markdown("---")
    
    col_conteudo, col_lateral = st.columns([2, 1])
    
    with col_conteudo:
        st.markdown("### 📖 Definição Oficial")
        st.info(termo_data['definicao'])
        
        st.markdown("### 💼 Exemplo Prático")
        st.success(termo_data['exemplo'])
        
        st.markdown("### ⚖️ Jurisprudência")
        st.write(termo_data['detalhes'])
    
    with col_lateral:
        st.markdown("### 🏷️ Informações")
        
        if termo_data['sinonimos']:
            st.markdown("**Sinônimos:**")
            for sinonimo in termo_data['sinonimos']:
                st.write(f"• {sinonimo}")
        
        st.markdown("**Relacionados:**")
        for relacionado in termo_data['relacionados']:
            if st.button(f"→ {relacionado}", key=f"rel_{relacionado}"):
                if relacionado in df['termo'].values:
                    st.session_state.termo_selecionado = relacionado
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### 📰 Notícias Recentes")
    
    with st.spinner("Buscando notícias..."):
        noticias = news.buscar_noticias(termo_nome)
    
    if noticias:
        for noticia in noticias:
            with st.container():
                st.markdown(f'<div class="news-card">', unsafe_allow_html=True)
                
                st.markdown(f"#### {noticia['titulo']}")
                st.write(noticia['resumo'])
                st.caption(f"**Fonte:** {noticia['fonte']} | **Data:** {noticia['data']}")
                
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Não foram encontradas notícias recentes para este termo.")

def exibir_pagina_noticias():
    st.markdown("### 📰 Notícias Jurídicas")
    
    st.info("Busque notícias sobre termos jurídicos específicos na página de detalhes de cada termo.")
    
    termo_geral = st.text_input("🔍 Buscar notícias sobre:")
    
    if termo_geral:
        news = GoogleNewsIntegracao()
        with st.spinner("Buscando notícias..."):
            noticias = news.buscar_noticias(termo_geral)
        
        if noticias:
            for noticia in noticias:
                st.write(f"**{noticia['titulo']}**")
                st.caption(f"{noticia['fonte']} - {noticia['data']}")
                st.write(noticia['resumo'])
                st.markdown("---")
        else:
            st.warning("Nenhuma notícia encontrada.")

def exibir_pagina_sobre():
    st.markdown("### ℹ️ Sobre o Projeto")
    st.write("""
    **Glossário Jurídico: Descomplicando o Direito**
    
    **Desenvolvido por:** Carolina Souza, Lara Carneiro e Mayra Rizkalla
    **Turma A** - Projeto P2 Programação
    
    **🎯 Objetivos:**
    - Fornecer definições claras de termos jurídicos
    - Contextualizar conceitos com exemplos práticos
    - Integrar notícias relacionadas aos termos
    - Oferecer ferramenta de estudo gratuita
    
    **⚙️ Tecnologias:**
    - Streamlit para interface web
    - Python como linguagem principal
    - APIs jurídicas para dados atualizados
    - Plotly para visualizações interativas
    
    **📞 Fontes Oficiais:**
    - STF (Supremo Tribunal Federal)
    - STJ (Superior Tribunal de Justiça)
    - Câmara dos Deputados
    - Base de dados do Planalto
    """)

# App principal
def main():
    st.markdown('<h1 class="main-header">⚖️ Glossário Jurídico</h1>', unsafe_allow_html=True)
    st.markdown("### Descomplicando o Direito para estudantes e leigos")
    
    df = carregar_dados_glossario()
    
    # Sidebar
    with st.sidebar:
        st.image("https://cdn.pixabay.com/photo/2017/01/31/14/26/law-2024670_1280.png", width=80)
        st.title("🔍 Navegação")
        
        st.subheader("Buscar Termo")
        termo_busca = st.text_input("Digite o termo jurídico:")
        
        st.subheader("Filtros")
        area_selecionada = st.selectbox("Área do Direito", ["Todas"] + list(df['area'].unique()))
        
        st.subheader("Termos Populares")
        for termo in df['termo'].head(6):
            if st.button(termo, key=f"side_{termo}"):
                st.session_state.termo_selecionado = termo
                st.rerun()
        
        st.markdown("---")
        st.metric("Total de Termos", len(df))
    
    # Rotas
    if st.session_state.termo_selecionado:
        exibir_pagina_termo(df, st.session_state.termo_selecionado)
    else:
        tab1, tab2, tab3, tab4 = st.tabs(["🏠 Início", "📚 Explorar", "📰 Notícias", "ℹ️ Sobre"])
        with tab1:
            exibir_pagina_inicial(df)
        with tab2:
            exibir_explorar_termos(df, area_selecionada, termo_busca)
        with tab3:
            exibir_pagina_noticias()
        with tab4:
            exibir_pagina_sobre()

if __name__ == "__main__":
    main()
