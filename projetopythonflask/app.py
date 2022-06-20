from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import random


app = Flask(__name__)

# S_K
app.secret_key = '7911b263612d4cb723a552cec507f5b36d86505c7e711fbaa79fe5c423019628'

#TEMPO DE SESSAO
#app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=5)

# DB
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'jmrpg'

# INICIALIZAR MYSQL
mysql = MySQL(app)

@app.route('/')
def recepcao():
    return 'Olá'


@app.route('/login/', methods=['GET', 'POST'])
def login():
    #session.permanent = True
    msg = ''
    # Verifica se o usuario e senha existe, usuario roda o formulario
    if request.method == 'POST' and 'usuario' in request.form and 'senha' in request.form:
        # Cria variaveis de acesso
        usuario = request.form['usuario']
        senha = request.form['senha']
        # Verifica se conta existe no MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM contas WHERE usuario = %s AND senha = %s', (usuario, senha,))
        # Fetch one para retornar resultado
        contas = cursor.fetchone()
        # Se a conta existir no db
        if contas:
            # Criação da sessão
            session['loggedin'] = True
            session['id'] = contas['id']
            session['usuario'] = contas['usuario']
            # Redireciona pagina
            return redirect(url_for('inicio'))
        else:
            # Caso erro login
            msg = 'Usuário ou Senha Incorreto!'
    return render_template('index.html', msg=msg)

# Script de logout
@app.route('/login/logout')
def logout():
    # Remover Sessão
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('usuario', None)
   # Redireciona pagina
   return redirect(url_for('login'))

# Cadastro
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'usuario' in request.form and 'senha' in request.form and 'email' in request.form:
        #Cria variaveis para acesso
        usuario = request.form['usuario']
        senha = request.form['senha']
        email = request.form['email']
        # Verifica se a conta existe
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM contas WHERE usuario = %s', (usuario,))
        contas = cursor.fetchone()
        # Verifica se existe
        if contas:
            msg = 'Conta já cadastrada!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Email Invalido!'
        elif not re.match(r'[A-Za-z0-9]+', usuario):
            msg = 'Usuario pode conter somente letras e numeros!'
        elif not usuario or not senha or not email:
            msg = 'Preencha os campos!'
        else:
            # Valida e faz a inserção da conta
            cursor.execute('INSERT INTO contas VALUES (NULL, %s, %s, %s)', (usuario, senha, email,))
            mysql.connection.commit()
            msg = 'Conta Cadastrada Com Sucesso!'
    # Mostra MSG Ao completar
    return render_template('register.html', msg=msg)

@app.route('/inicio') # INICIO
def inicio():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM novidades ORDER BY id DESC LIMIT 3")          
        novidades = cursor.fetchall()



        return render_template('inicio.html', usuario=session['usuario'], novidades=novidades)

    return redirect(url_for('login'))

@app.route('/arena') # ARENA
def arena():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM contas WHERE id = %s", (session['id'],))
        contas = cursor.fetchone()



        return render_template('arena.html', contas = contas)
    return redirect(url_for('login'))

@app.route('/personagem') # PERSONAGEM
def personagem():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM contas WHERE id = %s", (session['id'],))
        contas = cursor.fetchone()
        cursor.execute("SELECT * FROM bolsa WHERE id_usuario = %s", (session['id'],))      
        bolsa = cursor.fetchall()
        cursor.execute("SELECT * FROM loja")           
        loja = cursor.fetchall()


        return render_template('personagem.html', contas = contas, bolsa=bolsa, loja=loja)
    return redirect(url_for('login'))


@app.route('/batalhaandamento') # PERSONAGEM
def batalhaandamento():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM contas WHERE id = %s", (session['id'],))
        contas = cursor.fetchone()
        cursor.execute("SELECT * FROM log_monstros WHERE id_usuario = %s", (session['id'],))      
        log_monstros = cursor.fetchall()


        return render_template('./batalha/batalhaandamento.html', contas = contas, log_monstros=log_monstros)
    return redirect(url_for('login'))

