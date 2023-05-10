from flask import Flask 
from config import Config 
import logging 
from logging.handlers import SMTPHandler, RotatingFileHandler 
import os 
from flask_bootstrap import Bootstrap

app = Flask