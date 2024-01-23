from flask import Flask, request, render_template, session, redirect, send_file
import random, string, sqlite3, datetime, os, time

app = Flask(__name__)
app.secret_key = "aosuchpao9s8cghpai9su7gc8pi&G*iCGP*AI&SGC*yfgv"
app.permanent_session_lifetime = datetime.timedelta(days=7)
app.debug = True


sqlConnecter = sqlite3.connect("data.db", check_same_thread=False)
sqlConnecter.execute("CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY, username VARCHAR2(200), password VARCHAR2(200), type INT, date TIMESTAMP, phone VARCHAR2(200), email VARCHAR2(200), address VARCHAR2(200));")
sqlConnecter.execute("CREATE TABLE IF NOT EXISTS tool (id INTEGER PRIMARY KEY, name VARCHAR2(500), count INTEGER, date TIMESTAMP);")
sqlConnecter.execute("CREATE TABLE IF NOT EXISTS reserve (id INTEGER PRIMARY KEY, teacher VARCHAR2(200), class VARCHAR2(200), year VARCHAR2(200), term VARCHAR2(200), subject_name VARCHAR2(200), subject_title VARCHAR2(200), lab_name VARCHAR2(200), tools VARCHAR2(200), status VARCHAR2(200), reserve_date VARCHAR2(200), date TIMESTAMP);")
sqlConnecter.execute("CREATE TABLE IF NOT EXISTS worktime (id INTEGER PRIMARY KEY, wfrom timestamp, wto timestamp, status INTEGER);")
sqlConnecter.execute("CREATE TABLE IF NOT EXISTS session (name VARCHAR2(500), username VARCHAR2(200), ip VARCHAR2(200));")
sqlConnecter.commit()

def cprint(msg):
    os.system("cls" if os.name=="nt" else "clear")
    print("-------------------------------------------------------------")
    print(msg)
    print("-------------------------------------------------------------")

def getToday():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def dateToTimestamp(date: str):
    return time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d %H:%M").timetuple())

