from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL

app = Flask(__name__)

mysql = MySQL(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'sakila'

def stripRes(result):
    result = result.replace('(', '')
    result = result.replace(')', '')
    result = result.replace('\'', '')
    newRes = result.replace(',', '')
    return newRes

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
            mysql.connection.commit()    
              
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
                countryID = stripRes(str(cur.fetchall()))
            
            #city
            res = cur.execute("SELECT city_id FROM city WHERE city=%s", (city,))
            if res > 0:
                results = str(cur.fetchall())             
            else:
                cur.execute("INSERT INTO city VALUES (DEFAULT, %s, %s, DEFAULT)", (city, countryID,))
                mysql.connection.commit()
                res = cur.execute("SELECT city_id FROM city WHERE city=%s", (city,))
                results = str(cur.fetchall())
            cityID = stripRes(results)

            #address
            res = cur.execute("INSERT INTO address VALUES (DEFAULT, %s, %s, %s, %s, %s, %s,POINT(51.61100420,-0.10213410), DEFAULT)", (addy, addy2, district, cityID, zip, phone,))
            mysql.connection.commit()    
            res = cur.execute("SELECT address_id FROM address WHERE phone=%s",(phone,))
            if res > 0:
                addyID = stripRes(str(cur.fetchall()))

            #customer (finally)
            res = cur.execute("INSERT INTO customer VALUES (DEFAULT, 1, %s, %s, %s, %s, 1, CURDATE(), DEFAULT)", (fName, lName, email, addyID,))
            mysql.connection.commit()
            res = cur.execute("SELECT customer_id FROM customer WHERE last_name=%s AND email=%s", (lName, email))
            if res > 0:
                custID = stripRes(str(cur.fetchall()))
                
        elif request.form.get("custDet") == "View More":
            cID = request.form.get("custID")
            #gathering customer information
            #first name
            res = cur.execute("SELECT first_name FROM customer WHERE customer_id=%s;", (cID,)) 
            firstName = stripRes(str(cur.fetchone()))
            #last name
            res = cur.execute("SELECT last_name FROM customer WHERE customer_id=%s;", (cID,))
            lastName = stripRes(str(cur.fetchone()))
            #email
            res = cur.execute("SELECT email FROM customer WHERE customer_id=%s;", (cID,))
            email =  stripRes(str(cur.fetchone()))
            #address id
            res = cur.execute("SELECT address_id FROM customer WHERE customer_id=%s;", (cID,))        
            addressID = stripRes(str(cur.fetchone()))
            res = cur.execute("SELECT address FROM address WHERE address_id=%s", (addressID,))
            street = stripRes(str(cur.fetchall()))
            res = cur.execute("SELECT address2 FROM address WHERE address_id=%s", (addressID,))
            street2 = stripRes(str(cur.fetchall()))
            res = cur.execute("SELECT district FROM address WHERE address_id=%s", (addressID,))
            district = stripRes(str(cur.fetchall()))
            res = cur.execute ("SELECT phone FROM address WHERE address_id=%s", (addressID,))
            phone = stripRes(str(cur.fetchall()))
            res = cur.execute ("SELECT postal_code FROM address WHERE address_id=%s", (addressID,))
            zip = stripRes(str(cur.fetchall()))
            #city id
            res = cur.execute("SELECT city_id FROM address WHERE address_id=%s", (addressID,))
            cityID = stripRes(str(cur.fetchall()))
            res = cur.execute("SELECT city FROM city WHERE city_id=%s", (cityID,))
            city = stripRes(str(cur.fetchall()))
            #country id 
            res = cur.execute("SELECT country_id FROM city WHERE city_id=%s", (cityID,))
            countryID = stripRes(str(cur.fetchall()))
            res = cur.execute("SELECT country FROM country WHERE country_id=%s", (countryID,))
            country = stripRes(str(cur.fetchall()))

            return render_template('customers.html', cID = cID, fN = firstName, lN = lastName, eM = email, sT = street, sT2 = street2, dT = district, pH = phone, cT = city, zip = zip, cTry = country)

        elif request.form.get("upCus") == "Update Customer":
            ID = request.form.get("ID")
            fName = request.form.get("fN")
            lName = request.form.get("lN")
            email = request.form.get("eM")
            phone = request.form.get("pH")
            addy = request.form.get("sT")
            addy2 = request.form.get("sT2")
            district = request.form.get("dT")
            city = request.form.get("cT")
            zip = request.form.get("zip")
            country = request.form.get("cTry")

            #update customer table
            res = cur.execute("UPDATE customer SET first_name=%s, last_name=%s, email=%s WHERE customer_id=%s", (fName, lName, email, ID))
            mysql.connection.commit()

            #update address table
            #get address ID and country ID
            res = cur.execute("SELECT address_id FROM customer WHERE customer_id=%s", (ID,))
            addyID = stripRes(str(cur.fetchone()))
            res = cur.execute("SELECT country_id FROM country WHERE country=%s", (country,))
            countryID = stripRes(str(cur.fetchone()))
            #city
            res = cur.execute("SELECT city_id FROM city WHERE city=%s", (city,))
            if res > 0:
                cityID = stripRes(str(cur.fetchone()))
            else: #if city does not exist
                res = cur.execute("INSERT INTO city VALUES (DEFAULT, %s, %s, DEFAULT)", (city, countryID,))
                mysql.connection.commit()
                res = cur.execute("SELECT city_id FROM city WHERE city=%s", (city,))
                cityID = stripRes(str(cur.fetchone()))

            res = cur.execute("UPDATE address SET address=%s, address2=%s, district=%s, city_id=%s, postal_code=%s, phone=%s WHERE address_id=%s", (addy, addy2, district, cityID, zip, phone, addyID,))
            mysql.connection.commit()

        elif request.form.get("delCus") == "Delete Customer":
            custID = request.form.get("ID")
            res = cur.execute("DELETE FROM customer WHERE customer_id=%s", (custID,))
            mysql.connection.commit()
        elif request.form.get("rentals") == "View Rentals":
            custID = request.form.get("ID")
            res = cur.execute("SELECT rental_id, film.title, rental_date, return_date, rental.last_update FROM rental JOIN inventory ON rental.inventory_id = inventory.inventory_id JOIN film ON inventory.film_id = film.film_id WHERE rental.customer_id=%s;", (custID,))
            if res > 0:
                results = cur.fetchall()
                res = cur.execute("SELECT last_name FROM customer WHERE customer_id=%s", (custID,))
                lNam = stripRes(str(cur.fetchone()))
                res = cur.execute("SELECT first_name FROM customer WHERE customer_id=%s", (custID,))
                fNam = stripRes(str(cur.fetchone()))
                return render_template("customers.html", rentals=results, custIden=custID, lNam=lNam, fNam=fNam)

            #grab return_date individually and store in variable to help determine if movie has been returned on front-end

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
