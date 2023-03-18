def restartClient():
    lines = [] #content of files
    with open("file0.txt", 'r') as file:
        lines = file.readlines()
    logstr = lines[-1] 
    votedForColon = lines[-2].find(':')
    votedFor = int(lines[-2][votedForColon+1:])

    currentTermColon = lines[-3].find(':')
    currentTerm = int(lines[-3][currentTermColon+1:])

    logColon = lines[-1].find(':')
    logString = lines[-1][logColon+1:len(lines[-1])-1]

    log = [[eval(item) if item.isdigit() else item.strip("\"") for item in inner.split(",")] for inner in logString.split(";")]

    print(log)
    print(votedFor)
    print(currentTerm)

restartClient()