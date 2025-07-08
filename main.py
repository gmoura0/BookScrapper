import streamlit as st  # importa a biblioteca Streamlit para criação da interface web
import requests  # para fazer requisições HTTP
from bs4 import BeautifulSoup  # para parsear HTML
import pandas as pd  # para manipulação de dados em DataFrame
import io  # para operações de I/O em memória
import streamlit.components.v1 as components  # para renderizar HTML customizado no Streamlit

# URLs base do site a ser raspado
BASE_URL = "https://books.toscrape.com/"
CATALOGUE_URL = BASE_URL + "catalogue/"
# Cabeçalho HTTP para simular um navegador legítimo
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Configuração da página do Streamlit
st.set_page_config(page_title="📘 Books Streamer", layout="wide")

# ---------- FUNÇÕES ----------

def get_rating(soup):
    """
    Extrai a avaliação (rating) de estrelas do HTML de um livro.
    Retorna a classe CSS correspondente (e.g., 'Three', 'Five').
    """
    r = soup.find("p", class_="star-rating")  # procura o paragráfo com classe 'star-rating'
    return r["class"][1] if r else "None"  # retorna a segunda classe, ou 'None' se não achar


def scrape_book_details(book_url, session):
    """
    Faz requisição à página de detalhes de um livro e retorna um dicionário
    com campos como UPC, preço, disponibilidade, etc.
    Usa uma sessão para reaproveitar conexões.
    """
    res = session.get(book_url, headers=HEADERS)  # requisição GET da URL do livro
    soup = BeautifulSoup(res.text, 'html.parser')  # parse do HTML
    table = soup.find("table", class_="table table-striped")  # encontra a tabela de detalhes
    # inicializa dicionário com chaves vazias
    details = {k: "" for k in [
        "upc", "product type", "price (excl. tax)",
        "price (incl. tax)", "tax", "availability", "number of reviews"
    ]}
    if table:
        # percorre cada linha da tabela e extrai chave/valor
        for row in table.find_all("tr"):
            key = row.th.text.strip().lower()  # nome da coluna
            details[key] = row.td.text.strip()  # valor correspondente
    return details


def scrape_all_pages():
    """
    Raspagem completa de todas as páginas de livros do site.
    Itera até encontrar uma página inexistente (status != 200).
    """
    session = requests.Session()  # cria sessão para eficiência
    books = []  # lista que armazenará todos os livros
    page = 1  # contador de páginas
    while True:
        url = CATALOGUE_URL + f"page-{page}.html"  # URL da página atual
        res = session.get(url, headers=HEADERS)  # requisição para a página
        if res.status_code != 200:
            break  # interrompe loop se não existir mais página

        soup = BeautifulSoup(res.text, 'html.parser')
        articles = soup.find_all("article", class_="product_pod")  # lista de livros
        if not articles:
            break  # interrompe se não encontrar nenhum livro

        for art in articles:
            # extrai dados básicos do livro
            name = art.h3.a["title"]
            rate = get_rating(art)
            price = art.find("p", class_="price_color").text.strip().replace("Â", "")
            rel = art.h3.a["href"].replace("../../../", "")
            full_url = CATALOGUE_URL + rel
            # detalhes adicionais via scrape_book_details
            details = scrape_book_details(full_url, session)
            books.append({
                "name": name,
                "rate": rate,
                "value": price,
                "url": full_url,
                **details
            })
        page += 1  # passa para a próxima página
    return books


def convert_df_to_csv(df):
    """
    Converte um DataFrame em CSV com delimitador ';' e codificação UTF-8 com BOM.
    Retorna bytes para uso no download_button.
    """
    buf = io.StringIO()
    df.to_csv(buf, index=False, sep=";", encoding="utf-8-sig")
    return buf.getvalue().encode("utf-8-sig")

# ---------- LAYOUT ----------
# Título e instruções iniciais
st.title("📘 Books — Raspagem Completa")
st.write("Clique no botão abaixo para raspar **todas as páginas** (~1.000 livros).")
st.markdown("---")

# Botão para iniciar raspagem completa
if st.button("🚀 Coletar dados"):
    with st.spinner("Raspando todas as páginas... isso pode levar um tempo"):
        st.session_state.books = scrape_all_pages()
    st.success(f"Concluído: {len(st.session_state.books)} livros coletados.")