@app.route('/arredores') # PERSONAGEM
def arredores():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM contas WHERE id = %s", (session['id'],))
        contas = cursor.fetchone()

        cursor.execute("SELECT * FROM log_monstros WHERE id_usuario = %s", (session['id'],))      
        log_monstros = cursor.fetchall()

        cursor.execute("SELECT * FROM monstros")       
        monstros = cursor.fetchall()


        return render_template('./areas/arredores.html', contas = contas, log_monstros=log_monstros, monstros=monstros)
    return redirect(url_for('login'))

@app.route('/batalhar/<int:item_id>') # USAR ITEM
def batalhar(item_id):
    dialogo = ''
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM monstros ORDER BY id DESC")       
        monstros = cursor.fetchall()

        cursor.execute("SELECT * FROM contas WHERE id = %s", (session['id'],))
        contas = cursor.fetchone()

        area_max = contas['area_max']

        if area_max == 0:
            for m in monstros:
                idmonstro = m['id']
                vida = m['vida']
                nivel = m['nivel']
                nome_monstro = m['nome_monstro']
                recompensa = 0

                if item_id == idmonstro:
                        dialogo = f'Você adicionou o monstro {nome_monstro} ele possui o nivel: {nivel}'
                        area_max += 1
                        cursor.execute(f"UPDATE contas SET area_max = {area_max}  WHERE id = %s", (session['id'],))
                        mysql.connection.commit()
                        cursor.execute('INSERT INTO log_monstros VALUES (NULL, %s, %s, %s, %s)', (session['id'], nome_monstro, vida, recompensa,))
                        mysql.connection.commit()
        else:
            dialogo = f'Há uma batalha em andamento.'  
                      
        return render_template('./batalha/batalhar.html', dialogo=dialogo, contas=contas)
    return redirect(url_for('login'))


@app.route('/atacar/<int:item_id>')
def atacar(item_id):
    dialogo = f''
    dialogo2 = f''
    dialogo3 = f''
    botao = f'button onClick=window.location.reload()'
    botao2 = f'Atacar'
    botao3 = f'/button'
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM log_monstros")    
        log_monstros = cursor.fetchall()
        cursor.execute("SELECT * FROM monstros")       
        monstros = cursor.fetchall()

        cursor.execute("SELECT * FROM contas WHERE id = %s", (session['id'],))
        contas = cursor.fetchone()

        area_max = contas['area_max']
        energia = contas['energia']
        exp = contas['exp']
        prata = contas['total_prata']

        ataque = contas['ataque']
        vida_jogador = contas['vida']
        

        
        for m in log_monstros:
            idmonstro = m['id']
            vida = m['vida']
            nome_monstro = m['nome_monstro']
            recompensa = m['recompensa']
            #PRECISA SALVAR NO LOG AS RECOMPENSAS.

            if area_max == 1 and recompensa == 0:
                

                for m in monstros:
                    dano_rate = random.randrange(m['dano_min'], m['dano_max'])
                    exp_rate = random.randrange(m['exp_min'], m['exp_max'])
                    prata_rate = random.randrange(m['prata_min'], m['prata_max'])
                    def_rate = random.randrange(m['def_min'], m['def_max'])
                    energia -= 1
                    xp = exp + exp_rate
                    total_prata = prata + prata_rate

                    if item_id == idmonstro and vida >= 1:
                        dialogo = f'Nome: {nome_monstro} Vida: {vida} e dano {dano_rate}'
                        dialogo2 = f'Seu dano {ataque} e possui Vida: {vida_jogador}'
                        dialogo3 = f"img src=../static/img/monstros/{nome_monstro}.gif height=64px width=64px"
                        dano_recebido = vida_jogador - dano_rate
                        cursor.execute(f"UPDATE contas SET vida = {dano_recebido}  WHERE id = %s", (session['id'],))
                        mysql.connection.commit()
                        dano_ataque = vida - ataque
                        cursor.execute(f"UPDATE log_monstros SET vida = {dano_ataque}  WHERE id_usuario = %s", (session['id'],))
                        mysql.connection.commit()

                    elif vida <= 0: 
                        cursor.execute(f"UPDATE log_monstros SET vida = {0}, recompensa = {1}  WHERE id_usuario = %s", (session['id'],))
                        cursor.execute(f"UPDATE contas SET area_max = {0}  WHERE id = %s", (session['id'],))
                        mysql.connection.commit()
                        return redirect(url_for('batalhaandamento'))  

            else:
                dialogo = f'Recebeu recompensa XP:  - Prata '
                dialogo2 = 'XP'
                dialogo3 = 'XP'
                botao = 'XP'
                botao2 = 'XP'
                botao3 = 'XP'
                '''print(xp) #PRECISA TERMINAR
                cursor.execute(f"UPDATE contas SET exp = {xp}, total_prata = {total_prata}, energia = {energia} WHERE id = %s", (session['id'],))
                '''
                cursor.execute(f"DELETE FROM log_monstros WHERE id_usuario = %s", (session['id'],))
                mysql.connection.commit()
                      
        return render_template('./batalha/batalhou.html', dialogo=dialogo, dialogo2=dialogo2, dialogo3=dialogo3, contas=contas, botao=botao, botao2=botao2, botao3=botao3)
    return redirect(url_for('login'))

