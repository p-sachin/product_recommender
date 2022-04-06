from flask import Flask, render_template, redirect, request
from flask_bootstrap import Bootstrap
import joblib
import numpy as np
import pandas as pd
import difflib
import tensorflow
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.keras.layers import GlobalMaxPooling2D
from tensorflow.keras.preprocessing import image
from keras.preprocessing.image import load_img
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from numpy.linalg import norm
from sklearn.neighbors import NearestNeighbors
from PIL import Image
import numpy as np
import json
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)


model = ResNet50(weights="imagenet", include_top=False, input_shape=(60,80,3))
model.trainable = False

model = tensorflow.keras.Sequential([
    model,
    GlobalMaxPooling2D()
])

feature_list = np.array(joblib.load(open('image_embed_1.pkl', 'rb')))
filenames = joblib.load(open('_file_name_1.pkl', 'rb'))
myjsonfile = open('_final_csvjson.json', 'r')
jsondata = myjsonfile.read()

products = json.loads(jsondata)

def recommend(image_url, feature_list):
    reco_product_id = []
    digit = ''
    img = Image.open(requests.get(image_url, stream=True).raw)
    img = img.resize((80,60), Image.NEAREST)
    img_array = image.img_to_array(img)
    expanded_img_array = np.expand_dims(img_array, axis=0)
    preprocessed_img = preprocess_input(expanded_img_array)
    result = model.predict(preprocessed_img).flatten()
    normalized_result = result /  norm(result)
    neighbors = NearestNeighbors(n_neighbors=6, algorithm='brute', metric='euclidean')
    neighbors = neighbors.fit(feature_list)
    indices = neighbors.kneighbors([normalized_result])[1]

    for file in indices[0][1:6]:
        target = filenames[file]
        digits = [d for d in target if d.isdigit()]
        digit = ''.join(digits)
        reco_product_id.append(digit)
    return reco_product_id

def image_search_recommend(img, feature_list):
    reco_product_id = []
    digit = ''
    img_array = image.img_to_array(img)
    expanded_img_array = np.expand_dims(img_array, axis=0)
    preprocessed_img = preprocess_input(expanded_img_array)
    result = model.predict(preprocessed_img).flatten()
    normalized_result = result /  norm(result)
    neighbors = NearestNeighbors(n_neighbors=5, algorithm='brute', metric='euclidean')
    neighbors = neighbors.fit(feature_list)
    indices = neighbors.kneighbors([normalized_result])[1]
    for file in indices[0]:
        target = filenames[file]
        digits = [d for d in target if d.isdigit()]
        digit = ''.join(digits)
        reco_product_id.append(digit)
    return reco_product_id



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

@app.route('/')
def index():
    all_products = db.session.query(Products).all()
    return render_template('index.html', all_products=all_products)

