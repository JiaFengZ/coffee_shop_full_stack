import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
  data = Drink.query.order_by(Drink.id).all()
  drinks = [item.short() for item in data]
  total = len(drinks)

  if total == 0:
    abort(404)

  return jsonify({
    'success': True,
    'drinks': drinks
  })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
def get_drinks_detail():
  data = Drink.query.order_by(Drink.id).all()
  drinks = [item.long() for item in data]
  total = len(drinks)

  if total == 0:
    abort(404)

  return jsonify({
    'success': True,
    'drinks': drinks
  })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
def create_drink():
  body = request.get_json()

  new_title = body.get('title', None)
  new_recipe = body.get('recipe', None)

  try:
    drink = Drink(
      title=new_title,
      recipe=new_recipe
    )
    drink.insert()

    drink = Drink.query.filter(Drink.id == drink.id).one_or_none()

    return jsonify({
      'success': True,
      'drinks': [drink.long]
    })

  except Exception:
    abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
def edit_drink(id):
  try:
    drink = Drink.query.get(id)
    body = request.get_json()
    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)
    if new_title != None:
      drink.title = new_title
    if new_recipe != None:
      drink.recipe = new_recipe
    drink.update()
  except Exception:
    abort(422)
  return jsonify({
    'success': True,
    'drinks': [drink.long]
  })

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
def delete_drink(id):
  try:
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if drink is None:
      abort(404)

    drink.delete()

    return jsonify({
      'success': True,
      'delete': drink.id
    })

  except Exception:
    abort(422)


## Error Handling
'''
422
'''
@app.errorhandler(422)
def unprocessable(error):
  return jsonify({
    "success": False, 
    "error": 422,
    "message": "unprocessable"
    }), 422

'''
404
'''
@app.errorhandler(404)
def not_found(error):
  return jsonify({
    "success": False, 
    "error": 404,
    "message": "resource not found"
    }), 404

'''
400
'''
@app.errorhandler(400)
def bad_request(error):
  return jsonify({
    "success": False, 
    "error": 400,
    "message": "bad request"
    }), 400

'''
405
'''
@app.errorhandler(405)
def not_allowed(error):
  return jsonify({
    "success": False, 
    "error": 405,
    "message": "method not allowed"
    }), 405


'''
AuthError
'''
@app.errorhandler(401)
def user_unauthorized(error):
  return jsonify({
    "success": False, 
    "error": 401,
    "message": error.description
    }), 401

@app.errorhandler(403)
def resource_unauthorized(error):
  return jsonify({
    "success": False, 
    "error": 403,
    "message": error.description
    }), 403