# Se já coletou livros, exibe filtros e tabela
if st.session_state.get("books"):
    df = pd.DataFrame(st.session_state.books)  # monta DataFrame com os dados

    # Layout de pesquisa e filtros centralizado
    with st.container():
        st.markdown("<div style='display:flex; justify-content:center; gap:16px; margin-bottom:16px;'>", unsafe_allow_html=True)
        # campo de pesquisa por título
        search_query = st.text_input("🔍 Pesquisar livro", key='search', placeholder="Digite o título...")
        # selectbox de ordenação
        sort_option = st.selectbox(
            "🔀 Ordenar por", [
                "Nome (A→Z)", "Nome (Z→A)",
                "Avaliação (Maior→Menor)", "Avaliação (Menor→Maior)",
                "Preço (Maior→Menor)", "Preço (Menor→Maior)",
            ], key='sort'
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # Filtra DataFrame pelo texto digitado
    if search_query:
        df = df[df["name"].str.contains(search_query, case=False, na=False)]

    # Converte rating textual em numérico para ordenar facilmente
    rating_map = {"Zero":0, "One":1, "Two":2, "Three":3, "Four":4, "Five":5}
    df["rate_num"] = df["rate"].map(rating_map)

    # Aplica ordenações conforme opção selecionada
    if sort_option == "Nome (A→Z)":
        df = df.sort_values("name", ascending=True)
    elif sort_option == "Nome (Z→A)":
        df = df.sort_values("name", ascending=False)
    elif sort_option == "Avaliação (Maior→Menor)":
        df = df.sort_values("rate_num", ascending=False)
    elif sort_option == "Avaliação (Menor→Maior)":
        df = df.sort_values("rate_num", ascending=True)
    else:
        df["price_num"] = df["value"].str.replace("£", "").astype(float)
        ascending = sort_option == "Preço (Menor→Maior)"
        df = df.sort_values("price_num", ascending=ascending)

    # Remove colunas auxiliares usadas só para ordenação
    df = df.drop(columns=[c for c in ["rate_num", "price_num"] if c in df.columns])

    # Gera coluna 'Link' com HTML para abrir em nova aba
    df["Link"] = df["url"].apply(lambda u: f'<a href="{u}" target="_blank">Abrir</a>')
    df_display = df.drop(columns=["url"])  # remove coluna de URL bruta

    # CSS minimalista para inputs e tabela
    css = """
    <style>
      /* Remove padding adicional do componente baseweb */
      div[data-baseweb] > div { padding: 0 !important; }
      /* Estiliza caixa de texto e select como balões arredondados */
      .stTextInput>div>div>input, .stSelectbox>div>div>div>select {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 6px 12px;
        width: 200px;
      }
      /* Container scrollável da tabela */
      .table-container {
        overflow-x: auto;
        padding: 4px;
      }
      /* Tabela minimalista */
      table.minimalist {
        border-collapse: collapse;
        width: 100%;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 14px;
      }
      table.minimalist th, table.minimalist td {
        padding: 6px 12px;
        border: 1px solid #e0e0e0;
      }
      table.minimalist thead th {
        background: transparent;
        color: #333;
        font-weight: 600;
      }
      table.minimalist tbody tr:nth-child(even) {
        background: #fafafa;
      }
      table.minimalist tbody tr:hover {
        background: #f5f5f5;
      }
      table.minimalist td a {
        color: #0366d6;
        text-decoration: none;
      }
      table.minimalist td a:hover {
        text-decoration: underline;
      }
    </style>
    """

    html = css + f"""
      <div class="table-container">
        {df_display.to_html(classes="minimalist", escape=False, index=False)}
      </div>
    """
    components.html(html, height=600, scrolling=True)  # renderiza HTML personalizado

    # Botão de download do CSV resultante
    csv = convert_df_to_csv(df)
    st.download_button(
        "📥 Baixar CSV",
        data=csv,
        file_name="books_all_pages.csv",
        mime="text/csv"
    )
else:
    # Mensagem inicial aguardando coleta de dados
    st.info("Clique no botão para iniciar a raspagem completa.")
