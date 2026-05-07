import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from dotenv import load_dotenv
from supabase import create_client, Client
from google import genai

load_dotenv()

app = Flask(__name__)
app.secret_key = "chave_fixa_para_nao_cair_sessao"

url_banco = os.getenv("SUPABASE_URL")
chave_banco = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url_banco, chave_banco)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- FUNÇÃO DA NUTRI ---
def chamar_gemini_nutri(pergunta):
    try:
        email = session.get('user_email')
        if not email:
            return "ERRO DE SESSÃO: Faça login novamente."
            
        resposta_db = supabase.table('alunos').select("*").eq('email', email).execute()
        if not resposta_db.data:
            return "ERRO DE BANCO: Aluno não encontrado."
            
        dados_aluno = resposta_db.data[0]
        
        prompt_sistema = f"""
        Você é um nutricionista esportivo atuando como inteligência artificial.
        Sua tarefa é personalizar 100% a resposta com base no perfil físico e objetivo deste aluno específico.
        
        Perfil do Aluno:
        - Idade: {dados_aluno.get('idade')} anos
        - Peso: {dados_aluno.get('peso')} kg
        - Altura: {dados_aluno.get('altura')} m
        - Objetivo Principal: {dados_aluno.get('objetivo_principal')}
        - Ambiente de Treino: {dados_aluno.get('ambiente_treino')}
        - Experiência: {dados_aluno.get('nivel_experiencia')}
        
        Instrução de Comportamento:
        Adapte o seu tom de voz para o estilo escolhido pelo aluno: {dados_aluno.get('estilo_treinador')}.
        Calcule estimativas de macros e sugira alimentos focados exclusivamente no objetivo listado acima.
        
        Pergunta do aluno: {pergunta}
        """
        
        resposta = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_sistema
        )
        
        return resposta.text
    except Exception as e:
        return f"ERRO NO PYTHON: {str(e)}"

# --- ROTAS DE AUTENTICAÇÃO E CADASTRO ---
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        resposta = supabase.table('alunos').select("*").eq('email', email).execute()
        
        if not resposta.data:
            flash("E-mail não cadastrado! Crie uma conta abaixo.", "error")
            return redirect(url_for('login'))
            
        usuario = resposta.data[0]
        
        if usuario['senha_hash'] == senha:
            session['user_email'] = usuario['email']
            return redirect(url_for('dashboard'))
        else:
            flash("Senha incorreta. Tente novamente.", "error")
            return redirect(url_for('login'))
            
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
            return redirect(url_for('login'))
        except Exception as e:
            return f"Erro ao salvar: {e}"
            
    return render_template('cadastro_vibe.html')

@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# --- ROTAS DA IA NUTRI ---
@app.route('/nutri')
def nutri():
    if 'user_email' not in session:
        return redirect(url_for('login'))
        
    user_data = supabase.table('alunos').select("*").eq('email', session['user_email']).execute()
    return render_template('nutri.html', aluno=user_data.data[0])

@app.route('/nutri/pergunta', methods=['POST'])
def perguntar_nutri():
    pergunta = request.form.get('pergunta')
    resposta = chamar_gemini_nutri(pergunta) 
    return jsonify({"resposta": resposta})

@app.route('/nutri/salvar', methods=['POST'])
def salvar_nutri():
    conteudo = request.form.get('conteudo')
    email = session.get('user_email')
    
    supabase.table('historico_nutri').insert({
        "aluno_email": email,
        "conteudo": conteudo
    }).execute()
    
    return "OK", 200

@app.route('/historico_nutri')
def historico_nutri():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    email = session.get('user_email')
    resposta = supabase.table('historico_nutri').select("*").eq('aluno_email', email).order('created_at', desc=True).execute()
    
    return render_template('historico_nutri.html', historico=resposta.data)

# --- ROTAS DO COACH IA ---
@app.route('/treinador')
def treinador():
    if 'user_email' not in session: return redirect(url_for('login'))
    return render_template('treinador.html')

@app.route('/treinador/gerar', methods=['POST'])
def gerar_treino():
    pergunta = request.form.get('pergunta')
    email = session.get('user_email')
    
    res = supabase.table('alunos').select("*").eq('email', email).execute()
    aluno = res.data[0]
    
    prompt = f"""
    Você é um Personal Trainer de elite. Gere um treino focado para:
    Aluno: {aluno['objetivo_principal']} | Nível: {aluno['nivel_experiencia']}
    Local: {aluno['ambiente_treino']}
    Estilo de resposta: {aluno['estilo_treinador']}
    
    Pedido específico: {pergunta}
    
    Retorne o treino com nomes de exercícios, séries e repetições de forma organizada.
    """
    
    try:
        resposta = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return jsonify({"resposta": resposta.text})
    except Exception as e:
        return jsonify({"resposta": f"ERRO DA IA: {str(e)}"})

@app.route('/treino/salvar', methods=['POST'])
def salvar_treino():
    conteudo = request.form.get('conteudo')
    email = session.get('user_email')
    
    supabase.table('treinos').insert({
        "aluno_email": email,
        "conteudo": conteudo,
        "tipo": "Gerado pela IA"
    }).execute()
    
    return "OK", 200

@app.route('/historico')
def historico():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    email = session.get('user_email')
    resposta = supabase.table('treinos').select("*").eq('aluno_email', email).order('created_at', desc=True).execute()
    
    return render_template('historico.html', treinos=resposta.data)

if __name__ == '__main__':
    app.run(debug=True)