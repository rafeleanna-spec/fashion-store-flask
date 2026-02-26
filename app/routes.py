from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import db, Product, Cart, CartItem, Order , User

main = Blueprint('main', __name__)

# ======================
# PÁGINA INICIAL
# ======================

@main.route('/')
def index():
    return render_template('index.html')


# ======================
# LISTAR PRODUTOS
# ======================

@main.route("/produtos")
def produtos():
    page = request.args.get("page", 1, type=int)
    busca = request.args.get("q", "")
    categoria = request.args.get("categoria", "")

    consulta = Product.query

    # 🔎 Filtro por nome
    if busca:
        consulta = consulta.filter(Product.nome.ilike(f"%{busca}%"))

    # 🏷 Filtro por categoria
    if categoria:
        consulta = consulta.filter(Product.categoria == categoria)

    produtos = consulta.paginate(page=page, per_page=6)

    # Lista de categorias únicas para mostrar no select
    categorias = db.session.query(Product.categoria).distinct().all()
    categorias = [c[0] for c in categorias]

    return render_template(
        "produtos.html",
        produtos=produtos,
        busca=busca,
        categoria_selecionada=categoria,
        categorias=categorias
    )

# ======================
# ADICIONAR AO CARRINHO
# ======================
@main.route('/add_to_cart/<int:product_id>')
@login_required
def add_to_cart(product_id):

    product = Product.query.get_or_404(product_id)

    if product.estoque <= 0:
        return redirect(url_for('main.produtos'))

    # Buscar carrinho do usuário
    cart = Cart.query.filter_by(user_id=current_user.id).first()

    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()

    # Buscar item pelo cart_id (NÃO user_id)
    cart_item = CartItem.query.filter_by(
        cart_id=cart.id,
        product_id=product_id
    ).first()

    if cart_item:
        if cart_item.quantidade + 1 > product.estoque:
            return redirect(url_for('main.cart'))

        cart_item.quantidade += 1
    else:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantidade=1
        )
        db.session.add(cart_item)

    db.session.commit()

    return redirect(url_for('main.cart'))
# ======================
# VER CARRINHO
# ======================

@main.route('/cart')
@login_required
def cart():
    cart = Cart.query.filter_by(user_id=current_user.id).first()

    if not cart:
        return render_template('cart.html', items=[], total=0)

    items = cart.items

    total = 0
    for item in items:
        total += item.product.preco * item.quantidade

    return render_template('cart.html', items=items, total=total)


# ======================
# REMOVER ITEM DO CARRINHO
# ======================

@main.route('/remove-from-cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)

    if item.cart.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()

    return redirect(url_for('main.cart'))


# ======================
# FINALIZAR COMPRA
# ======================

@main.route('/checkout')
@login_required
def checkout():
    cart = Cart.query.filter_by(user_id=current_user.id).first()

    if not cart or not cart.items:
        return redirect(url_for('main.cart'))

    cart_items = cart.items

    # Verificar estoque antes de finalizar
    for item in cart_items:
        if item.quantidade > item.product.estoque:
            return redirect(url_for('main.cart'))

    # Calcular total
    total = 0
    for item in cart_items:
        total += item.product.preco * item.quantidade

    # Criar pedido
    novo_pedido = Order(
        user_id=current_user.id,
        total=total,
        status="Pago"  # Já simulando pagamento aprovado
    )

    db.session.add(novo_pedido)

    # Diminuir estoque
    for item in cart_items:
        item.product.estoque -= item.quantidade

    # Limpar carrinho
    for item in cart_items:
        db.session.delete(item)

    db.session.commit()

    return redirect(url_for('main.index'))

    # Limpar carrinho
    for item in cart.items:
        db.session.delete(item)

    db.session.commit()

    return redirect(url_for('main.pagamento', pedido_id=novo_pedido.id))

@main.route("/favoritar/<int:produto_id>")
@login_required
def favoritar(produto_id):
    produto = Product.query.get_or_404(produto_id)

    if produto not in current_user.favoritos:
        current_user.favoritos.append(produto)
    else:
        current_user.favoritos.remove(produto)

    db.session.commit()
    return redirect(request.referrer)

@main.route("/favoritos")
@login_required
def meus_favoritos():
    return render_template(
        "favoritos.html",
        produtos=current_user.favoritos
    )

@main.route('/admin/dashboard')
@login_required
def admin_dashboard():

    if not current_user.is_admin:
        return redirect(url_for('main.index'))

    page = request.args.get("page", 1, type=int)

    # Produtos paginados
    produtos = Product.query.paginate(page=page, per_page=5)

    # Pedidos recentes
    pedidos = Order.query.order_by(Order.created_at.desc()).limit(5).all()

    total_produtos = Product.query.count()
    total_usuarios = User.query.count()
    total_carrinhos = Cart.query.count()
    total_pedidos = Order.query.count()

    # Soma total arrecadado
    total_arrecadado = db.session.query(db.func.sum(Order.total)).scalar() or 0

    produtos_sem_estoque = Product.query.filter_by(estoque=0).all()
    produtos_estoque_baixo = Product.query.filter(
        Product.estoque <= 5,
        Product.estoque > 0
    ).all()

    return render_template(
        'admin_dashboard.html',
        produtos=produtos,
        pedidos=pedidos,
        total_produtos=total_produtos,
        total_usuarios=total_usuarios,
        total_carrinhos=total_carrinhos,
        total_pedidos=total_pedidos,
        total_arrecadado=total_arrecadado,
        produtos_sem_estoque=produtos_sem_estoque,
        produtos_estoque_baixo=produtos_estoque_baixo
    )

@main.route('/meus-pedidos')
@login_required
def meus_pedidos():
    pedidos = Order.query.filter_by(user_id=current_user.id)\
        .order_by(Order.created_at.desc()).all()

    return render_template("meus_pedidos.html", pedidos=pedidos)

@main.route('/pagamento/<int:pedido_id>')
@login_required
def pagamento(pedido_id):

    pedido = Order.query.get_or_404(pedido_id)

    if pedido.user_id != current_user.id:
        return redirect(url_for('main.index'))

    return render_template('pagamento.html', pedido=pedido)

@main.route('/processar-pagamento/<int:pedido_id>', methods=['POST'])
@login_required
def processar_pagamento(pedido_id):

    pedido = Order.query.get_or_404(pedido_id)

    if pedido.user_id != current_user.id:
        return redirect(url_for('main.index'))

    # Simulação de aprovação automática
    pedido.status = "Pago"

    db.session.commit()

    return redirect(url_for('main.pedido_sucesso', pedido_id=pedido.id))

@main.route('/pedido-sucesso/<int:pedido_id>')
@login_required
def pedido_sucesso(pedido_id):

    pedido = Order.query.get_or_404(pedido_id)

    return render_template('pedido_sucesso.html', pedido=pedido)