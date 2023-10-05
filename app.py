from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL

app = Flask(__name__)

mysql = MySQL(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'sakila'

@app.route('/', methods=['GET', 'POST'])
def index():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        if request.form.get("top") == "View Top 5 Rented":
            res = cur.execute("SELECT DISTINCT (film.title), COUNT(film.title), film.film_id FROM film RIGHT JOIN inventory ON film.film_id = inventory.film_id RIGHT JOIN rental ON inventory.inventory_id = rental.inventory_id GROUP BY film.title, film.film_id ORDER BY COUNT(film.title) DESC LIMIT 0, 5;")
            if res > 0:
                results = cur.fetchall()
                return render_template('index.html', details=results)
            
        elif isinstance(request.form.get("top"), str):
            movie = request.form.get("top")
            movie = str(movie)
            res = cur.execute("SELECT film_id, title, description, release_year FROM film WHERE title=%s",(movie,))
            if res > 0:
                results = cur.fetchall()
                return render_template('index.html', movieDetails=results)
            
        elif request.form.get("topActor") == "View Top 5 Actors":
            res = cur.execute("SELECT actor.first_name, actor.last_name, COUNT(film_actor.actor_id) FROM actor JOIN film_actor ON actor.actor_id = film_actor.actor_id GROUP BY film_actor.actor_id ORDER BY COUNT(film_actor.actor_id) DESC LIMIT 0,5;")
            if res > 0:
                results = cur.fetchall()
                return render_template('index.html', actorDetails=results)
       
        elif request.form.get("topActor") == "View Details":
            actorFname = request.form.get("first_name")
            actorLname = request.form.get("last_name")
            res = cur.execute("SELECT title, COUNT(film.title) FROM rental JOIN inventory ON rental.inventory_id = inventory.inventory_id JOIN film ON inventory.film_id = film.film_id JOIN film_actor ON film.film_id = film_actor.film_id JOIN actor ON film_actor.actor_id = actor.actor_id WHERE actor.first_name=%s AND actor.last_name=%s GROUP BY film.title ORDER BY COUNT(film.title) DESC LIMIT 0,5;", (actorFname, actorLname,))
            if res > 0:
                results = cur.fetchall()
                return render_template('index.html', iActorDetails=results)
        
    if request.method == "POST":
        if request.form.get("nav") == "Home":
            return redirect("/")
        elif request.form.get("nav") == "Movies":
            return redirect("/movies")
        elif request.form.get("nav") == "Customers":
            return redirect("/customers")
                       
    return render_template('index.html')

@app.route('/movies', methods=['GET', 'POST'])
def movies():
    cur = mysql.connection.cursor()
    if request.method == "POST":
        if request.form.get("subSearch") == "Go":
            txt = "%" + request.form['search'] +"%"
            res = cur.execute('SELECT DISTINCT(title) FROM category JOIN film_category ON category.category_id = film_category.category_id JOIN film ON film_category.film_id = film.film_id JOIN film_actor ON film.film_id = film_actor.film_id JOIN actor ON film_actor.actor_id = actor.actor_id WHERE film.title LIKE %s OR actor.first_name LIKE %s OR actor.last_name LIKE %s OR category.name LIKE %s GROUP BY title, description, release_year, category.name ORDER BY title', (txt, txt, txt, txt,))
            if res > 0:
                results = cur.fetchall()
                return render_template('movies.html', searchRes=results)
        elif isinstance(request.form.get("mov"), str):
            movie = request.form.get("mov")
            movie = str(movie)
            res = cur.execute("SELECT film_id, title, description, release_year FROM film WHERE title=%s",(movie,))
            if res > 0:
                results = cur.fetchall()
                return render_template('movies.html', movieDetails=results)
        elif request.form.get("rent") == "Rent":
            movieID = str(request.form.get("rentedMov"))
            custID = str(request.form.get("custID"))
            res = cur.execute("SELECT inventory_id FROM inventory WHERE film_id=%s LIMIT 0,1;",(movieID,))
            if res > 0:
                results = str(cur.fetchall())
                results = results.replace('(', '')
                results = results.replace(')', '')
                invID = results.replace(',', '')
            res = cur.execute("INSERT INTO rental VALUES (DEFAULT, CURDATE(),%s, %s, NULL, 1, DEFAULT)", (invID, custID,))    
              
    if request.method == "POST":
        if request.form.get("nav") == "Home":
            return redirect("/")
        elif request.form.get("nav") == "Movies":
            return redirect("/movies")
        elif request.form.get("nav") == "Customers":
            return redirect("/customers")
    return render_template('movies.html')

@app.route('/customers', methods=['GET', 'POST'])
def customers():
    cur = mysql.connection.cursor()
    if request.method == "POST":
        if request.form.get("list") == "View All":
            res = cur.execute("SELECT customer_id, first_name, last_name FROM customer")
            if res > 0:
                results = cur.fetchall()
                return render_template('customers.html', customerList=results)
        elif request.form.get("filterSub") == "Filter":
            filter = request.form.get("filterVal")
            newFilter = "%" + request.form.get("filterVal") + "%"
            res = cur.execute("SELECT customer_id, first_name, last_name FROM customer WHERE customer_id=%s OR first_name LIKE %s OR last_name LIKE %s", (filter, newFilter, newFilter,))
            if res > 0:
                results = cur.fetchall()
                return render_template('customers.html', customerList=results)
        elif request.form.get("subAdd") == "Add Customer":
            #Fetch all variables
            fName = request.form.get("fName")
            lName = request.form.get("lName")
            email = request.form.get("email")
            phone = request.form.get("phone")
            addy = request.form.get("addy")
            addy2 = request.form.get("addy2")
            district = request.form.get("dist")
            city = request.form.get("city")
            zip = request.form.get("zip")
            country = request.form.get("country")

            #country
            res = cur.execute("SELECT country_id FROM country WHERE country=%s",(country,))
            if res > 0:
                results = str(cur.fetchall())
                results = results.replace('(', '')
                results = results.replace(')', '')
                countryID = results.replace(',', '')
            
            #city
            res = cur.execute("SELECT city_id FROM city WHERE city=%s", (city,))
            if res > 0:
                results = str(cur.fetchall())             
            else:
                cur.execute("INSERT INTO city VALUES (DEFAULT, %s, %s, DEFAULT)", (city, countryID,))
                mysql.connection.commit()
                res = cur.execute("SELECT city_id FROM city WHERE city=%s", (city,))
                results = str(cur.fetchall())
            results = results.replace('(', '')
            results = results.replace(')', '')
            cityID = results.replace(',', '')

            #address
            res = cur.execute("INSERT INTO address VALUES (DEFAULT, %s, %s, %s, %s, %s, %s,POINT(51.61100420,-0.10213410), DEFAULT)", (addy, addy2, district, cityID, zip, phone,))
            mysql.connection.commit()    
            res = cur.execute("SELECT address_id FROM address WHERE phone=%s",(phone,))
            if res > 0:
                results = str(cur.fetchall())
                results = results.replace('(', '')
                results = results.replace(')', '')
                addyID = results.replace(',', '')

            #customer (finally)
            res = cur.execute("INSERT INTO customer VALUES (DEFAULT, 1, %s, %s, %s, %s, 1, CURDATE(), DEFAULT)", (fName, lName, email, addyID,))
            mysql.connection.commit()
            res = cur.execute("SELECT customer_id FROM customer WHERE last_name=%s AND email=%s", (lName, email))
            if res > 0:
                results = str(cur.fetchall())
                results = results.replace('(', '')
                results = results.replace(')', '')
                custID = results.replace(',', '')
                return custID   

                
    if request.method == "POST":
        if request.form.get("nav") == "Home":
            return redirect("/")
        elif request.form.get("nav") == "Movies":
            return redirect("/movies")
        elif request.form.get("nav") == "Customers":
            return redirect("/customers")
    return render_template('customers.html')

if __name__ == '__main__':
    app.run(debug=True)
