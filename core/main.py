from flask import jsonify
from flask_jwt_extended import jwt_required, unset_jwt_cookies

from .db_setup import init_db
from . import app
from .common.auth import get_identity, view_require_permission
from .models.users.routes import users_bp
from .models.roles.routes import roles_bp
from .models.products.routes import products_bp
from .models.permissions.routes import permissions_bp
from .models.sales.routes import sales_bp

DATABASE = app.config["DATABASE_URL"]
init_db()

app.register_blueprint(users_bp)
app.register_blueprint(roles_bp)
app.register_blueprint(permissions_bp)
app.register_blueprint(products_bp)
app.register_blueprint(sales_bp)

@app.route('/')
def home():
    return """
    <h1>Bem vindo a API de Overflow Lanches</h1>
    <p>Esta API permite que você execute operações CRUD (Create, Read, Update, Delete) em uma base de dados SQLite.</p>
    <p>Rotas protegidas estão representadas com (#) no método</p>
    <p>Rotas disponíveis:</p>
    <ul>
        <li>POST /login - Retorna o JWT de autenticação. Envie um JSON com "username" e "password" referente a seu usuário</li>
        <li>GET /hello - Interpreta as credenciais do JWT para identificar a identidade do cliente na requisição.</li>
        <li>GET(#) /users  - Consulta todos os usuários cadastrados.</li>
        <li>POST(#) /users - Registra um usuário no sistema. Envie um JSON com "username" e "password" para as credenciais e adicione o 
        valor 1 ao campo "is_admin" se quiser criar um super usuário (solução provisória)</li>
        <li>PUT(#) /users - Altera a senha de um usuário. Envie um JSON com "username" e "password" para realizar alteração (essa medida
        é provisória)</li>
    </ul>
    """


@app.route("/me", methods=["GET"]) 
@jwt_required() 
def me(): 
    user = get_identity()
    return jsonify({"username": user["username"]})

@app.route("/validate", methods=["GET"])
@jwt_required()
@view_require_permission()
def validate():
    return jsonify({"message:" : "aprovado"}, 200)

@app.route("/logout", methods=["POST"]) 
def logout(): 
    resp = jsonify({"message": "logout realizado"}) 
    unset_jwt_cookies(resp)
    return resp

if __name__ == "__main__":
    app.run()