@app.route('/loja') # LOJAS 0 - Ouro, 1 - Comerciante, 2 - Ferreiro/Forja
def loja():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM contas WHERE id = %s", (session['id'],))
        contas = cursor.fetchone()
        cursor.execute("SELECT * FROM loja")       
        loja = cursor.fetchall()


        return render_template('./loja/comprar/loja.html', loja=loja, contas=contas)
    return redirect(url_for('login'))

@app.route('/loja/comerciante') # LOJAS 0 - Ouro, 1 - Comerciante, 2 - Ferreiro/Forja
def lojacomerciante():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM contas WHERE id = %s", (session['id'],))
        contas = cursor.fetchone()
        cursor.execute("SELECT * FROM loja")       
        loja = cursor.fetchall()


        return render_template('./loja/comprar/comerciante.html', loja=loja, contas=contas)
    return redirect(url_for('login'))

@app.route('/loja/ferreiro') # LOJAS 0 - Ouro, 1 - Comerciante, 2 - Ferreiro/Forja
def lojaferreiro():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM contas WHERE id = %s", (session['id'],))
        contas = cursor.fetchone()
        cursor.execute("SELECT * FROM loja")       
        loja = cursor.fetchall()


        return render_template('./loja/comprar/ferreiro.html', loja=loja, contas=contas)
    return redirect(url_for('login'))

@app.route('/loja/taverna') # LOJAS 0 - Ouro, 1 - Comerciante, 2 - Ferreiro/Forja
def lojataverna():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM contas WHERE id = %s", (session['id'],))
        contas = cursor.fetchone()
        cursor.execute("SELECT * FROM loja")       
        loja = cursor.fetchall()


        return render_template('./loja/comprar/taverna.html', loja=loja, contas=contas)
    return redirect(url_for('login'))

@app.route('/addvida')
def addvida():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM contas WHERE id = %s", (session['id'],))
        contas = cursor.fetchone()

        total_pontos = contas['total_pontos']
        vida = contas['vida']
        vida_max = contas['vida_max']
        total = 998

        if total_pontos > 0 and vida_max <= total:
            dialogo = 'Ponto atribuido!'
            total_pontos -= 1
            vida_max += 1
            vida = vida_max
            cursor.execute(f"UPDATE contas SET vida = {vida}, vida_max = {vida_max}, total_pontos = {total_pontos}  WHERE id = %s", (session['id'],))
            mysql.connection.commit()
        elif vida_max >= total:
            dialogo = 'Vida já está no máximo!'
        else:
            dialogo = 'Nenhum ponto para atribuir'

        return render_template('./loja/dialogs/add.html', contas=contas, dialogo=dialogo)
    return redirect(url_for('login'))

@app.route('/addener')
def addener():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM contas WHERE id = %s", (session['id'],))
        contas = cursor.fetchone()

        total_pontos = contas['total_pontos']
        energia = contas['energia']
        energia_max = contas['energia_max']
        total = 998

        if total_pontos > 0 and energia_max <= total:
            dialogo = 'Ponto atribuido!'
            total_pontos -= 1
            energia_max += 1
            energia = energia_max
            cursor.execute(f"UPDATE contas SET energia = {energia}, energia_max = {energia_max}, total_pontos = {total_pontos}  WHERE id = %s", (session['id'],))
            mysql.connection.commit()
        elif energia_max >= total:
            dialogo = 'Energia já está no máximo!'
        else:
            dialogo = 'Nenhum ponto para atribuir'

        return render_template('./loja/dialogs/add.html', contas=contas, dialogo=dialogo)
    return redirect(url_for('login'))


