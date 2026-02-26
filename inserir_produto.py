from app import create_app
from app.models import db, Product

app = create_app()

with app.app_context():
    print("ANTES:", Product.query.count())

    produto = Product(
        nome="Camisa Feminina Verde",
        descricao="Camisa feminina elegante e confortável",
        preco=89.90,
        imagem="camisa_verde.jpg",
        categoria="Feminino",
        visivel=True
    )

    db.session.add(produto)
    db.session.commit()

    print("DEPOIS:", Product.query.count())