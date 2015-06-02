from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
             if self.path.endswith("/delete"):
                restaurantId = self.path.split('/')[-2]
                restaurantToEdit = session.query(Restaurant).filter_by(id = restaurantId).one()
                if restaurantId:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h1>Update Restaurant name</h1>"
                    output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'><h2>Are you sure to delete it?</h2><input type="submit" value="Delete"> </form>''' % restaurantId
                    output += "</body></html>"
                    output += "</br>"
                    self.wfile.write(output)
                    print output
                return


             if self.path.endswith("/edit"):
                restaurantId = self.path.split('/')[-2]
                restaurantToEdit = session.query(Restaurant).filter_by(id = restaurantId).one()
                if restaurantId:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h1>Update Restaurant name</h1>"
                    output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'><h2>Please input a new name for restaurant</h2><input name="newRestaurantName" type="text" placeholder = '%s'  ><input type="submit" value="update"> </form>''' % (restaurantId, restaurantToEdit.name)
                    output += "</body></html>"
                    output += "</br>"
                    self.wfile.write(output)
                    print output
                return

             if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Create Restaurants</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'><h2>Please input a name for new restaurant</h2><input name="newRestaurantName" type="text" placeholder="new restaurant name"  ><input type="submit" value="Create"> </form>'''
                output += "</body></html>"
                output += "</br>"
                self.wfile.write(output)
                print output
                return

             if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                restaurants = session.query(Restaurant).all()
                print "ok to get restaurants"
                output = ""
                output += "<html><body>"
                output += "<h1>Restaurants</h1>"
                output += "</br>"
                output += "<a href = '/restaurants/new'>Make a New Restaurant Here</a>"
                output += "</br>"
                output += "</br>"
                for restaurant in restaurants:
                    output += restaurant.name
                    output += "</br>"
                    output += "<a href='/restaurants/%s/edit'>Edit</a>" % restaurant.id
                    output += "</br>"
                    output += "<a href='/restaurants/%s/delete'>Delete</a>" % restaurant.id
                    output += "</br>""</br>"

                output += "</body></html>"
                self.wfile.write(output)
                print output
                return


        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype ==  'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messageContent = fields.get('newRestaurantName')

                    newRestaurant = Restaurant(name = messageContent[0])
                    session.add(newRestaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype ==  'multipart/form-data':
                    restaurantId = self.path.split('/')[-2]
                    restaurant = session.query(Restaurant).filter_by(id = restaurantId).one()
                    if restaurant:
                        session.delete(restaurant)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype ==  'multipart/form-data':
                    restaurantId = self.path.split('/')[-2]
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messageContent = fields.get('newRestaurantName')
                    restaurant = session.query(Restaurant).filter_by(id = restaurantId).one()
                    if restaurant:
                        restaurant.name = messageContent[0]
                        print 'get restaurant to edit %s' % restaurant.name
                        session.add(restaurant)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()

        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()
