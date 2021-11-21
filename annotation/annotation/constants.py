def get_secret_key():
    SECRET_KEY = 'e2^#^iv5ukf9td$f*5&qmb8a4sw+9q$ga$92)_=)&k(pzj#8ui'
    return SECRET_KEY

def connect_to_mongo():
    from mongoengine import connect
    c = connect(
        db='coordinates',        
        host='mongodb://localhost:27017/?readPreference=primary&ssl=false'
    )
    print(c)