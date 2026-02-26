from flask import Blueprint, session, redirect, url_for, render_template
from app.models import Product

cart = Blueprint("cart", __name__)

# -------------------------
# Adicionar ao carrinho
# -------------------------
@cart.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    if "cart" not in session:
        session["cart"] = []

    session["cart"].append(product_id)
    session.modified = True

    return redirect(url_for("main.produtos"))


# -------------------------
# Remover do carrinho
# -------------------------
@cart.route("/remove_from_cart/<int:product_id>")
def remove_from_cart(product_id):
    if "cart" in session:
        if product_id in session["cart"]:
            session["cart"].remove(product_id)
            session.modified = True

    return redirect(url_for("cart.ver_carrinho"))


# -------------------------
# Ver carrinho
# -------------------------
@cart.route("/carrinho")
def ver_carrinho():
    cart_ids = session.get("cart", [])

    produtos = []
    total = 0

    for product_id in cart_ids:
        produto = Product.query.get(product_id)
        if produto:
            produtos.append(produto)
            total += produto.preco

    return render_template(
        "carrinho.html",
        produtos=produtos,
        total=total
    )