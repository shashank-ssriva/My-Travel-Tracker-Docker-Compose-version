# Import the necessary modules
from flask import Flask, render_template, json, request, redirect
import pymysql
from tables import Results
from flaskext.mysql import MySQL
import dateutil.parser as parser
from datetime import datetime
import urllib.request
import mysql.connector

# Invoke MySQL
#mysql = MySQL()
app = Flask(__name__)

# MySQL database details

config = {
        'user': 'travel_tracker',
        'password': 'MyPassw0rdStr0ng',
        'host': 'db',
        'port': '3306',
        'database': 'MyTravelTracker',
        'auth_plugin': 'mysql_native_password'
    }
#mysql.init_app(app)

# Define the homepage. This page controls the data to be submitted.
@app.route('/')
def main():
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM TravelDetails")
        tripcount = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COUNT(*) FROM TravelDetails WHERE trip_type = 'International'")
        internationalflights = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COUNT(*) FROM TravelDetails WHERE trip_type = 'Domestic'")
        domesticflights = cursor.fetchone()[0]
        if internationalflights > domesticflights:
            diffint = internationalflights - domesticflights
        else:
            diffint = domesticflights - internationalflights
        cursor.execute(
            "SELECT destination_airport, COUNT(*) as count FROM TravelDetails WHERE trip_type = 'International' GROUP BY destination_airport ORDER BY count DESC LIMIT 1")
        mostvisiteddest = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COUNT(*) as count FROM TravelDetails WHERE trip_type = 'International' GROUP BY destination_airport ORDER BY count DESC LIMIT 1")
        mostvisiteddestcount = cursor.fetchone()[0]
        cursor.execute(
            "SELECT destination_airport, COUNT(*) as count FROM TravelDetails WHERE trip_type = 'Domestic' GROUP BY destination_airport ORDER BY count DESC LIMIT 1")
        mostvisiteddomdest = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COUNT(*) as count FROM TravelDetails WHERE trip_type = 'Domestic' GROUP BY destination_airport ORDER BY count DESC LIMIT 1")
        mostvisiteddomdestcount = cursor.fetchone()[0]
        cursor.execute(
            "SELECT source_airport FROM TravelDetails ORDER BY travel_date DESC LIMIT 1;")
        lastsource = cursor.fetchone()[0]
        cursor.execute(
            "SELECT destination_airport FROM TravelDetails ORDER BY travel_date DESC LIMIT 1;")
        lastdestination = cursor.fetchone()[0]
        cursor.execute(
            "SELECT travel_date FROM TravelDetails ORDER BY travel_date DESC LIMIT 1;")
        lastdate = cursor.fetchone()[0]
        date_format = "%Y-%m-%d"
        today = datetime.today().strftime('%Y-%m-%d')
        todaydate = datetime.strptime(today, date_format)
        lastdateval = datetime.strptime(lastdate, date_format)
        delta = todaydate - lastdateval
        days_since_last_trip = delta.days
        print(days_since_last_trip)
        cursor.execute(
            "SELECT travel_date FROM TravelDetails WHERE trip_type = 'Domestic' ORDER BY travel_date DESC LIMIT 1")
        last_dom_trip = cursor.fetchone()[0]
        cursor.execute(
            "SELECT destination_airport, COUNT(*) as count FROM TravelDetails WHERE trip_type = 'International' GROUP BY destination_airport ORDER BY count DESC")
        dataarray = cursor.fetchall()
        labels = []
        values = []
        for i in dataarray:
            labels.append(i[0])
            values.append(i[1])

        cursor.execute(
            "SELECT destination_airport, COUNT(*) as count FROM TravelDetails WHERE trip_type = 'Domestic' GROUP BY destination_airport ORDER BY count DESC")
        dataarraydom = cursor.fetchall()
        labelsdom = []
        valuesdom = []
        for i in dataarraydom:
            labelsdom.append(i[0])
            valuesdom.append(i[1])

        # Code to find the years & their respective trip counts
        cursor.execute("SELECT travel_date FROM TravelDetails")
        yearArray = cursor.fetchall()
        yearlist = []
        yearlistarray = []
        for item in yearArray:
            yearlist.append(item[0])
        for x in yearlist:
            y = parser.parse(x).year
            yearlistarray.append(y)
        uniqueyearlist = []
        tripcountlist = []
        for x in yearlistarray:
            if x not in uniqueyearlist:
                uniqueyearlist.append(x)
        uniqueyearlist.sort()
        for x in uniqueyearlist:
            cursor.execute(
                "SELECT COUNT(*) FROM TravelDetails WHERE travel_date LIKE %s", ("%" + str(x) + "%",))
            tripcountarray = cursor.fetchall()
            for z in tripcountarray:
                tripcountlist.append(z[0])
        conn.close()

        with urllib.request.urlopen("https://api.weatherbit.io/v2.0/current?city=%s&key=c1c3dd1fde8649ac8ff1e2f2d40e16d9" % mostvisiteddest) as url:
            most_visited_city_data = json.loads(url.read().decode())
            most_visited_city_temp = most_visited_city_data['data'][0]['temp']
            most_visited_city_rh = most_visited_city_data['data'][0]['rh']

        return render_template('index.html',
                               tripcount=tripcount, internationalflights=internationalflights,
                               domesticflights=domesticflights, mostvisiteddest=mostvisiteddest,
                               mostvisiteddestcount=mostvisiteddestcount,
                               mostvisiteddomdest=mostvisiteddomdest, mostvisiteddomdestcount=mostvisiteddomdestcount,
                               lastsource=lastsource, lastdestination=lastdestination, lastdate=lastdate,
                               diffint=diffint, labels=labels, values=values, labelsdom=labelsdom, valuesdom=valuesdom,
                               uniqueyearlist=uniqueyearlist, tripcountlist=tripcountlist,
                               days_since_last_trip=days_since_last_trip, last_dom_trip=last_dom_trip,
                               most_visited_city_temp=most_visited_city_temp, most_visited_city_rh=most_visited_city_rh
                               )
    except Exception as e:
        return json.dumps({'error': str(e)})

