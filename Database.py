import sqlite3
def createdb(name):
        con= sqlite3.connect(name)
        cursor=con.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Products (
                            ProductID INTEGER PRIMARY KEY,
                            Name TEXT NOT NULL,
                            Url TEXT NOT NULL,
                            TargetPrice FLOAT NOT NULL
                          )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS PriceHistory (
                            ProductID INTEGER,
                            Price FLOAT,
                            Day INTEGER,
                            FOREIGN KEY(ProductID) REFERENCES Products(ProductID)
                          )''')
        con.commit()
        con.close()

def addproduct(username,product_id, name, url, target_price):
    """Add a new product to the Products table."""
    con = sqlite3.connect(f"{username}.db")
    cursor = con.cursor()
    try:
        cursor.execute("INSERT INTO Products (ProductID, Name, Url, TargetPrice) VALUES (?, ?, ?, ?)",
                       (product_id, name, url, target_price))
        con.commit()
    except sqlite3.IntegrityError:
        raise
    finally:
        con.close()

def loadproductsdb(username):
    """Load all tracked products from the Products table."""
    con = sqlite3.connect(f"{username}.db")
    cursor = con.cursor()
    cursor.execute("SELECT ProductID, Name, Url, TargetPrice FROM Products")
    products = cursor.fetchall()
    con.close()
    return products

def deleteproduct(username, product_id):
    """Delete a product from the Products table and all associated price history by ID."""
    con = sqlite3.connect(f"{username}.db")
    cursor = con.cursor()
    cursor.execute("DELETE FROM PriceHistory WHERE ProductID = ?", (product_id,))
    cursor.execute("DELETE FROM Products WHERE ProductID = ?", (product_id,))

    con.commit()
    con.close()



def loadproductpricedb(username,product_id):
    con = sqlite3.connect(f"{username}.db")
    cursor = con.cursor()
    cursor.execute("SELECT Price,Day FROM PriceHistory WHERE ProductID = ?",(product_id,))
    history = cursor.fetchall()
    return history

def addpricehistorydb(username,product_id,price,day):
    con = sqlite3.connect(f"{username}.db")
    cursor = con.cursor()
    cursor.execute("INSERT INTO PriceHistory VALUES (?,?,?)",(product_id,price,day))
    con.commit()
    con.close()

def accesslasttrackeddaydb(username,product_id):
    con = sqlite3.connect(f"{username}.db")
    cursor = con.cursor()
    cursor.execute("SELECT * FROM PriceHistory WHERE ProductID = ? ORDER BY Day DESC LIMIT 1",(product_id,))
    record=cursor.fetchall()
    con.close()
    return record