@app.route('/addataque')
def addataque():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM contas WHERE id = %s", (session['id'],))
        contas = cursor.fetchone()

        total_pontos = contas['total_pontos']
        ataque = contas['ataque']
        total = 98

        if total_pontos > 0 and ataque <= total:
            dialogo = 'Ponto atribuido!'
            total_pontos -= 1
            ataque += 1
            cursor.execute(f"UPDATE contas SET ataque = {ataque}, total_pontos = {total_pontos}  WHERE id = %s", (session['id'],))
            mysql.connection.commit()
        elif ataque >= total:
            dialogo = 'Ataque já está no máximo!'
        else:
            dialogo = 'Nenhum ponto para atribuir'

        return render_template('./loja/dialogs/add.html', contas=contas, dialogo=dialogo)
    return redirect(url_for('login'))

@app.route('/adddefesa')
def adddefesa():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM contas WHERE id = %s", (session['id'],))
        contas = cursor.fetchone()

        total_pontos = contas['total_pontos']
        defesa = contas['defesa']
        total = 98

        if total_pontos > 0 and defesa <= total:
            dialogo = 'Ponto atribuido!'
            total_pontos -= 1
            defesa += 1
            cursor.execute(f"UPDATE contas SET defesa = {defesa}, total_pontos = {total_pontos}  WHERE id = %s", (session['id'],))
            mysql.connection.commit()
        elif defesa >= total:
            dialogo = 'Defesa já está no máximo!'
        else:
            dialogo = 'Nenhum ponto para atribuir'

        return render_template('./loja/dialogs/add.html', contas=contas, dialogo=dialogo)
    return redirect(url_for('login'))

@app.route('/comprou/<int:item_id>') # COMPRAR ITEM
def comprou(item_id):
    dialogo = ''
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM loja ORDER BY id DESC")       
        loja = cursor.fetchall()
        cursor.execute("SELECT * FROM contas WHERE id = %s", (session['id'],))
        contas = cursor.fetchone()
        cursor.execute("SELECT * FROM bolsa")       
        bolsa = cursor.fetchall()

        min_bolsa = contas['min_bolsa']
        max_bolsa = contas['max_bolsa']
        moedas = contas['total_prata']


        if min_bolsa <= max_bolsa:
            for i in loja:
                preco = i['preco']
                produto = i['produto']
                desc = i['desc']
                bonus_ataque = i['bonus_ataque']
                bonus_defesa = i['bonus_defesa']
                
                if item_id == i['id'] and moedas >= preco:
                        dialogo = f'Você comprou item {produto} e pagou {preco} prata'
                        min_bolsa += 1
                        moedas -= preco
                        cursor.execute(f"UPDATE contas SET total_prata = {moedas}, min_bolsa = {min_bolsa}  WHERE id = %s", (session['id'],))
                        mysql.connection.commit()
                        cursor.execute('INSERT INTO bolsa VALUES (NULL, %s, %s, %s, %s, %s)', (session['id'], produto, desc, bonus_ataque, bonus_defesa,))
                        mysql.connection.commit()
                        
                elif moedas < preco:
                    dialogo = 'Não possui prata suficiente'
        else:
            print('Cheio')
            dialogo = f'Bolsa max. {max_bolsa}, não foi possivel completar a compra.'  

        return render_template('./loja/dialogs/comprou.html', dialogo=dialogo, loja=loja)
    return redirect(url_for('login'))

