import uvicorn


if __name__ == "__main__":
    # Run the main app which initializes DB and starts the consumer thread
    uvicorn.run("src.main:app", host="0.0.0.0", port=8010, reload=False)


