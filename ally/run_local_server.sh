#!/bin/bash
# hypercorn main:app --host 0.0.0.0 --port 5050 --reload
hypercorn main:app --bind 0.0.0.0:5050 --reload