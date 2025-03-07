from flask import Flask, request, render_template
import re
import math

app = Flask("_name_")

@app.route("/")
def loadPage():
    return render_template('index.html', query="")

@app.route("/", methods=['POST'])
def cosineSimilarity():
    try:
        universalSetOfUniqueWords = []
        matchPercentage = 0
        
        inputQuery = request.form['query']
        lowercaseQuery = inputQuery.lower()
        queryWordList = re.sub(r"[^\w]", " ", lowercaseQuery).split()
        queryWordList = list(map(str, queryWordList))
        
        for word in queryWordList:
            if word not in universalSetOfUniqueWords:
                universalSetOfUniqueWords.append(word)
        
        fd = open("database1.txt", "r")
        database1 = fd.read().lower()
        fd.close()
        
        databaseWordList = re.sub(r"[^\w]", " ", database1).split()
        databaseWordList = list(map(str, databaseWordList))
        
        for word in databaseWordList:
            if word not in universalSetOfUniqueWords:
                universalSetOfUniqueWords.append(word)
        
        queryTF = []
        databaseTF = []
        
        for word in universalSetOfUniqueWords:
            queryTF.append(queryWordList.count(word))
            databaseTF.append(databaseWordList.count(word))
        
        dotProduct = sum(q * d for q, d in zip(queryTF, databaseTF))
        queryVectorMagnitude = math.sqrt(sum(q ** 2 for q in queryTF))
        databaseVectorMagnitude = math.sqrt(sum(d ** 2 for d in databaseTF))
        
        if queryVectorMagnitude * databaseVectorMagnitude != 0:
            matchPercentage = (dotProduct / (queryVectorMagnitude * databaseVectorMagnitude)) * 100
        
        output = f"Input query text matches {matchPercentage:.2f}% with database."
        return render_template('index.html', query=inputQuery, output=output)
    
    except Exception as e:
        output = "Please Enter Valid Data"
        return render_template('index.html', query=inputQuery, output=output)

if _name_ == "_main_":
    app.run(debug=True)