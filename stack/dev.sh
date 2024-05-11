#!/bin/sh

echo Starting server...
uvicorn app.main:app --reload --port 9000
