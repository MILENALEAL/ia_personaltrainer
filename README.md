# Coach.IA (sim, ainda tenho que pensar em um nome melhor)🦾

Um web app inteligente de acompanhamento fitness e nutricional. O sistema utiliza a API do Google Gemini para atuar como um Personal Trainer e Nutricionista, gerando treinos e conselhos alimentares 100% personalizados com base na biometria, objetivo e ambiente de treino do usuário.

## - Funcionalidades

* **Autenticação:** Sistema de login e cadastro integrado ao Supabase.
* **Perfil do Aluno:** Coleta de dados físicos (peso, altura, idade), nível de experiência e estilo do treinador desejado.
* **Coach IA:** Geração de treinos dinâmicos usando o Gemini 2.5 Flash, adaptados para casa ou academia.
* **Nutri IA:** Chatbot nutricional com foco em emagrecimento, hipertrofia ou manutenção.
* **Histórico:** Salvamento automático de treinos e dicas da Nutri no banco de dados para consulta futura.
* **UI/UX:** Interface "Dark & Red" responsiva e minimalista.

## - Tecnologias Utilizadas

* **Back-end:** Python, Flask
* **Banco de Dados:** Supabase (PostgreSQL)
* **Inteligência Artificial:** Google GenAI SDK (Gemini 2.5 Flash)
* **Front-end:** HTML5, CSS3, JavaScript (Vanilla)

## - Como rodar o projeto localmente

1. Clone este repositório:
   ```bash
   git clone https://github.com/MILENALEAL/ia_personaltrainer.git

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   # No Windows:
   venv\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install flask python-dotenv supabase google-genai
   ```

4. Crie um arquivo `.env` na raiz do projeto com as suas chaves:
   ```text
   SUPABASE_URL=sua_url_do_supabase
   SUPABASE_KEY=sua_chave_do_supabase
   GEMINI_API_KEY=sua_chave_do_google_ai_studio
   ```

5. Inicie o servidor:
   ```bash
   python app.py
   ```

---
Desenvolvido por **Milena Leal** • Versão 1.0
