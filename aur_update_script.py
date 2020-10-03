import subprocess
import os
import re
import glob
import pickle
import sys
import readchar

#directories / files for app
appDir=os.environ['HOME'] + '/AUR/update-apps/'  #where are your apps located
updateAppsNeeds = []
gitList = os.environ['HOME'] + "/AUR/gitUrls"
appUpdates = os.environ['HOME'] + "/AUR/appUpdates"
menu = ["1. Update Git Origin", "2. Update Apps ", "3. View Report","4. Clean App Directories"] 

def enumerateAppDirs():
    filteredDirs = []
    unfilteredDirs = os.listdir(rf"{appDir}")
    # print(unfilteredDirs)
    for i in unfilteredDirs:
        # print(filteredDirs)
        if os.path.isdir(os.path.join(appDir,i)):
            filteredDirs.append(i)
    return filteredDirs

folders=enumerateAppDirs() #list of folders in app directory

def printTitle():
    title = "Welcome to Update Apps AUR Helper"
    print('-' * len(title),"\n",title,"\n",'-' * len(title))

def printMenu(menu):
    #"2. Get list of AUR git repository urls",  "3. Reset Git Head"
    for item in menu:
        print(item)

def loadApps():
    if os.path.exists(appDir + "updateAppNeeds.dat"):
        os.chdir(appDir)
        updateAppNeeds = pickle.load(open("updateAppNeeds.dat","rb"))
        return updateAppNeeds
    else:
            print("There are no apps in the saved array that need to be loaded.")       

def getUserChoice(menu):

    while True:
        choice = input("What option would you like to pick?  ")
        if choice.isdigit():
            check = int(choice)
            match = re.search(r"[1-4]{1}",choice)
            if not match or check < 1 and check > len(menu)+1:
                print("Please enter valid option.")
                continue
            elif match or check < 1 and check > len(menu)+1:
                break
            else:
                print("Error no match found")
                main()
        else:
            print("Please enter a valid option")
            continue

    return choice

def runOption(choice, updateAppNeeds, folders):
    if choice == "1":
       return updateGitOrigin(updateAppNeeds)
    elif choice == "2":
        updateApps(updateAppNeeds)
    elif choice == "3":
        printReport(updateAppNeeds)
    elif choice == "4":
        cleanApps(folders)

def updateGitOrigin(report):

    #this function switches into each directory, cleans it, updates git from origin master, compiles source, then installs
    #this is the loop that loops into each directory it then runs processes in each app directory, git clean, git pull, and makepk
    if report:
        report = report
    else:
        report = []

    for folder in folders:

        #changes into app directory
        os.chdir(appDir + folder)
        print("Current Working Directory", os.getcwd())

        print("Running update routine for",folder)
        output = subprocess.run(['git','pull','origin','master'],capture_output=True)
        match = re.search('Already up to date.', str(output))

        if len(report) > 0:
            if not match and folder not in report:
                report.append(folder)
        elif not report:
            if not match:
                report.append(folder)

    os.chdir(appDir)
    pickle.dump(report,open("updateAppNeeds.dat", "wb"))
   

    return report

def printReport(report):
    print("You have the following apps that need to be updated:  ")
    print(report)

def runSubProcess(commands):
    child = subprocess.Popen(commands,stdin=subprocess.PIPE,stdout=subprocess.PIPE,shell=True,executable="/bin/bash")
    proc_stdout = child.communicate()[0].strip()
    print(proc_stdout)
    returnCode = child.returncode
    return returnCode

# def runSubProcessClean():
 
#     subprocess.run(["git","fetch","origin"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,shell=True,executable="/bin/bash")
#     # subprocess.run(["git","fetch","origin"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,shell=)
#     # subprocess.run(["git","reset","--hard","origin/master"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
#     # subprocess.run(['git','clean','-f'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)

# def runSubProcessUpdate(options):
#     child = subprocess.Popen(options.split(),stdin=subprocess.PIPE,stdout=subprocess.PIPE,executable="/bin/bash")
#     returnCode = child.returncode
#     return returnCode