# addDetails route takes the values from the homepage & POSTs to the add-details.html page.
@app.route('/addDetails', methods=['POST', 'GET'])
def addDetails():
    try:
        _tookoff = request.form['took-off-from']  # GET data from the text-box.
        _landedon = request.form['landed-on']  # GET data from the text-box.
        _tripdate = request.form['trip-date']  # GET data from the text-box.
        # GET data from the dropdown.
        _triptype = request.form['trip-category']
        # If none of the text-boxes is empty & submit button is pressed.
        if _tookoff and _landedon and _tripdate and _triptype and request.method == 'POST':
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()
            sql = "INSERT INTO TravelDetails(source_airport, destination_airport, travel_date, trip_type) VALUES(%s, %s, %s, %s)"
            data = (_tookoff, _landedon, _tripdate, _triptype,)
            cursor.execute(sql, data)
            conn.commit()
            return redirect('/')
        else:
            return 'Please fill all the details...', 400
    except Exception as e:
        return json.dumps({'error': str(e)})


@app.route('/tripDetails')
def tripDetails():
    print("Trip details page.")
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute(
            "SELECT * FROM TravelDetails ORDER BY travel_date DESC")
        result = cursor.fetchall()
        # table = Results(rows)
        # table.border = True
        
        return render_template('trip-details.html', result=result)
    except Exception as e:
        return json.dumps({'error': str(e)})


@app.route('/editTrip/<int:id>')
def edit_trip(id):
    try:
        conn = mysql.connector.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM TravelDetails WHERE travel_id=%s", id)
        row = cursor.fetchone()
        if row:
            return render_template('edit-trip.html', row=row)
        else:
            return 'Error loading #{id}'.format(id=id)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/update', methods=['POST'])
def update_trip():
    try:
        _tookoff = request.form['took-off-from']  # GET data from the text-box.
        _landedon = request.form['landed-on']  # GET data from the text-box.
        _tripdate = request.form['trip-date']  # GET data from the text-box.
        # GET data from the dropdown.
        _triptype = request.form['trip-category']
        _tripid = request.form['trip-id']
        # Validate the received values
        if _tookoff and _landedon and _tripdate and _triptype and _tripid and request.method == 'POST':
            # Save edits
            sql = "UPDATE TravelDetails SET source_airport=%s, destination_airport=%s, travel_date, trip_type=%s WHERE trip_id=%s"
            data = (_tookoff, _landedon, _tripdate, _triptype, _tripid)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql, data)
            conn.commit()
            flash('User updated successfully!')
            return redirect('/')
        else:
            return 'Error while updating the trip!'
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/delete/<int:id>')
def delete_user(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tbl_user WHERE user_id=%s", (id,))
        conn.commit()
        flash('User deleted successfully!')
        return redirect('/')
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002, debug=True)
