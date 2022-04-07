from fashlance import db 
from fashlance import app

@app.before_first_request
def create_tables():
    db.create_all()

class Products(db.Model):
    id = db.Column(db.String(10),primary_key=True,nullable=False)
    productDisplayName = db.Column(db.String(255),nullable=False,default='Film')
    year = db.Column(db.Integer(),nullable=False,default=2000)
    gender = db.Column(db.String(20),nullable=False,default='Not available')
    masterCategory = db.Column(db.String(255),nullable=False,default='Not available')
    subCategory = db.Column(db.String(255),nullable=False,default='Not available')
    articleType = db.Column(db.String(255),nullable=False,default='Not available')
    baseColour = db.Column(db.String(255),nullable=False,default='Not available')
    season = db.Column(db.String(20),nullable=False,default='Not available')
    usage = db.Column(db.String(20),nullable=False,default=0)
    amount = db.Column(db.DECIMAL(10,2))
    image = db.Column(db.Text(),nullable=False,default='http://assets.myntassets.com/v1/images/style/properties/7a5b82d1372a7a5c6de67ae7a314fd91_images.jpg')

class Comments(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=False)
    posted_at = db.Column(db.DateTime,nullable=False,default=db.func.now())
    message = db.Column(db.Text(),nullable=False,default='Comment content')
    id = db.Column(db.String(10),db.ForeignKey('products.id'))