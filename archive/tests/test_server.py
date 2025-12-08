from app import create_app

app = create_app()

@app.route('/test-error')
def test_error():
    raise Exception("Test error")

if __name__ == '__main__':
    app.run(debug=False)
