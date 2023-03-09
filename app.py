
from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import pymongo
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)


app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")


@app.route("/reviews" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
        try:

            searchString = request.form['content'].replace(" ","")
            logging.info(searchString)
            uClient = uReq(searchString)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser") 
            logging.info(flipkart_html)
            div_classes = flipkart_html.find_all('div',{'class': 'col _2wzgFH K0kLPL'})
            logging.info(len(div_classes))
            product_name = flipkart_html.find_all('div', {'class':'_2s4DIt _1CDdy2'})[0].text
            logging.info(product_name)
            header = "Product,Name,Rating,Comment Heading, Comments\n"
            
            fw = open(f"{product_name[0:20]}"+".csv","w")
            fw.write(header)
            reviews = []
            for div_class in div_classes:
                try:
                    #collecting rating
                    rating = div_class.find('div', {'class':'_3LWZlK _1BLPMq'}).text
                except:
                    rating = "No Rating"
                    logging.info(rating)
                try:
                    #collecting comment head
                    commentHead = div_class.find('p', {'class': '_2-N8zT'}).text
                except:
                    commentHead = "No Header"
                    logging.info(commentHead)
                try:
                    #collecting username
                    username = div_class.find('p', {'class': '_2sc7ZR _2V5EHH'}).text
                except:
                    username = "No Name"
                    logging.info(username)

                try:
                    #collecting comments
                    comment = div_class.find('div', {'class': 't-ZTKy'}).div.div.text
                except:
                    comment = "No comment"
                    logging.info(comment)
                    
                mydict = {"Product": product_name, "Name": username, "Rating": rating, "CommentHead": commentHead,
                        "Comment": comment}
                csvdata = f"{product_name},{username},{rating},{commentHead.replace(',',' ')},{comment.replace(',',' ')}\n"
                fw.write(csvdata)
                reviews.append(mydict)
                logging.info(f"This is the Final log {reviews}")
                
            print(reviews)       
            fw.close()
            client = pymongo.MongoClient('mongodb+srv://monu:monu123@datascience.w4c50iz.mongodb.net/?retryWrites=true&w=majority') 
            db = client['DataScience']
            coll_data = db['web_scraper']
            coll_data.insert_many(reviews)


            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.info(e)
            return "something went wrong"
    else:
        return render_template('index.html')

if __name__=="__main__":
    app.run(host="0.0.0.0")