import subprocess
import os
import re
import glob

#directories / files for app

appDir="/home/aether/AUR/update-apps/"
folders=os.listdir("/home/aether/AUR/update-apps")
gitList = "/home/aether/AUR/gitUrls"

#TODO Run routines to enumerate apps and see which ones need updating and create files if they dont exists maybe create a folder for the user to store AUR apps


def updateGitOrigin():

    #this function switches into each directory, cleans it, updates git from origin master, compiles source, then installs

    #this is the loop that loops into each directory it then runs processes in each app directory, git clean, git pull, makepkg, and pacman -U to install
    #it also locates all .tar.*z files in each directory and uses the one with the latest ctime to install
    for folder in folders:

        #changes into app directory
        os.chdir(appDir + folder)
        print("Current Working Directory", os.getcwd())

        print("Running update routine for",folder)
        print(subprocess.run(['git','pull','origin','master'],capture_output=True))

def updateApps():
       

    #clears directory
    print("Running cleaing routines for",folder)
    subprocess.run(['git','clean','-f'])

    #compiles source with makepkg
    print("Compiling source...")
    print(subprocess.run(['makepkg','-si'],capture_output=True))

    # #enumerates files, finds latest source compiled, installs compiled source
    # files = glob.glob("./*.tar.*z")
    # latest_file = max(files, key=os.path.getctime)
    # print("Installing compiled source...")
    # subprocess.run(['sudo','pacman','-U',latest_file],capture_output=True)
        
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
                g = open(gitList,'a')
                g.write(matchUrl + '\n')
                g.close()
            f.close()
        else:
            print(".git directory does not exists and is probably not a git repository")

def printTitle():
    title = "Welcome to Update Apps AUR Helper"
    print('-' * len(title),"\n",title,"\n",'-' * len(title))

def resetHead():
    for folder in folders:
        os.chdir(appDir + folder)
        print(subprocess.run(["git","fetch","origin"],capture_output=True))
        print(subprocess.run(["git","reset","--hard","origin/master"],capture_output=True))

def printMenu():
    menu = ["1. Update Git Origin", "2. Get list of AUR git repository urls", "3.  Update Apps", "4. Reset Git Head"]
    print(menu[0],"\n",menu[1])

def getUserChoice():
    return input("What option would you like to pick?")

def runOption(choice):
    if choice == "1":
        updateGitOrigin()
    elif choice == "2":
        getGitUrls()
    elif choice == "3":
        updateApps()
    elif choice == "4":
        resetHead()

def main():
    printTitle()
    printMenu()
    choice = getUserChoice()
    runOption(choice)

main()