def timestampToDate(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")

def createSession():
    allCharacters = string.ascii_letters + "!#$%&()*+,-./<=>?@[]^_{|}~"  + string.digits
    randSession = "".join(random.choice(allCharacters) for _blabla in range(random.randint(60, 65)))
    session["sessionID"] = randSession
    sqlConnecter.execute("INSERT INTO session(name, username, ip) VALUES (?, ?, ?)", (randSession, '', request.access_route[-1],))
    sqlConnecter.commit()
    
def addUserToSession(username):
    sessionID = session["sessionID"]
    sqlConnecter.execute("UPDATE session SET username=? WHERE name=?;", (username, sessionID,))
    sqlConnecter.commit()

def loggedin():
    try:
        sessionID = session["sessionID"]
        username = sqlConnecter.execute("SELECT username FROM session WHERE name=?", (sessionID,)).fetchall()[0][0]
        if username:
            return True
        else:
            return False
    except:
        return False

def logoutSession():
    sessionID = session["sessionID"]
    sqlConnecter.execute("DELETE FROM session WHERE name=?;", (sessionID,))
    sqlConnecter.commit()
    try:
        session.clear()
    except:
        pass

def getUsername():
    sessionName = session["sessionID"]
    return sqlConnecter.execute("SELECT username FROM session WHERE name=?", (sessionName,)).fetchall()[0][0]

def getAccountType():
    return sqlConnecter.execute("SELECT type FROM user WHERE username=?", (getUsername(),)).fetchall()[0][0]

def getUser():
    user = {}
    userData = sqlConnecter.execute("SELECT * FROM user WHERE username=?", (getUsername(),)).fetchone()
    user["username"] = userData[1]
    user["type"] = userData[3]
    user["date"] = userData[4]
    user["phone"] = userData[5]
    user["email"] = userData[6]
    user["address"] = userData[7]
    return user

def getUsers():
    users = {}
    usersData = sqlConnecter.execute("SELECT * FROM user").fetchall()
    for user in usersData:
        users[user[0]] = {}
        users[user[0]]["username"] = user[1]
        users[user[0]]["type"] = user[3]
        users[user[0]]["date"] = timestampToDate(user[4])
    return users

def getTools():
    tools = {}
    toolsData = sqlConnecter.execute("SELECT * FROM tool").fetchall()
    for tool in toolsData:
        tools[tool[0]] = {}
        tools[tool[0]]["name"] = tool[1]
        tools[tool[0]]["count"] = tool[2]
        tools[tool[0]]["date"] = timestampToDate(tool[3])
    return tools

def getReserves():
    reserves = {}
    if getAccountType() == 1:
        reservesData = sqlConnecter.execute("SELECT * FROM reserve WHERE teacher=?", (getUsername(),)).fetchall()
    else:
        reservesData = sqlConnecter.execute("SELECT * FROM reserve").fetchall()

    for reserve in reservesData:
        reserves[reserve[0]] = {}
        reserves[reserve[0]]["teacher"] = reserve[1]
        reserves[reserve[0]]["class"] = reserve[2]
        reserves[reserve[0]]["year"] = reserve[3]
        reserves[reserve[0]]["term"] = reserve[4]
        reserves[reserve[0]]["subject_name"] = reserve[5]
        reserves[reserve[0]]["subject_title"] = reserve[6]
        reserves[reserve[0]]["lab_name"] = reserve[7]
        reserves[reserve[0]]["reserve_date"] = reserve[8]
        reserves[reserve[0]]["date"] = reserve[9]
        reserves[reserve[0]]["tools"] = reserve[10][0:-1].split("|")
        reserves[reserve[0]]["status"] = reserve[11]
    return reserves

def getWorkingTime():
    wt = {}
    wtData = sqlConnecter.execute("SELECT * FROM worktime").fetchall()
    for wti in wtData:
        wt[wti[0]] = {}
        wt[wti[0]]["wfrom"] = timestampToDate(wti[1])
        wt[wti[0]]["wto"] = timestampToDate(wti[2])
        wt[wti[0]]["status"] = wti[3]
    return wt

@app.route("/")
def index():
    if loggedin(): return redirect("/dashboard")
    else: return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login_page():
    session.permanent = True
    if "sessionID" not in session: createSession() 
    if loggedin(): return redirect("/dashboard")
    if request.method == "GET": return render_template("login.html")
    username = request.form["username"]
    password = request.form["password"]
    if not username or not password: return "error|Enter login credentials"
    try:
        passwordData = sqlConnecter.execute("SELECT password FROM user WHERE username=?", (username,)).fetchall()[0][0]
        if password != passwordData:
            return "error|Invalid login data"
        addUserToSession(username)
        return f"success|Welcome {username}, Logging you in ...."
    except:
        return "error|Invalid login data"

@app.route("/dashboard", methods=["POST", "GET"])
def dashboard_page():
    session.permanent = True
    if not loggedin(): return redirect("/")
    return render_template("dashboard.html", user=getUser(), reserves=getReserves(), tools=getTools(), wt=getWorkingTime(), users=getUsers())

@app.route("/add-reserve", methods=["POST", "GET"])
def addReserve():
    if not loggedin(): return redirect("/")
    if request.method == "GET": return redirect("/")
    if not request.form["subjectName"] or not request.form["subjectTitle"] or not request.form["labName"] or not request.form["class"] or not request.form["term"] or not request.form["date"] or not request.form["tools"] : return "error|Please insert all fields"

    try:
        wfrom = int(dateToTimestamp(request.form["date"].split(" / ")[0]))
        sqlConnecter.execute("UPDATE worktime SET status=? WHERE wfrom=?;", (0, wfrom,))
        sqlConnecter.commit()
        sqlConnecter.execute("INSERT INTO reserve (teacher, class, year, term, subject_name, subject_title, lab_name, reserve_date, date, tools, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (getUsername(), request.form["class"], datetime.datetime.now().year, request.form["term"], request.form["subjectName"], request.form["subjectTitle"], request.form["labName"], request.form["date"], dateToTimestamp(getToday()), request.form["tools"], "Waiting",))
        sqlConnecter.commit()
    except ValueError:
        return "error|Please select the reserve date"
    return "success|Reserve has been created"

@app.route("/admin/<action>", methods=["POST", "GET"])
def admin(action):
    if not loggedin(): return redirect("/")
    if request.method == "GET": return redirect("/")
    if action == "addUser":
        if not request.form["username"] or not request.form["password"] or not request.form["email"] or not request.form["phone"] or not request.form["address"] or not request.form["type"]: return "error|Enter all fields"
        sqlConnecter.execute("INSERT INTO user (username, password, type, date, email, phone, address) VALUES (?, ?, ?, ?, ?, ?, ?);", (request.form["username"], request.form["password"], request.form["type"], dateToTimestamp(getToday()), request.form["email"], request.form["phone"], request.form["address"],))
        return "success|User has been created"
    elif action == "addTool":
        if not request.form["name"] or not request.form["count"]: return "error|Enter all fields"
        try: int(request.form["count"]) 
        except : return "error|Tool Count must be a number"
        sqlConnecter.execute("INSERT INTO tool (name, count, date) VALUES (?, ?, ?);", (request.form["name"], request.form["count"], dateToTimestamp(getToday()),))
        return "success|Tool has been created"
    elif action == "addWT":
        if not request.form["start"] or not request.form["end"]: return "error|Enter all fields"
        sqlConnecter.execute("INSERT INTO worktime (wfrom, wto, status) VALUES (?, ?, ?);", (dateToTimestamp(request.form["start"]), dateToTimestamp(request.form["end"]), 1,))
        return "success|Working Time has been created"

@app.route("/edit/<action>", methods=["POST", "GET"])
def editData(action):
    if not loggedin(): return redirect("/")
    if request.method == "GET": return redirect("/")
    if action == "labStatus":
        try:
            wfrom = int(dateToTimestamp(request.form["editLabDate"].split(" / ")[0]))
            sqlConnecter.execute("UPDATE worktime SET status=? WHERE wfrom=?;", (1, wfrom,))
            sqlConnecter.commit()
        except:
            return "error|Please select the lab reserve date"
        return "success|Lab status has been changed"
    elif action == "reserve":
        if getAccountType() == 1:
            try:
                wfrom = int(dateToTimestamp(request.form["editReserveDate"].split(" / ")[0]))
                sqlConnecter.execute("UPDATE worktime SET status=? WHERE wfrom=?;", (0, wfrom,))
                sqlConnecter.commit()
                sqlConnecter.execute("UPDATE reserve SET reserve_date=? WHERE id=?;", (request.form["editReserveDate"], request.form["editReserveID"],))
                sqlConnecter.commit()
            except:
                return "error|Please select the lab reserve date"
            return "success|Reserve status has been edited"
        elif getAccountType() == 2:
            if not request.form["editReserveStatus"]: return "error|Enter reserve status"
            sqlConnecter.execute("UPDATE reserve SET status=? WHERE id=?;", (request.form["editReserveStatus"], request.form["editReserveID"],))
            sqlConnecter.commit()
            return "success|Reserve status has been edited"
        
@app.route("/delete/<action>/<id>", methods=["POST", "GET"])
def deleteData(action, id):
    if not loggedin(): return redirect("/")
    if action == "user":
        if getAccountType() != 0: return redirect("/")
        sqlConnecter.execute("DELETE FROM user WHERE id=?", (id,))
        sqlConnecter.commit()
    elif action == "tool":
        if getAccountType() != 0: return redirect("/")
        sqlConnecter.execute("DELETE FROM tool WHERE id=?", (id,))
        sqlConnecter.commit()
    elif action == "wt":
        if getAccountType() != 0: return redirect("/")
        sqlConnecter.execute("DELETE FROM worktime WHERE id=?", (id,))
        sqlConnecter.commit()
    return redirect("/")

@app.route("/excel-link")
def excelLink():
    return send_file(".//static/Excal.xls")

@app.route("/logout")
def logout():
    logoutSession()
    return redirect("/")


app.run(host="0.0.0.0", port=4546)