@app.route('/technologies')
def technologies():
    return render_template('technologies.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    page = request.args.get('page', 1, type=int)
    if request.method == 'GET':
        for item in products:
            isExisting = db.session.query(Products).filter(Products.id == str(item["id"])).first()
            if isExisting:
                pass
            else:
                product2database = Products(
                id=item["id"],
                year=item["year"],
                gender=item["gender"],
                masterCategory=item["masterCategory"],
                subCategory=item["subCategory"],
                articleType=item["articleType"],
                baseColour=item["baseColour"],
                season=item["season"],
                usage=item["usage"],
                amount=item['price'],
                productDisplayName=item["productDisplayName"],
                image = item["image"]
            )
                db.session.add(product2database)
        db.session.commit()

        prode = db.session.query(Products).all()

        prod = db.session.query(Products).paginate(page=page, per_page=12)

        #Counts
        total_prod = len(prode)

        # FIlter MasterCat
        res = list(item.masterCategory for item in prode)
        my_dict = {i:res.count(i) for i in res}
        my_dict = sorted(my_dict.items(), key=lambda x: x[1], reverse=True)
        sorted_master = {k: v for k, v in my_dict}

        #Filter SubCat
        result = list(item.articleType for item in prode)
        my_dict = {i:result.count(i) for i in result}
        my_dict = sorted(my_dict.items(), key=lambda x: x[1], reverse=True)
        sub_filter = {k: v for k, v in my_dict}
        
        return render_template('dashboard.html', products=prod, prod_count=total_prod, cat_filter=sorted_master, sub_filter=sub_filter)

@app.route('/categories', methods=['GET', 'POST'])
def categories():
    page = request.args.get('page', 1, type=int)
    tag = request.args.get('type')
    search = "%{}%".format(tag)
    prode = db.session.query(Products).all()
    total_prod = len(Products.query.filter(Products.masterCategory.like(search)).all())
    categories = Products.query.filter(Products.masterCategory.like(search)).paginate(page=page, per_page=12)

    # FIlter MasterCat
    res = list(item.masterCategory for item in prode)
    my_dict = {i:res.count(i) for i in res}
    my_dict = sorted(my_dict.items(), key=lambda x: x[1], reverse=True)
    sorted_master = {k: v for k, v in my_dict}

    #Filter SubCat
    result = list(item.articleType for item in prode)
    my_dict = {i:result.count(i) for i in result}
    my_dict = sorted(my_dict.items(), key=lambda x: x[1], reverse=True)
    sub_filter = {k: v for k, v in my_dict}

    return render_template('dashboard.html', products=categories, prod_count=total_prod, cat_filter=sorted_master, sub_filter=sub_filter)

@app.route('/filters', methods=['GET', 'POST'])
def filters():
    page = request.args.get('page', 1, type=int)
    tag = request.args.get('type')
    search = "%{}%".format(tag)
    prode = db.session.query(Products).all()
    total_prod = len(Products.query.filter(Products.articleType.like(search)).all())
    categories = Products.query.filter(Products.articleType.like(search)).paginate(page=page, per_page=12)

        # FIlter MasterCat
    res = list(item.masterCategory for item in prode)
    my_dict = {i:res.count(i) for i in res}
    my_dict = sorted(my_dict.items(), key=lambda x: x[1], reverse=True)
    sorted_master = {k: v for k, v in my_dict}

    #Filter SubCat
    result = list(item.articleType for item in prode)
    my_dict = {i:result.count(i) for i in result}
    my_dict = sorted(my_dict.items(), key=lambda x: x[1], reverse=True)
    sub_filter = {k: v for k, v in my_dict}
    return render_template('dashboard.html', products=categories, prod_count=total_prod, cat_filter=sorted_master, sub_filter=sub_filter)



@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        name = request.form.get('keyword')
        if name != '':
            all_products = db.session.query(Products).all()
            base_color = [item.baseColour for item in all_products]
            article_type = [item.articleType for item in all_products]
            productDisplayName = [item.productDisplayName for item in all_products]
            id = [item.id for item in all_products]
            df = pd.DataFrame()
            index = [value for value in range(3216)]
            df['productDisplayName'] = productDisplayName
            df['id'] = id
            df['index'] = index
            df['base_color'] = base_color
            df['article_type'] = article_type
            combined_features = df['base_color']+' '+df['article_type']
            df['combined_features'] = combined_features
            vectorizer = TfidfVectorizer()
            feature_vectors = vectorizer.fit_transform(combined_features)
            # Similarity Score
            similarity = cosine_similarity(feature_vectors)
            find_close_match = difflib.get_close_matches(name, combined_features)

            try:
                close_match = find_close_match[0]
                            # Finding the index of product with name
                index_product = df[df.combined_features == close_match]['index'].values[0]
                # Printing a list of similar products
                similarity_score = list(enumerate(similarity[index_product]))
                # Sort products based on their similarity score
                sorted_similar = sorted(similarity_score, key = lambda x:x[1], reverse=True)

                id_list = []
                for prod in sorted_similar:
                    index = prod[0]
                    product_id = df[df.index==index]['id'].values[0]
                    if len(id_list) <= 6:
                        id_list.append(product_id)
                    else:
                        pass

                searched_products = []        
                for p_id in id_list:
                    search_products = db.session.query(Products).filter(Products.id == p_id).first()
                    searched_products.append(search_products)
                return render_template('product-list.html', searched_product=searched_products, name=name)

            except:
                close_match = 'None'
                return render_template('product-list.html', searched_product=close_match, name=name)
                


        else:

            imageFile = request.files['fileup']
            image_path = "./static/img/" + imageFile.filename    
            imageFile.save(image_path)
            image = load_img(image_path, target_size=(60, 80))
            reco_id = image_search_recommend(image, feature_list)
            prod_list = []
            for r_id in reco_id:
                recommended_products = db.session.query(Products).filter(Products.id==r_id).first()
                prod_list.append(recommended_products)

            return render_template('product-list.html', prod_lists=prod_list, img_name=imageFile.filename)

@app.route('/product_details/<id>', methods=['GET', 'POST'])
def info(id):
    comments = Comments.query.filter_by(id=id).all()

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        comment = Comments(name=name, email=email, message=message, id=id)
        db.session.add(comment)
        db.session.commit()
        return redirect(request.url)
    user_info=db.session.query(Products).filter(Products.id==id).first()
    image_url = user_info.image
    reco_id = recommend(image_url, feature_list)
    rec_list = []
    for r_id in reco_id:
        recommended_products = db.session.query(Products).filter(Products.id==r_id).first()
        rec_list.append(recommended_products)

    return render_template('single-product.html', information=user_info, comments=comments, rec=rec_list)


if __name__ == '__main__':
    #app.run('0.0.0.0', port=(os.environ.get("PORT", 5000)))
    app.run(debug=True)