@app.route('/usar/<int:item_id>') # USAR ITEM
def usar(item_id):
    dialogo = ''
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM loja ORDER BY id DESC")       
        loja = cursor.fetchall()
        cursor.execute("SELECT * FROM contas WHERE id = %s", (session['id'],))
        contas = cursor.fetchone()
        cursor.execute("SELECT * FROM bolsa")       
        bolsa = cursor.fetchall()

        capacete_eqp = contas['capacete_eqp']
        peitoral_eqp = contas['peitoral_eqp']
        calca_eqp = contas['calca_eqp']
        botas_eqp = contas['botas_eqp']
        arma_eqp = contas['arma_eqp']
        
        vazio = 'vazio'

        for itens in bolsa:
            produto = itens['nome_item']
            
            for i in loja:
                tipo = i['tipo']
                item = i['produto']
                addataque = contas['b_ataque'] + i['bonus_ataque']
                adddefesa = contas['b_defesa'] + i['bonus_defesa']
                # tipo 1 - capacete, tipo 2 - peitoral, tipo 3 - calça, tipo 4 - botas, tipo 5 - arma, tipo 6/7/8 - magia1,2,3, tipo 9 - mascote, tipo 10 - montaria
                if capacete_eqp == vazio:
                    if item_id == itens['id'] and item == produto and tipo == 1:
                        dialogo = f'item equipado.'
                        cursor.execute(f"UPDATE contas SET capacete_eqp = REPLACE(capacete_eqp, capacete_eqp, '{produto}'), b_defesa = {adddefesa} WHERE id = {'%s'}", (session['id'],))
                        mysql.connection.commit()
                else:
                    dialogo = f'item equipado.'

                if peitoral_eqp == vazio:
                    if item_id == itens['id'] and item == produto and tipo == 2:
                        dialogo = f'item equipado.'
                        cursor.execute(f"UPDATE contas SET peitoral_eqp = REPLACE(peitoral_eqp, peitoral_eqp, '{produto}'), b_defesa = {adddefesa} WHERE id = {'%s'}", (session['id'],))
                        mysql.connection.commit()
                else:
                    dialogo = f'item equipado.'

                if calca_eqp == vazio:
                    if item_id == itens['id'] and item == produto and tipo == 3:
                        dialogo = f'item equipado.'
                        cursor.execute(f"UPDATE contas SET calca_eqp = REPLACE(calca_eqp, calca_eqp, '{produto}'), b_defesa = {adddefesa} WHERE id = {'%s'}", (session['id'],))
                        mysql.connection.commit()
                else:
                    dialogo = f'item equipado.'

                if botas_eqp == vazio:
                    if item_id == itens['id'] and item == produto and tipo == 4:
                        dialogo = f'item equipado.'
                        cursor.execute(f"UPDATE contas SET botas_eqp = REPLACE(botas_eqp, botas_eqp, '{produto}'), b_defesa = {adddefesa} WHERE id = {'%s'}", (session['id'],))
                        mysql.connection.commit()
                else:
                    dialogo = f'item equipado.'
                
                if arma_eqp == vazio:
                    if item_id == itens['id'] and item == produto and tipo == 5:
                        dialogo = f'item equipado.'
                        cursor.execute(f"UPDATE contas SET arma_eqp = REPLACE(arma_eqp, arma_eqp, '{produto}'), b_ataque = {addataque} WHERE id = {'%s'}", (session['id'],))
                        mysql.connection.commit()
                else:
                    dialogo = f'item equipado.'
                        
        return render_template('./loja/dialogs/usou.html', dialogo=dialogo, loja=loja, contas=contas, bolsa=bolsa)
    return redirect(url_for('login'))

