unilist = []
list = []
with open("./id.txt" , "r") as file :
    for line in file :
        id = line.strip()
        list.append(id)
    unilist = set(list)
with open ("./id.txt" , "w") as file :
    for i in unilist :
        file.write(i + "\n") 