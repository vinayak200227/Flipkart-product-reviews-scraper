from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import logging
import pymongo

# log file
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)  

app = Flask(__name__)

@app.route("/", methods = ['GET'])  # route to display home page
@cross_origin()   # it helps to acsses the application from any origin/country so that it is available globally to all
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])   # route to display reviews page
@cross_origin()   # it helps to acsses the application from any origin/country so that it is available globally to all
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")   # requesting search string entered in search form
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString  
            uClient = urlopen(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(productLink)    
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            # print(prod_html)
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})   # will give list of div boxes having class _16PBlm

            filename = searchString + ".csv"    # csv file having particular search string
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"   # header of csv file
            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    #name.encode(encoding='utf-8')
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text  # name of user who wrote comment

                except:
                    logging.info("name")

                try:
                    #rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.div.div.text     # ratings


                except:
                    rating = 'No Rating'
                    logging.info("rating")

                try:
                    #commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.div.div.p.text     # comment title

                except:
                    commentHead = 'No Comment Heading'
                    logging.info(commentHead)
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    #custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text   
                except Exception as e:
                    logging.info(e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)     # append to reviews
            logging.info("log my final result {}".format(reviews))

            # MangoDB
            client = pymongo.MongoClient(("mongodb+srv://vinayakvt2708:vinayak@cluster0.v5gfcxk.mongodb.net/?retryWrites=true&w=majority"))
            db =client['scrapper_reviews']   # database
            coll_pw_eng = db['scraper_reviews_vvt']  # collection
            coll_pw_eng.insert_many(reviews)     # insert all reviews in collection

            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.info(e)
            return 'something is wrong'

    else:
        return render_template('index.html')


if __name__=="__main__":
    app.run(debug=True)
