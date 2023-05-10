from flask import render_template, flash, redirect \
    , url_for, request, send_from_directory 
from app import app 

@app.route('/', methods=['GET', 'POST']) 
def index():
    pass 

