from flask import Blueprint, render_template, request, redirect, url_for, current_app , flash , abort
from flask_login import login_required, current_user
from app.models import db, Product , Order
import os
from werkzeug.utils import secure_filename

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.route("/dashboard")
@login_required
def dashboard():
    if not current_user.is_admin:
        abort(403)

    from app.models import User, Order

    page = request.args.get("page", 1, type=int)

    total_usuarios = User.query.count()
    total_produtos = Product.query.count()
    total_pedidos = Order.query.count()

    pedidos = Order.query.limit(5).all()
    total_arrecadado = sum(p.total for p in pedidos) if pedidos else 0


    produtos = Product.query.paginate(page=page, per_page=5)

    return render_template(
        "admin_dashboard.html",
        total_usuarios=total_usuarios,
        total_produtos=total_produtos,
        total_pedidos=total_pedidos,
        total_arrecadado=total_arrecadado,
        pedidos=pedidos,
        produtos=produtos
    )

@admin.route("/produtos/novo", methods=["GET", "POST"])
@login_required
def novo_produto():
    if not current_user.is_admin:
        return "Acesso negado", 403

    if request.method == "POST":
        nome = request.form.get("nome")
        descricao = request.form.get("descricao")
        preco = request.form.get("preco")
        estoque = request.form.get("estoque")

        imagem_file = request.files.get("imagem")

        nome_arquivo = None

        if imagem_file:
            nome_arquivo = secure_filename(imagem_file.filename)

            caminho = os.path.join(
                current_app.root_path,
                "static/uploads",
                nome_arquivo
            )

            imagem_file.save(caminho)

        produto = Product(
            nome=nome,
            descricao=descricao,
            preco=float(preco),
            imagem=nome_arquivo,
            estoque=int(estoque) if estoque else 0
        )

        db.session.add(produto)
        db.session.commit()


        return redirect(url_for("admin.dashboard"))

    return render_template("admin/novo_produto.html")


@admin.route("/produto/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar_produto(id):
    if not current_user.is_admin:
        abort(403)

    produto = Product.query.get_or_404(id)

    if request.method == "POST":
        produto.nome = request.form.get("nome")
        produto.preco = request.form.get("preco")
        produto.descricao = request.form.get("descricao")

        imagem = request.files.get("imagem")

        if imagem and imagem.filename != "":
            nome_arquivo = secure_filename(imagem.filename)
            caminho = os.path.join(current_app.root_path, "static/uploads", nome_arquivo)
            imagem.save(caminho)
            produto.imagem = nome_arquivo

        db.session.commit()
        flash("Produto atualizado com sucesso!", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/editar_produto.html", produto=produto)

@admin.route("/produto/<int:id>/excluir", methods=["POST"])
@login_required
def excluir_produto(id):
    if not current_user.is_admin:
        abort(403)

    produto = Product.query.get_or_404(id)

    # Opcional: remover imagem do servidor
    if produto.imagem:
        caminho = os.path.join(current_app.root_path, "static/uploads", produto.imagem)
        if os.path.exists(caminho):
            os.remove(caminho)

    db.session.delete(produto)
    db.session.commit()

    flash("Produto excluído com sucesso!", "success")
    return redirect(url_for("admin.dashboard"))

@admin.route('/pedido/<int:pedido_id>/alterar-status', methods=['POST'])
@login_required
def alterar_status_pedido(pedido_id):
    if not current_user.is_admin:
        return "Acesso negado", 403

    pedido = Order.query.get_or_404(pedido_id)

    novo_status = request.form.get("status")
    pedido.status = novo_status

    db.session.commit()

    return redirect(url_for('admin.dashboard'))