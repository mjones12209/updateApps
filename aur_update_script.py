import subprocess
import os
import re
import glob

#directories / files for app

#TODO Run routines to enumerate apps and see which ones need updating and create files if they dont exists maybe create a folder for the user to store AUR apps

appDir=os.environ['HOME'] + '/AUR/update-apps/'  #where are your apps located
folders=os.listdir(appDir) #list of folders in app directory
updateAppsNeeds = []
gitList = os.environ['HOME'] + "/AUR/gitUrls"
appUpdates = os.environ['HOME'] + "/AUR/appUpdates"




def updateGitOrigin():

    #this function switches into each directory, cleans it, updates git from origin master, compiles source, then installs
    #this is the loop that loops into each directory it then runs processes in each app directory, git clean, git pull, and makepkg

    # if os.path.exists(appUpdates): 
    #     f = open(appUpdates,"a")
    # else: 
    #     f = open(appUpdates,"x")

    for folder in folders:

        #changes into app directory
        os.chdir(appDir + folder)
        print("Current Working Directory", os.getcwd())

        print("Running update routine for",folder)
        output = subprocess.run(['git','pull','origin','master'],capture_output=True)
        match = re.search('Already up to date.', str(output))

        if not match:
            updateAppsNeeds.append(folder)

    ##TODO write updatable apps to a updateApps file and then be able to read them back in later to update them and also it need to be done right the first time each time
    #an origin update is completed 
   

    # f.write(updateAppsNeeds)
    # f.close()
   

    return updateAppsNeeds


def updateApps(report):

    #clears directory
    for app in report:
        os.chdir(appDir + app)
        print("Running cleaing routines for",app)
        subprocess.run(['git','clean','-f'])

        #compiles source with makepkg
        print("Compiling source...")
        print(subprocess.run(['makepkg','-si'],capture_output=True))

            
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

def printTitle():
    title = "Welcome to Update Apps AUR Helper"
    print('-' * len(title),"\n",title,"\n",'-' * len(title))

def resetHead():
    for folder in folders:
        os.chdir(appDir + folder)
        print(subprocess.run(["git","fetch","origin"],capture_output=True))
        print(subprocess.run(["git","reset","--hard","origin/master"],capture_output=True))
    return False

def printMenu():
    menu = [" 1. Update Git Origin", "2. Get list of AUR git repository urls",  "3. Reset Git Head"]
    print(menu[0],"\n",menu[1], "\n", menu[2])

def getUserChoice():
    return input("What option would you like to pick?")

def runOption(choice):
    if choice == "1":
       return updateGitOrigin()
    elif choice == "2":
        return getGitUrls()
    elif choice == "3":
        return resetHead()

def main():
    printTitle()
    printMenu()
    choice = getUserChoice()
    report = runOption(choice)

    if report:
        print("The follow apps needs to be updated: " + '\n', report)
        while True:
            print("Please enter y for yes or n for no...")
            update = input("Would you like to update them now? y or n ")
            if update == "y":
                updateApps(report)
                break
            elif update == "n": 
                print("Exiting...")
                break
            else:
                continue


main()