import os
from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

url_banco = os.getenv("SUPABASE_URL")
chave_banco = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url_banco, chave_banco)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('cadastro_bio'))
    return render_template('login.html')

@app.route('/cadastro/bio', methods=['GET', 'POST'])
def cadastro_bio():
    if request.method == 'POST':
        session['email'] = request.form.get('email')
        session['senha'] = request.form.get('senha')
        session['idade'] = request.form.get('idade')
        return redirect(url_for('cadastro_objetivo'))
    return render_template('cadastro_bio.html')

@app.route('/cadastro/objetivo', methods=['GET', 'POST'])
def cadastro_objetivo():
    if request.method == 'POST':
        session['peso'] = request.form.get('peso')
        session['altura'] = request.form.get('altura')
        session['objetivo'] = request.form.get('objetivo')
        return redirect(url_for('cadastro_vibe'))
    return render_template('cadastro_objetivo.html')

@app.route('/cadastro/vibe', methods=['GET', 'POST'])
def cadastro_vibe():
    if request.method == 'POST':
        ambiente = request.form.get('ambiente')
        estilo = request.form.get('estilo')
        
        dados_aluno = {
            "email": session.get('email'),
            "senha_hash": session.get('senha'),
            "idade": int(session.get('idade', 0)),
            "peso": float(session.get('peso', 0).replace(',', '.')),
            "altura": float(session.get('altura', 0).replace(',', '.')),
            "objetivo_principal": session.get('objetivo'),
            "ambiente_treino": ambiente,
            "estilo_treinador": estilo,
            "nivel_experiencia": "Iniciante"
        }
        
        try:
            supabase.table('alunos').insert(dados_aluno).execute()
            session.clear()
            return "Cadastro realizado com sucesso no banco!"
        except Exception as e:
            return f"Erro ao salvar: {e}"
            
    return render_template('cadastro_vibe.html')

if __name__ == '__main__':
    app.run(debug=True)