def cleanApps(appFolders):

    try:
        appFolders.index("All Apps")
    except:
        appFolders.append("All Apps")
    

    for index,app in enumerate(appFolders):
        print(str(index+1) + '.',app)
        lastIndexOfAppFolders = index

    while True:
        choice = input("Which app would you like to clean?")
        if choice.isdigit():
            if int(choice) < 1 or int(choice) > lastIndexOfAppFolders + 1:
                print("Please enter a valid option.")
                
            else:
                break
        else:
            print("Please enter a valid option.")

    while True:
        print("Are you sure you want to continue? This will delete all untracked files within the local git repo and reset the head. (y or n)")
        continueClean = input()
        if continueClean != 'y' and continueClean != 'n':
            print("Please enter y or n")
            continue
        elif continueClean == 'y':
            if choice == str(len(appFolders)):
                appFolders.pop()
                for app in appFolders:
                    os.chdir(appDir + app)
                    print("Running cleaing routines for",app)
                    os.system("git fetch origin; git reset --hard origin/master; git clean -f")
                break
            else:
                actualIndex = int(choice) - 1
                appName = appFolders[actualIndex]
                os.chdir(appDir + appName)
                print("Running cleaing routines for",appName)
                os.system("git fetch origin; git reset --hard origin/master; git clean -f")
                break
        elif continueClean == 'n':
            break

def getLatestSource(app):
    listOfFiles = glob.glob(appDir + app + '/*.tar.*')
    latestSource = max(listOfFiles, key=os.path.getctime)
    return latestSource

def updateApps(updateAppNeeds):
    print("Runnings updateApps")
    print(updateAppNeeds)
    updateAppNeedsUpdated = updateAppNeeds
    for app in updateAppNeeds:
        
        os.chdir(appDir + app)
        #compiles source with makepkg
        print("Currentworking diretory: ", os.getcwd())
        print("Compiling source...")
        makepkgReturnCode = None
        makepkgReturnCode = os.WEXITSTATUS(os.system("makepkg -s --skippgpcheck"))
        while makepkgReturnCode is None:
            pass
        #find the latest tar.xz file
        latestSource = getLatestSource(app)
        #install the compiled source
        pacmanReturnCode = None
        pacmanReturnCode = os.WEXITSTATUS(os.system(f"sudo pacman -U {latestSource}"))
        while pacmanReturnCode is None:
            pass
        if pacmanReturnCode == 0:
            updateAppNeedsUpdated.remove(app)
            pickle.dump(updateAppNeedsUpdated,open(appDir + "updateAppNeeds.dat", "wb"))
        else:
            print("There was an error while installing the package")
    

        
        
            
def getGitUrls():

    #this functions compiles a list of aur apps in the update folders by getting the https* url from ./.git/config
    for folder in folders:
        #change into the directory and print name of directory
        os.chdir(appDir + folder)
        print("Current directory: ",appDir + folder)
    
        #if there is a ./.git then proceeed otherwise complain
        if(os.path.exists(appDir + folder + "/" +".git")):
            os.chdir(".git")
            f = open("config",'rt')
            match = re.search(r'http[\'"]?([^\'" >]+).git',f.read())
            if match:
                matchUrl = match.group(0)
                print("adding....",matchUrl)
                g = open(gitList,'w')
                g.write(matchUrl + '\n')
                g.close()
            f.close()
        else:
            print(".git directory does not exists and is probably not a git repository")
    return False

def restart():
    restart = input("Would you like to do something else? (y or n) ")
    while True:
        if restart != 'y' and restart != 'n':
            print("Please enter valid input.")
            restart = input("Would you like to do something else? (y or n) ")
            continue
        elif restart == 'y':
            main()
            break
        elif restart == 'n':
            break

def main():
    printTitle()
    printMenu(menu)
    updateAppNeeds = loadApps()
    choice = getUserChoice(menu)
    if choice == "1":
        updateAppNeeds = runOption(choice, updateAppNeeds,folders)
    else:
        runOption(choice, updateAppNeeds, folders)

    restart()

    # if updateAppNeeds:
    #     print("The follow apps needs to be updated: " + '\n', updateAppNeeds)
    #     while True:
    #         print("Please enter y for yes or n for no...")
    #         update = input("Would you like to update them now? y or n ")
    #         if update == "y":
    #             updateApps(updateAppNeeds)
    #             break
    #         elif update == "n": 
    #             print("Exiting...")
    #             break
    #         else:
    #             continue

def test():
    updateAppNeeds = loadApps()
    updateAppNeeds.remove("teamviewer")
    updateAppNeeds.remove("slack-desktop")
    pickle.dump(updateAppNeeds,open("updateAppNeeds.dat", "wb"))
    print(updateAppNeeds)
    # updateApps(updateAppNeeds)
main()
# test()