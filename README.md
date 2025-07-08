# 📘 Books Streamer - Raspagem de Livros

Este projeto consiste em um script Python que realiza web scraping do site "books.toscrape.com" para coletar informações sobre livros. Os dados coletados são exibidos em uma interface web interativa criada com Streamlit, permitindo ao usuário pesquisar, ordenar e baixar os dados em formato CSV.

## Funcionalidades

*   Raspagem de todos os livros listados no site (aproximadamente 1.000 livros).
*   Extração de detalhes como título, avaliação (estrelas), preço, UPC, disponibilidade, etc.
*   Interface web para visualização dos dados.
*   Pesquisa de livros por título.
*   Ordenação dos livros por nome, avaliação ou preço.
*   Download dos dados coletados em um arquivo CSV.

## Pré-requisitos

*   Python 3.7+

## Configuração do Ambiente

1.  **Clone o repositório (ou baixe os arquivos):**
    ```bash
    # Se estiver usando Git
    git clone <url-do-repositorio>
    cd <nome-do-repositorio>
    ```

2.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    python -m venv venv
    ```
    *   No Windows:
        ```bash
        venv\\Scripts\\activate
        ```
    *   No macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

## Como Executar

Após a configuração do ambiente e instalação das dependências, execute o script Streamlit:

```bash
streamlit run main.py
```

Isso deverá abrir a aplicação no seu navegador padrão.

## Estrutura do Código

*   `main.py`: Script principal contendo a lógica de raspagem, as funções de processamento de dados e a interface Streamlit.
*   `requirements.txt`: Lista das bibliotecas Python necessárias para o projeto.
*   `.gitignore`: Especifica arquivos e pastas a serem ignorados pelo Git.
*   `README.md`: Este arquivo, fornecendo informações sobre o projeto.

## Bibliotecas Utilizadas

*   [Streamlit](https://streamlit.io/): Para a criação da interface web interativa.
*   [Requests](https://requests.readthedocs.io/): Para realizar requisições HTTP.
*   [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/): Para fazer o parsing do HTML.
*   [Pandas](https://pandas.pydata.org/): Para manipulação e estruturação dos dados.