@app.route('/remover/<int:item_id>') # REMOVER ITEM
def remover(item_id):
    dialogo = ''
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM loja ORDER BY id DESC")       
        loja = cursor.fetchall()
        cursor.execute("SELECT * FROM contas WHERE id = %s", (session['id'],))
        contas = cursor.fetchone()
        cursor.execute("SELECT * FROM bolsa")       
        bolsa = cursor.fetchall()

        capacete_eqp = contas['capacete_eqp']
        peitoral_eqp = contas['peitoral_eqp']
        calca_eqp = contas['calca_eqp']
        botas_eqp = contas['botas_eqp']
        arma_eqp = contas['arma_eqp']
        
        vazio = 'vazio'

        for itens in bolsa:
            produto = itens['nome_item']
            
            for i in loja:
                tipo = i['tipo']
                item = i['produto']
                rmataque = contas['b_ataque'] - i['bonus_ataque']
                rmdefesa = contas['b_defesa'] - i['bonus_defesa']
                # tipo 1 - capacete, tipo 2 - peitoral, tipo 3 - calça, tipo 4 - botas, tipo 5 - arma, tipo 6/7/8 - magia1,2,3, tipo 9 - mascote, tipo 10 - montaria
                if capacete_eqp == produto:
                    if item_id == itens['id'] and item == produto and tipo == 1:
                        dialogo = f'item removido.'
                        cursor.execute(f"UPDATE contas SET capacete_eqp = REPLACE(capacete_eqp, capacete_eqp, '{vazio}'), b_defesa = {rmdefesa} WHERE id = {'%s'}", (session['id'],))
                        mysql.connection.commit()
                else:
                    dialogo = f'item removido.'

                if peitoral_eqp == produto:
                    if item_id == itens['id'] and item == produto and tipo == 2:
                        dialogo = f'item removido.'
                        cursor.execute(f"UPDATE contas SET peitoral_eqp = REPLACE(peitoral_eqp, peitoral_eqp, '{vazio}'), b_defesa = {rmdefesa} WHERE id = {'%s'}", (session['id'],))
                        mysql.connection.commit()
                else:
                    dialogo = f'item removido.'

                if calca_eqp == produto:
                    if item_id == itens['id'] and item == produto and tipo == 3:
                        dialogo = f'item removido.'
                        cursor.execute(f"UPDATE contas SET calca_eqp = REPLACE(calca_eqp, calca_eqp, '{vazio}'), b_defesa = {rmdefesa} WHERE id = {'%s'}", (session['id'],))
                        mysql.connection.commit()
                else:
                    dialogo = f'item removido.'

                if botas_eqp == produto:
                    if item_id == itens['id'] and item == produto and tipo == 4:
                        dialogo = f'item removido.'
                        cursor.execute(f"UPDATE contas SET botas_eqp = REPLACE(botas_eqp, botas_eqp, '{vazio}'), b_defesa = {rmdefesa} WHERE id = {'%s'}", (session['id'],))
                        mysql.connection.commit()
                else:
                    dialogo = f'item removido.'
                
                if arma_eqp == produto:
                    if item_id == itens['id'] and item == produto and tipo == 5:
                        dialogo = f'item removido.'
                        cursor.execute(f"UPDATE contas SET arma_eqp = REPLACE(arma_eqp, arma_eqp, '{vazio}'), b_ataque = {rmataque} WHERE id = {'%s'}", (session['id'],))
                        mysql.connection.commit()
                else:
                    dialogo = f'item removido.'
                        
        return render_template('./loja/dialogs/removeu.html', dialogo=dialogo, loja=loja, contas=contas, bolsa=bolsa)
    return redirect(url_for('login'))

@app.route('/padmin') # PAINEL ADMINISTRATIVO PARA CARGO ADMIN
def padmin():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM contas WHERE id = %s", (session['id'],))
        contas = cursor.fetchone()

        acesso = contas['acesso']

        if acesso == 1:
            print('tem acesso admin')
            msg = 'BEM VINDO ADMIN'
        else:
            return redirect(url_for('inicio'))


        return render_template('./admin/padmin.html', msg=msg)
    return redirect(url_for('login'))

@app.route('/mapa')
def mapa():
    if 'loggedin' in session:
        return render_template('mapa.html',)
    return redirect(url_for('login'))

@app.route('/masmorras')
def masmorras():
    msgbox5 = f""
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM contas WHERE id = %s", (session['id'],))
        contas = cursor.fetchone()
        cursor.execute("SELECT * FROM monstros ORDER BY RAND() LIMIT 1")       
        monstros = cursor.fetchall()

        for monstro in monstros:
            msgbox5 = f"img src=../static/img/monstros/{monstro['nome_monstro']}.gif height=64px width=64px"

        return render_template('./areas/masmorras.html', contas=contas, monstros=monstros, msgbox5=msgbox5)
    return redirect(url_for('login'))

@app.errorhandler(404)
def notfound(erro):
    return render_template('pagina_404.html'), 404 

# Deploy
if __name__ == '__main__':
    app.run(debug=True)

