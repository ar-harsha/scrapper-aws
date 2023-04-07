from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as ureq
import traceback

application = Flask(__name__)
app = application

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/review", methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        try:
            searchstring = request.form['content'].replace(" ","")
            flipkart_url = 'https://www.flipkart.com/search?q='+searchstring
            uclient = ureq(flipkart_url)
            flipkartpage = uclient.read()
            uclient.close()
            flipkart_html = bs(flipkartpage,"html.parser")
            bigboxes = flipkart_html.findAll("div",{"class":"_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productlink = "https://www.flipkart.com"+box.div.div.div.a['href']
            productreq = requests.get(productlink)
            productreq.encoding = 'utf-8'
            product_html = bs(productreq.text,"html.parser")
            commentboxes = product_html.findAll('div',{"class":"_16PBlm"})
            filename = searchstring+'.csv'
            fw = open(filename,'w')
            headers = "product ,customer name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    name = commentbox.div.div.find_all("p",{"class":"_2sc7ZR _2V5EHH"})[0].text
                except:
                    name = "No Name"
                try:
                    rating = commentbox.div.div.div.div.text
                except:
                    rating = "No Rating"
                try:
                    commentHead = commentbox.div.div.div.p.text
                except:
                    commentHead = "No Comment Heading"
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    custcomment = comtag[0].div.text
                except Exception as e:
                    print("Exception whle creating dic: ",e)
                dic = {
                    "Product": searchstring,
                    "Name": name,
                    "Rating" : rating,
                    "Comment Heading":commentHead,
                    "Comment" : custcomment
                }
                reviews.append(dic)
            return render_template('result.html',reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print("excception mesage : ",e)
            print(traceback.format_exc())
            return "somthigns wrong"
        else:
            return render_template('index.html')


if __name__ == "__main__":
    app.run()
