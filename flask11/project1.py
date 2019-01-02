from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db', connect_args={'check_same_thread':False},echo=True)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/restaurants')
def restaurants():
	restaurant = session.query(Restaurant)
	return render_template('restaurant.html',restaurant=restaurant)
@app.route('/restaurants/new', methods=['GET','POST'])
def newRestaurant():
	if request.method == 'POST':
		name = request.form['name']
		newItem = Restaurant(name=name)
		session.add(newItem)
		session.commit()
		flash("new restaurant added")
		return redirect(url_for('restaurants'))
	else:
		return render_template('newrestaurant.html')
	


@app.route('/restaurants/<int:restaurant_id>/menu')
def restaurantMenu(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
	return render_template('menu.html', restaurant=restaurant, items = items, restaurant_id = restaurant_id)




@app.route('/restaurants/<int:restaurant_id>/new', methods=['GET','POST'])
def newMenuItem(restaurant_id):
	
	if request.method == 'POST':
		name = request.form['name']
		description=request.form['description']
		price=request.form['price']
		course=request.form['course']

		newItem = MenuItem(name=name,description=description,price=price,course=course,restaurant_id=restaurant_id)
		session.add(newItem)
		session.commit()

		flash("new menu "+name+" added")
		return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
	else:
		return render_template('newmenuitem.html', restaurant_id = restaurant_id)




@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit', methods = ['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
	restaurant=session.query(Restaurant).filter_by(id=restaurant_id).one()
	editedItem = session.query(MenuItem).filter_by(id = menu_id).one()
	if request.method == 'POST':
		if request.form['name']:
			editedItem.name = request.form['name']
		if request.form['description']:
			editedItem.description = request.form['description']
		if request.form['price']:
			editedItem.price = request.form['price']
		if request.form['course']:
			editedItem.course = request.form['course']
		session.add(editedItem)
		session.commit()
		flash("menu item "+editedItem.name+" updated succesfully")
		return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
	else:
		return render_template('editmenuitem.html', restaurant= restaurant, menu =editedItem)
	

#DELETE MENU ITEM SOLUTION
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete', methods = ['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
	restaurant=session.query(Restaurant).filter_by(id= restaurant_id).one()
	itemToDelete = session.query(MenuItem).filter_by(id = menu_id).one() 
	if request.method == 'POST':
		session.delete(itemToDelete)
		session.commit()
		flash("manu item "+itemToDelete.name+" deleted")
		return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
	else:
		return render_template('deletemenuitem.html',restaurant=restaurant, item = itemToDelete)


@app.route('/restaurants/<int:restaurant_id>/menu/json')
def restaurantMenuJson(restaurant_id):
	restaurant=session.query(Restaurant).filter_by(id=restaurant_id).one()
	items=session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
	return jsonify(MenuItem=[i.serialize for i in items])




@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def MenuJson(restaurant_id,menu_id):
	item = session.query(MenuItem).filter_by(id=menu_id).one()
	return jsonify(MenuItem=item.serialize)



if __name__ == '__main__':
	app.secret_key='super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)