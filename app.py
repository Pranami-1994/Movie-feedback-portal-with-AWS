from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
import json
from flask import jsonify 

app = Flask(__name__)
app.secret_key = "your_secret_key"  # For flash messages

# RDS configuration
rds_host = 'database-2.cb4kuiq2024t.us-east-1.rds.amazonaws.com'  # Replace with your RDS endpoint
rds_port = 3306  # Default MySQL port
db_username = 'admin'  # Replace with your database username
db_password = 'pranamidas1994'  # Replace with your database password
db_name = 'movie_feedback'  # Replace with your database name


print(rds_host)

# Connect to the RDS MySQL database
def connect_to_rds():
    try:
        connection = pymysql.connect(
            host=rds_host,
            user=db_username,
            password=db_password,
            database=db_name,
            port=rds_port
        )
        print("Connected to the database!")
        return connection
    except pymysql.MySQLError as e:
        print(f"Error connecting to the database: {e}")
        return None

def getMovies():
    connection = connect_to_rds()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM movie")
            movies = cursor.fetchall()

            # convert moie touple data to json
            if len(movies) > 0:
                keys = ['id', 'title', 'description', 'total_review', 'avg_rating', 'image_url']
                data = []
                for item in movies:
                    data.append(item)
                    # for item_data in item:
                json_data = [dict(zip(keys, item)) for item in data]

                
                # json_data =  data # [dict(zip(keys, item)) for item in data]
                # converted_data = json.dump(json_data, indent=4)
                # converted_data = jsonify(json_data, indent=4)

                return json_data
            else:
                return []
        except pymysql.MySQLError as e:
            print(f"Error connecting to the database: {e}")
            return []
    else:
        return []
    


def getMovieData(movie_id):
    connection = connect_to_rds()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute('''SELECT * FROM movie where id=%s''', (movie_id))
            movies = cursor.fetchall()
            if len(movies) > 0:
                data = [movies[0]]
                keys = ['id', 'title', 'description', 'total_review', 'avg_rating', 'image_url']
                json_data = [dict(zip(keys, item)) for item in data]
                return json_data[0]
            else:
                return None
        except pymysql.MySQLError as e:
            print(f"Error connecting to the database: {e}")
            return None
    else:
        return None
    
def updateMovieData(movie_id, total_reviews, avg_rating):
    connection = connect_to_rds()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute('''UPDATE movie SET avg_rating = %s, total_review = %s WHERE id = %s''', 
                           (avg_rating, total_reviews, movie_id))
            connection.commit()
            return True
        except pymysql.MySQLError as e:
            print(f"Error connecting to the database: {e}")
            return False
    else:
        return False

def addFeedback(name, email, feedback_text, rating, movie_name):
    connection = connect_to_rds()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute('''INSERT INTO feedback (movie, name, email, feedback, rating)
                              VALUES (%s, %s, %s, %s, %s)''', 
                              (movie_name, name, email, feedback_text, rating))
            connection.commit()
            return True
        except pymysql.MySQLError as e:
            print(f"Error connecting to the database: {e}")
            return False
    else:
        return False

# Homepage route
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/test')
def test():
    return render_template('test.html', data=movies)


# Movies selection route
@app.route('/movie')
def movies():
    movies = getMovies()
    return render_template('movie.html', data=movies)

# Feedback form route
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        # Get form data
        # data = request.data
        decoded_data = request.data.decode('utf-8')
        data = json.loads(decoded_data)

        print("data: ", data)
        id = data.get("id", "")
        movie_name = data.get("movie_name", "")
        name = data.get("name", "")
        email = data.get("email", "")
        feedback_text = data.get("feedback", "")
        rating = data.get("rating", 0)

        print(f"Received feedback for movie , {name}, {email}, {feedback_text}, {rating}")

        is_fedback_added = addFeedback(name, email, feedback_text, rating, movie_name)

        print("is feedback added: ", is_fedback_added, "\n")

        if is_fedback_added:
            movie_data = getMovieData(id)

            print("got movie data: ", movie_data, "\n")

            if movie_data != None and len(movie_data) > 0:
                print("json movie data: ", movie_data)
                avg_rating = movie_data.get("avg_rating")
                total_reviews = movie_data.get("total_review") 
                # avg_rating = movie_data["avg_rating"]
                # total_reviews = movie_data["total_review"] 


                new_avg_rating = ((avg_rating * total_reviews) + rating)/(total_reviews + 1)
                new_total_reviews = total_reviews + 1

                is_movie_data_updated = updateMovieData(id, new_total_reviews, new_avg_rating)

                print("is movie data updated ", is_movie_data_updated, "\n")

 
        return render_template('thankyou.html')
    
    movie_name = request.args.get("name")
    return render_template('feedback.html', data=movie_name)

# Thank you page route
@app.route('/thank-you',methods=['GET','POST'])
def thank_you():
    # Display the thank you message along with the provided feedback
    return render_template('thankyou.html')

if __name__ == '__main__':
    app.run(debug=True)